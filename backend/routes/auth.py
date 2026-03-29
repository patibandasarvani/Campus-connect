# College Management System - Authentication Routes
# Production-ready REST API for user authentication

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db, AuditLog
from functools import wraps
import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Helper function for API responses
def api_response(success=True, message=None, data=None, status_code=200):
    """Standard API response format"""
    response = {
        'success': success,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code

# Authentication decorator for API endpoints
def require_auth(f):
    """Decorator to require authentication for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return api_response(False, 'Authentication required', None, 401)
        return f(*args, **kwargs)
    return decorated_function

# Role-based access decorator
def require_role(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return api_response(False, 'Authentication required', None, 401)
            
            user = User.query.get(session['user_id'])
            if not user or user.role not in allowed_roles:
                return api_response(False, 'Insufficient permissions', None, 403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(key in data for key in ['username', 'password', 'role']):
            return api_response(False, 'Missing required fields: username, password, role', None, 400)
        
        username = data['username'].strip()
        password = data['password']
        role = data['role'].lower()
        email = data.get('email', '').strip()
        full_name = data.get('full_name', '').strip()
        department = data.get('department', 'General').strip()
        
        # Validate role
        valid_roles = ['admin', 'hod', 'faculty', 'student']
        if role not in valid_roles:
            return api_response(False, f'Invalid role. Must be one of: {", ".join(valid_roles)}', None, 400)
        
        # Validate input
        if len(username) < 3:
            return api_response(False, 'Username must be at least 3 characters long', None, 400)
        
        if len(password) < 6:
            return api_response(False, 'Password must be at least 6 characters long', None, 400)
        
        if email and '@' not in email:
            return api_response(False, 'Invalid email format', None, 400)
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return api_response(False, 'Username already exists', None, 409)
        
        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                return api_response(False, 'Email already exists', None, 409)
        
        # Check if this is the first user (becomes admin automatically)
        user_count = User.query.count()
        if user_count == 0:
            role = 'admin'
        
        # Create new user
        user = User(
            username=username,
            role=role,
            email=email if email else None,
            full_name=full_name if full_name else None,
            department=department
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log the registration
        AuditLog.log_action(
            user_id=user.id,
            action='CREATE',
            resource_type='USER',
            resource_id=user.id,
            new_values=user.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return api_response(
            True, 
            'User registered successfully', 
            {
                'user': user.to_dict(),
                'is_first_user': user_count == 0
            },
            201
        )
        
    except Exception as e:
        db.session.rollback()
        return api_response(False, f'Registration failed: {str(e)}', None, 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data or not all(key in data for key in ['username', 'password']):
            return api_response(False, 'Missing required fields: username, password', None, 400)
        
        username = data['username'].strip()
        password = data['password']
        
        # Validate input
        if not username or not password:
            return api_response(False, 'Username and password are required', None, 400)
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return api_response(False, 'Invalid username or password', None, 401)
        
        # Create session
        session['user_id'] = user.id
        session['username'] = user.username
        session['user_role'] = user.role
        session['user_department'] = user.department
        session['user_full_name'] = user.full_name
        session['login_time'] = datetime.datetime.utcnow().isoformat()
        
        # Log the login
        AuditLog.log_action(
            user_id=user.id,
            action='LOGIN',
            resource_type='USER',
            resource_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return api_response(
            True, 
            'Login successful', 
            {
                'user': user.to_dict(),
                'session_info': {
                    'login_time': session['login_time']
                }
            }
        )
        
    except Exception as e:
        return api_response(False, f'Login failed: {str(e)}', None, 500)

@auth_bp.route('/logout', methods=['GET'])
@require_auth
def logout():
    """User logout"""
    try:
        user_id = session.get('user_id')
        
        # Log the logout
        if user_id:
            AuditLog.log_action(
                user_id=user_id,
                action='LOGOUT',
                resource_type='USER',
                resource_id=user_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
        
        # Clear session
        session.clear()
        
        return api_response(True, 'Logout successful', None)
        
    except Exception as e:
        return api_response(False, f'Logout failed: {str(e)}', None, 500)

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get current user profile"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return api_response(False, 'User not found', None, 404)
        
        return api_response(True, 'Profile retrieved successfully', {'user': user.to_dict()})
        
    except Exception as e:
        return api_response(False, f'Failed to get profile: {str(e)}', None, 500)

@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update current user profile"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return api_response(False, 'User not found', None, 404)
        
        data = request.get_json()
        if not data:
            return api_response(False, 'No data provided', None, 400)
        
        # Store old values for audit
        old_values = user.to_dict()
        
        # Update allowed fields
        if 'email' in data:
            email = data['email'].strip()
            if email and '@' not in email:
                return api_response(False, 'Invalid email format', None, 400)
            
            # Check if email is already used by another user
            if email and email != user.email:
                existing_email = User.query.filter_by(email=email).first()
                if existing_email:
                    return api_response(False, 'Email already exists', None, 409)
            
            user.email = email if email else None
        
        if 'full_name' in data:
            user.full_name = data['full_name'].strip() if data['full_name'] else None
        
        # Only allow department change for non-admin users
        if 'department' in data and user.role != 'admin':
            user.department = data['department'].strip() if data['department'] else 'General'
        
        # Password change
        if 'current_password' in data and 'new_password' in data:
            current_password = data['current_password']
            new_password = data['new_password']
            
            if not user.check_password(current_password):
                return api_response(False, 'Current password is incorrect', None, 400)
            
            if len(new_password) < 6:
                return api_response(False, 'New password must be at least 6 characters long', None, 400)
            
            user.set_password(new_password)
        
        db.session.commit()
        
        # Log the profile update
        AuditLog.log_action(
            user_id=user.id,
            action='UPDATE',
            resource_type='USER',
            resource_id=user.id,
            old_values=old_values,
            new_values=user.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return api_response(True, 'Profile updated successfully', {'user': user.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return api_response(False, f'Profile update failed: {str(e)}', None, 500)

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return api_response(
                True, 
                'User is authenticated', 
                {
                    'user': user.to_dict(),
                    'session_info': {
                        'login_time': session.get('login_time')
                    }
                }
            )
    
    return api_response(False, 'User not authenticated', None, 401)

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return api_response(False, 'User not found', None, 404)
        
        data = request.get_json()
        if not data or not all(key in data for key in ['current_password', 'new_password']):
            return api_response(False, 'Missing required fields: current_password, new_password', None, 400)
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        if not user.check_password(current_password):
            return api_response(False, 'Current password is incorrect', None, 400)
        
        if len(new_password) < 6:
            return api_response(False, 'New password must be at least 6 characters long', None, 400)
        
        old_values = {'password': user.password}  # Hashed password
        
        user.set_password(new_password)
        db.session.commit()
        
        # Log the password change
        AuditLog.log_action(
            user_id=user.id,
            action='PASSWORD_CHANGE',
            resource_type='USER',
            resource_id=user.id,
            old_values=old_values,
            new_values={'password': user.password},  # New hashed password
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return api_response(True, 'Password changed successfully', None)
        
    except Exception as e:
        db.session.rollback()
        return api_response(False, f'Password change failed: {str(e)}', None, 500)

@auth_bp.route('/users', methods=['GET'])
@require_role('admin')
def get_all_users():
    """Get all users (Admin only)"""
    try:
        users = User.query.all()
        users_data = [user.to_dict() for user in users]
        
        return api_response(True, 'Users retrieved successfully', {'users': users_data})
        
    except Exception as e:
        return api_response(False, f'Failed to get users: {str(e)}', None, 500)

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user_by_id(user_id):
    """Get user by ID (with permission check)"""
    try:
        current_user_id = session.get('user_id')
        current_user = User.query.get(current_user_id)
        
        # Users can only view their own profile unless they're admin
        if current_user.role != 'admin' and current_user_id != user_id:
            return api_response(False, 'Permission denied', None, 403)
        
        user = User.query.get(user_id)
        if not user:
            return api_response(False, 'User not found', None, 404)
        
        return api_response(True, 'User retrieved successfully', {'user': user.to_dict()})
        
    except Exception as e:
        return api_response(False, f'Failed to get user: {str(e)}', None, 500)
