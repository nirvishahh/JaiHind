from flask import render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, date
from app import app, db
from models import User, Task
from utils import get_user_analytics, create_sample_data
import logging

# Create sample data on first run
with app.app_context():
    create_sample_data()

@app.route('/')
def index():
    """Home page - show tasks if logged in, otherwise redirect to login"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Get filter and sort parameters
    filter_type = request.args.get('filter', 'all')
    sort_by = request.args.get('sort', 'created_date')
    
    # Base query for user's tasks
    query = Task.query.filter_by(user_id=user_id)
    
    # Apply filters
    if filter_type == 'overdue':
        query = query.filter(Task.status == 'Pending', Task.due_date < date.today())
    elif filter_type == 'upcoming':
        query = query.filter(Task.status == 'Pending', Task.due_date >= date.today())
    elif filter_type == 'completed':
        query = query.filter(Task.status == 'Completed')
    elif filter_type == 'pending':
        query = query.filter(Task.status == 'Pending')
    
    # Apply sorting
    if sort_by == 'due_date':
        query = query.order_by(Task.due_date.asc())
    elif sort_by == 'priority':
        # Custom priority ordering: High, Medium, Low
        priority_order = ['High', 'Medium', 'Low']
        query = query.order_by(db.case(
            [(Task.priority == p, i) for i, p in enumerate(priority_order)]
        ))
    else:
        query = query.order_by(Task.created_date.desc())
    
    tasks = query.all()
    
    return render_template('index.html', user=user, tasks=tasks, 
                         current_filter=filter_type, current_sort=sort_by)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    """Add a new task"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']
        due_date_str = request.form['due_date']
        points = int(request.form.get('points', 5))
        
        # Parse due date
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format', 'error')
                return render_template('add_task.html')
        
        task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            points=points,
            user_id=session['user_id']
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_task.html')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Edit an existing task"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.priority = request.form['priority']
        task.points = int(request.form.get('points', 5))
        
        due_date_str = request.form['due_date']
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format', 'error')
                return render_template('edit_task.html', task=task)
        else:
            task.due_date = None
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit_task.html', task=task)

@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    """Toggle task completion status"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    
    if task.status == 'Pending':
        task.status = 'Completed'
        task.completed_date = datetime.utcnow()
        # Award points
        user.total_points += task.points
        flash(f'Task completed! You earned {task.points} points!', 'success')
    else:
        task.status = 'Pending'
        task.completed_date = None
        # Remove points
        user.total_points = max(0, user.total_points - task.points)
        flash('Task marked as pending', 'info')
    
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    """Delete a task"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    # If task was completed, remove points from user
    if task.status == 'Completed':
        user = User.query.get(session['user_id'])
        user.total_points = max(0, user.total_points - task.points)
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Analytics dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    analytics = get_user_analytics(user_id)
    
    return render_template('dashboard.html', user=user, analytics=analytics)

@app.route('/profile')
def profile():
    """User profile page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500
