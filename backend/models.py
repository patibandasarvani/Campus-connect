# College Management System - Database Models
# Production-ready models with proper relationships and validation

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and role management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, hod, faculty, student
    department = db.Column(db.String(50), default='General')
    email = db.Column(db.String(120), unique=True, index=True)
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with students (faculty can add students)
    students_added = db.relationship('Student', backref='added_by_user', lazy='dynamic', foreign_keys='Student.created_by')
    
    def set_password(self, password):
        """Hash password before storing"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        """Convert user object to dictionary for JSON response"""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'department': self.department,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Student(db.Model):
    """Student model for academic records"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    roll = db.Column(db.String(50), unique=True, nullable=False, index=True)
    department = db.Column(db.String(50), nullable=False, index=True)
    marks = db.Column(db.Integer, nullable=False, default=0)
    semester = db.Column(db.String(20), default='1')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert student object to dictionary for JSON response"""
        return {
            'id': self.id,
            'name': self.name,
            'roll': self.roll,
            'department': self.department,
            'marks': self.marks,
            'semester': self.semester,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_student_by_roll(roll):
        """Get student by roll number"""
        return Student.query.filter_by(roll=roll).first()
    
    @staticmethod
    def get_student_by_id(student_id):
        """Get student by ID"""
        return Student.query.get(student_id)
    
    @staticmethod
    def get_students_by_department(department):
        """Get all students in a department"""
        return Student.query.filter_by(department=department).all()
    
    @staticmethod
    def get_all_students():
        """Get all students"""
        return Student.query.all()
    
    @staticmethod
    def get_top_performers(limit=10):
        """Get top performing students"""
        return Student.query.order_by(Student.marks.desc()).limit(limit).all()
    
    @staticmethod
    def get_average_marks():
        """Get average marks of all students"""
        result = db.session.query(db.func.avg(Student.marks)).first()
        return round(result[0], 2) if result and result[0] else 0
    
    @staticmethod
    def get_department_stats():
        """Get statistics by department"""
        stats = db.session.query(
            Student.department,
            db.func.count(Student.id).label('total_students'),
            db.func.avg(Student.marks).label('avg_marks'),
            db.func.max(Student.marks).label('max_marks'),
            db.func.min(Student.marks).label('min_marks')
        ).group_by(Student.department).all()
        
        return [{
            'department': stat.department,
            'total_students': stat.total_students,
            'avg_marks': round(stat.avg_marks, 2) if stat.avg_marks else 0,
            'max_marks': stat.max_marks or 0,
            'min_marks': stat.min_marks or 0
        } for stat in stats]
    
    @staticmethod
    def get_performance_distribution():
        """Get performance distribution"""
        total = Student.query.count()
        if total == 0:
            return {
                'excellent': 0,
                'good': 0,
                'average': 0,
                'poor': 0
            }
        
        excellent = Student.query.filter(Student.marks >= 80).count()
        good = Student.query.filter(Student.marks >= 60, Student.marks < 80).count()
        average = Student.query.filter(Student.marks >= 40, Student.marks < 60).count()
        poor = Student.query.filter(Student.marks < 40).count()
        
        return {
            'excellent': excellent,
            'good': good,
            'average': average,
            'poor': poor,
            'total': total
        }
    
    def get_performance_grade(self):
        """Get performance grade based on marks"""
        if self.marks >= 90:
            return 'A+'
        elif self.marks >= 80:
            return 'A'
        elif self.marks >= 70:
            return 'B'
        elif self.marks >= 60:
            return 'C'
        elif self.marks >= 50:
            return 'D'
        else:
            return 'F'
    
    def get_performance_status(self):
        """Get performance status"""
        if self.marks >= 80:
            return 'Excellent'
        elif self.marks >= 60:
            return 'Good'
        elif self.marks >= 40:
            return 'Average'
        else:
            return 'Poor'
    
    def __repr__(self):
        return f'<Student {self.name} ({self.roll})>'


class AuditLog(db.Model):
    """Audit log for tracking system changes"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # CREATE, UPDATE, DELETE
    resource_type = db.Column(db.String(50), nullable=False)  # USER, STUDENT
    resource_id = db.Column(db.Integer, nullable=False)
    old_values = db.Column(db.Text)  # JSON string
    new_values = db.Column(db.Text)  # JSON string
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'old_values': json.loads(self.old_values) if self.old_values else None,
            'new_values': json.loads(self.new_values) if self.new_values else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @staticmethod
    def log_action(user_id, action, resource_type, resource_id, old_values=None, new_values=None, ip_address=None, user_agent=None):
        """Log an action for audit trail"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(audit_log)
        return audit_log
    
    def __repr__(self):
        return f'<AuditLog {self.action} {self.resource_type} {self.resource_id}>'


# Database initialization functions
def init_database():
    """Initialize database with default data"""
    db.create_all()
    
    # Check if admin user exists
    admin_user = User.query.filter_by(role='admin').first()
    if not admin_user:
        # Create default admin user
        admin = User(
            username='admin',
            role='admin',
            department='Administration',
            email='admin@college.edu',
            full_name='System Administrator'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: username=admin, password=admin123")


def get_db_stats():
    """Get comprehensive database statistics"""
    return {
        'users': {
            'total': User.query.count(),
            'admin': User.query.filter_by(role='admin').count(),
            'hod': User.query.filter_by(role='hod').count(),
            'faculty': User.query.filter_by(role='faculty').count(),
            'student': User.query.filter_by(role='student').count()
        },
        'students': {
            'total': Student.query.count(),
            'avg_marks': Student.get_average_marks(),
            'top_performer': Student.query.order_by(Student.marks.desc()).first(),
            'department_stats': Student.get_department_stats(),
            'performance_distribution': Student.get_performance_distribution()
        },
        'audit_logs': {
            'total': AuditLog.query.count(),
            'recent': AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
        }
    }


# Database helper functions
def verify_user_role(user_id, required_role):
    """Verify if user has required role"""
    user = User.query.get(user_id)
    if not user:
        return False
    return user.role == required_role


def check_permission(user_id, resource_id, action):
    """Check if user has permission to perform action on resource"""
    user = User.query.get(user_id)
    if not user:
        return False
    
    # Admin can do everything
    if user.role == 'admin':
        return True
    
    # HOD can view and manage department resources
    if user.role == 'hod':
        if action in ['view', 'read']:
            return True
        # For write operations, check if resource belongs to user's department
        if resource_id:
            student = Student.query.get(resource_id)
            if student and student.department == user.department:
                return True
    
    # Faculty can manage students in their department
    if user.role == 'faculty':
        if action in ['view', 'read']:
            return True
        # For write operations, check if resource belongs to user's department or was added by user
        if resource_id:
            student = Student.query.get(resource_id)
            if student and (student.department == user.department or student.created_by == user_id):
                return True
    
    # Students can only view their own data
    if user.role == 'student':
        if action == 'view' and resource_id:
            student = Student.query.get(resource_id)
            if student and student.roll == user.username:
                return True
    
    return False
