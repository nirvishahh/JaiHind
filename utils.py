from datetime import datetime, timedelta
from models import Task
from sqlalchemy import func

def get_user_analytics(user_id):
    """Get analytics data for a user"""
    # Total tasks
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    
    # Completed vs Pending tasks
    completed_tasks = Task.query.filter_by(user_id=user_id, status='Completed').count()
    pending_tasks = total_tasks - completed_tasks
    
    # Tasks by priority
    high_priority = Task.query.filter_by(user_id=user_id, priority='High').count()
    medium_priority = Task.query.filter_by(user_id=user_id, priority='Medium').count()
    low_priority = Task.query.filter_by(user_id=user_id, priority='Low').count()
    
    # Overdue tasks
    overdue_tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.status == 'Pending',
        Task.due_date < datetime.now().date()
    ).count()
    
    # Tasks completed on time vs late
    on_time_tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.status == 'Completed',
        Task.completed_date <= func.date(Task.due_date)
    ).count()
    
    late_tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.status == 'Completed',
        Task.completed_date > func.date(Task.due_date)
    ).count()
    
    # Weekly productivity (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    weekly_completed = []
    for i in range(7):
        day = week_ago + timedelta(days=i)
        day_tasks = Task.query.filter(
            Task.user_id == user_id,
            Task.status == 'Completed',
            func.date(Task.completed_date) == day.date()
        ).count()
        weekly_completed.append(day_tasks)
    
    return {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'overdue_tasks': overdue_tasks,
        'on_time_tasks': on_time_tasks,
        'late_tasks': late_tasks,
        'weekly_completed': weekly_completed
    }

def create_sample_data():
    """Create sample users and tasks for demonstration"""
    from app import db
    from models import User, Task
    from datetime import date, timedelta
    
    try:
        # Check if sample data already exists
        if User.query.filter_by(username='demo_user').first():
            return
        
        # Create sample users
        user1 = User(username='demo_user', email='demo@example.com', total_points=35)
        user1.set_password('password123')
        
        user2 = User(username='john_doe', email='john@example.com', total_points=15)
        user2.set_password('password123')
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.flush()  # Get user IDs
        
        # Create sample tasks for user1
        today = date.today()
        
        tasks = [
            Task(
                title='Complete project documentation',
                description='Write comprehensive documentation for the project',
                status='Completed',
                priority='High',
                due_date=today - timedelta(days=2),
                user_id=user1.id,
                completed_date=datetime.now() - timedelta(days=1)
            ),
            Task(
                title='Review code submissions',
                description='Review and provide feedback on team code submissions',
                status='Pending',
                priority='High',
                due_date=today,
                user_id=user1.id
            ),
            Task(
                title='Update website content',
                description='Update the company website with latest information',
                status='Pending',
                priority='Medium',
                due_date=today + timedelta(days=3),
                user_id=user1.id
            ),
            Task(
                title='Organize team meeting',
                description='Schedule and organize weekly team meeting',
                status='Completed',
                priority='Medium',
                due_date=today - timedelta(days=5),
                user_id=user1.id,
                completed_date=datetime.now() - timedelta(days=4)
            ),
            Task(
                title='Clean up old files',
                description='Remove unnecessary files from project directory',
                status='Pending',
                priority='Low',
                due_date=today + timedelta(days=7),
                user_id=user1.id
            ),
            Task(
                title='Research new technologies',
                description='Research and evaluate new development tools',
                status='Pending',
                priority='Low',
                due_date=today - timedelta(days=1),  # Overdue task
                user_id=user1.id
            )
        ]
        
        # Create sample tasks for user2
        user2_tasks = [
            Task(
                title='Prepare presentation',
                description='Prepare slides for client presentation',
                status='Pending',
                priority='High',
                due_date=today + timedelta(days=1),
                user_id=user2.id
            ),
            Task(
                title='Update resume',
                description='Update resume with recent projects',
                status='Completed',
                priority='Medium',
                due_date=today - timedelta(days=3),
                user_id=user2.id,
                completed_date=datetime.now() - timedelta(days=2)
            ),
            Task(
                title='Learn new framework',
                description='Study documentation for React framework',
                status='Pending',
                priority='Low',
                due_date=today + timedelta(days=10),
                user_id=user2.id
            )
        ]
        
        for task in tasks + user2_tasks:
            db.session.add(task)
        
        db.session.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating sample data: {e}")
