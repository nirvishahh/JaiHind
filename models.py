from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    total_points = db.Column(db.Integer, default=0)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with tasks
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_badge(self):
        """Get user's badge based on points"""
        if self.total_points >= 51:
            return {"name": "Gold", "class": "badge-warning"}
        elif self.total_points >= 21:
            return {"name": "Silver", "class": "badge-secondary"}
        else:
            return {"name": "Bronze", "class": "badge-dark"}
    
    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')  # Pending/Completed
    priority = db.Column(db.String(10), default='Medium')  # High/Medium/Low
    due_date = db.Column(db.Date)
    points = db.Column(db.Integer, default=5)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime)
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status == 'Pending':
            return self.due_date < datetime.now().date()
        return False
    
    def is_due_today(self):
        """Check if task is due today"""
        if self.due_date and self.status == 'Pending':
            return self.due_date == datetime.now().date()
        return False
    
    def get_priority_class(self):
        """Get CSS class for priority styling"""
        priority_classes = {
            'High': 'text-danger fw-bold',
            'Medium': 'text-warning fw-bold',
            'Low': 'text-success fw-bold'
        }
        return priority_classes.get(self.priority, 'text-secondary')
    
    def __repr__(self):
        return f'<Task {self.title}>'
