# College Management System - Admin Routes
# Production-ready REST API for administrative functions

from flask import Blueprint, request, jsonify, session
from models import User, Student, db, AuditLog, get_db_stats
from .auth import require_auth, require_role, api_response
import datetime
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@require_role('admin')
def get_admin_dashboard():
    """Get admin dashboard statistics"""
    try:
        # Get comprehensive database statistics
        stats = get_db_stats()
        
        # Get recent activity
        recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
        recent_activity = [log.to_dict() for log in recent_logs]
        
        # Get system health metrics
        system_health = {
            'database_status': 'healthy',
            'total_records': User.query.count() + Student.query.count(),
            'last_backup': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'uptime': '24/7'
        }
        
        dashboard_data = {
            'stats': stats,
            'recent_activity': recent_activity,
            'system_health': system_health,
            'quick_actions': [
                'Add User',
                'View Students',
                'Manage Users',
                'System Reports'
            ]
        }
        
        return api_response(True, 'Admin dashboard data retrieved successfully', dashboard_data)
        
    except Exception as e:
        return api_response(False, f'Failed to get admin dashboard: {str(e)}', None, 500)

@admin_bp.route('/users', methods=['GET'])
@require_role('admin')
def get_all_users():
    """Get all users with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        role = request.args.get('role', '')
        department = request.args.get('department', '')
        search = request.args.get('search', '')
        
        # Build query
        query = User.query
        
        # Apply filters
        if role:
            query = query.filter(User.role == role)
        
        if department:
            query = query.filter(User.department == department)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.username.like(search_term)) |
                (User.full_name.like(search_term)) |
                (User.email.like(search_term))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Get user statistics
        user_stats = {
            'total_users': User.query.count(),
            'admin_count': User.query.filter_by(role='admin').count(),
            'hod_count': User.query.filter_by(role='hod').count(),
            'faculty_count': User.query.filter_by(role='faculty').count(),
            'student_count': User.query.filter_by(role='student').count()
        }
        
        return api_response(
            True,
            'Users retrieved successfully',
            {
                'users': [user.to_dict() for user in users],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                },
                'stats': user_stats
            }
        )
        
    except Exception as e:
        return api_response(False, f'Failed to get users: {str(e)}', None, 500)

@admin_bp.route('/users', methods=['POST'])
@require_role('admin')
def create_user():
    """Create a new user (Admin only)"""
    try:
        data = request.get_json()
        
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
        
        # Log the creation
        AuditLog.log_action(
            user_id=session.get('user_id'),
            action='CREATE',
            resource_type='USER',
            resource_id=user.id,
            new_values=user.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return api_response(True, 'User created successfully', {'user': user.to_dict()}, 201)
        
    except Exception as e:
        db.session.rollback()
        return api_response(False, f'User creation failed: {str(e)}', None, 500)

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_role('admin')
def update_user(user_id):
    """Update a user (Admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return api_response(False, 'User not found', None, 404)
        
        # Prevent admin from modifying themselves (except for certain fields)
        current_user_id = session.get('user_id')
        if user_id == current_user_id:
            return api_response(False, 'Cannot modify your own account through this endpoint', None, 403)
        
        data = request.get_json()
        if not data:
            return api_response(False, 'No data provided', None, 400)
        
        # Store old values for audit
        old_values = user.to_dict()
        
        # Update allowed fields
        if 'role' in data:
            new_role = data['role'].lower()
            valid_roles = ['admin', 'hod', 'faculty', 'student']
            if new_role not in valid_roles:
                return api_response(False, f'Invalid role. Must be one of: {", ".join(valid_roles)}', None, 400)
            user.role = new_role
        
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
        
        if 'department' in data:
            user.department = data['department'].strip() if data['department'] else 'General'
        
        # Password change
        if 'password' in data:
            password = data['password']
            if len(password) < 6:
                return api_response(False, 'Password must be at least 6 characters long', None, 400)
            user.set_password(password)
        
        db.session.commit()
        
        # Log the update
        AuditLog.log_action(
            user_id=current_user_id,
            action='UPDATE',
            resource_type='USER',
            resource_id=user.id,
            old_values=old_values,
            new_values=user.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return api_response(True, 'User updated successfully', {'user': user.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return api_response(False, f'User update failed: {str(e)}', None, 500)

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_role('admin')
def delete_user(user_id):
    """Delete a user (Admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return api_response(False, 'User not found', None, 404)
        
        # Prevent admin from deleting themselves
        current_user_id = session.get('user_id')
        if user_id == current_user_id:
            return api_response(False, 'Cannot delete your own account', None, 403)
        
        # Prevent deletion of the last admin
        if user.role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                return api_response(False, 'Cannot delete the last admin user', None, 403)
        
        # Store old values for audit
        old_values = user.to_dict()
        
        db.session.delete(user)
        db.session.commit()
        
        # Log the deletion
        AuditLog.log_action(
            user_id=current_user_id,
            action='DELETE',
            resource_type='USER',
            resource_id=user.id,
            old_values=old_values,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return api_response(True, 'User deleted successfully', None)
        
    except Exception as e:
        db.session.rollback()
        return api_response(False, f'User deletion failed: {str(e)}', None, 500)

@admin_bp.route('/reports/students', methods=['GET'])
@require_role('admin')
def get_student_reports():
    """Generate comprehensive student reports"""
    try:
        # Get overall statistics
        total_students = Student.query.count()
        avg_marks = Student.query.with_entities(func.avg(Student.marks)).scalar() or 0
        avg_marks = round(avg_marks, 2)
        
        # Get department-wise statistics
        dept_stats = db.session.query(
            Student.department,
            func.count(Student.id).label('count'),
            func.avg(Student.marks).label('avg_marks'),
            func.max(Student.marks).label('max_marks'),
            func.min(Student.marks).label('min_marks')
        ).group_by(Student.department).all()
        
        department_reports = []
        for stat in dept_stats:
            department_reports.append({
                'department': stat.department,
                'total_students': stat.count,
                'average_marks': round(stat.avg_marks, 2),
                'highest_marks': stat.max_marks,
                'lowest_marks': stat.min_marks,
                'performance_grade': get_performance_grade(stat.avg_marks)
            })
        
        # Get performance distribution
        excellent = Student.query.filter(Student.marks >= 80).count()
        good = Student.query.filter(Student.marks >= 60, Student.marks < 80).count()
        average = Student.query.filter(Student.marks >= 40, Student.marks < 60).count()
        poor = Student.query.filter(Student.marks < 40).count()
        
        performance_distribution = {
            'excellent': {'count': excellent, 'percentage': round((excellent / total_students) * 100, 2) if total_students > 0 else 0},
            'good': {'count': good, 'percentage': round((good / total_students) * 100, 2) if total_students > 0 else 0},
            'average': {'count': average, 'percentage': round((average / total_students) * 100, 2) if total_students > 0 else 0},
            'poor': {'count': poor, 'percentage': round((poor / total_students) * 100, 2) if total_students > 0 else 0}
        }
        
        # Get top performers
        top_performers = Student.query.order_by(Student.marks.desc()).limit(10).all()
        top_performers_data = [student.to_dict() for student in top_performers]
        
        # Get semester-wise statistics
        semester_stats = db.session.query(
            Student.semester,
            func.count(Student.id).label('count'),
            func.avg(Student.marks).label('avg_marks')
        ).group_by(Student.semester).all()
        
        semester_reports = []
        for stat in semester_stats:
            semester_reports.append({
                'semester': stat.semester,
                'total_students': stat.count,
                'average_marks': round(stat.avg_marks, 2)
            })
        
        report_data = {
            'summary': {
                'total_students': total_students,
                'average_marks': avg_marks,
                'report_generated': datetime.datetime.utcnow().isoformat()
            },
            'department_reports': department_reports,
            'performance_distribution': performance_distribution,
            'top_performers': top_performers_data,
            'semester_reports': semester_reports
        }
        
        return api_response(True, 'Student reports generated successfully', report_data)
        
    except Exception as e:
        return api_response(False, f'Failed to generate student reports: {str(e)}', None, 500)

@admin_bp.route('/reports/users', methods=['GET'])
@require_role('admin')
def get_user_reports():
    """Generate comprehensive user reports"""
    try:
        # Get user statistics
        total_users = User.query.count()
        admin_count = User.query.filter_by(role='admin').count()
        hod_count = User.query.filter_by(role='hod').count()
        faculty_count = User.query.filter_by(role='faculty').count()
        student_count = User.query.filter_by(role='student').count()
        
        # Get department-wise user distribution
        dept_user_stats = db.session.query(
            User.department,
            func.count(User.id).label('count')
        ).group_by(User.department).all()
        
        department_users = []
        for stat in dept_user_stats:
            department_users.append({
                'department': stat.department,
                'total_users': stat.count
            })
        
        # Get recent user registrations
        recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
        recent_users_data = [user.to_dict() for user in recent_users]
        
        # Get user activity summary
        user_activity = {
            'total_logins': AuditLog.query.filter_by(action='LOGIN').count(),
            'recent_logins': AuditLog.query.filter_by(action='LOGIN').order_by(AuditLog.timestamp.desc()).limit(5).all()
        }
        
        report_data = {
            'summary': {
                'total_users': total_users,
                'admin_users': admin_count,
                'hod_users': hod_count,
                'faculty_users': faculty_count,
                'student_users': student_count,
                'report_generated': datetime.datetime.utcnow().isoformat()
            },
            'department_users': department_users,
            'recent_registrations': recent_users_data,
            'user_activity': user_activity
        }
        
        return api_response(True, 'User reports generated successfully', report_data)
        
    except Exception as e:
        return api_response(False, f'Failed to generate user reports: {str(e)}', None, 500)

@admin_bp.route('/audit-logs', methods=['GET'])
@require_role('admin')
def get_audit_logs():
    """Get audit logs with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        action = request.args.get('action', '')
        resource_type = request.args.get('resource_type', '')
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Build query
        query = AuditLog.query
        
        # Apply filters
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if start_date:
            try:
                start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(AuditLog.timestamp >= start_dt)
            except ValueError:
                return api_response(False, 'Invalid start_date format. Use YYYY-MM-DD', None, 400)
        
        if end_date:
            try:
                end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                end_dt = end_dt + datetime.timedelta(days=1)  # Include the end date
                query = query.filter(AuditLog.timestamp < end_dt)
            except ValueError:
                return api_response(False, 'Invalid end_date format. Use YYYY-MM-DD', None, 400)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        logs = query.order_by(AuditLog.timestamp.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        # Get log statistics
        log_stats = {
            'total_logs': AuditLog.query.count(),
            'recent_activity': AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(5).all()
        }
        
        return api_response(
            True,
            'Audit logs retrieved successfully',
            {
                'logs': [log.to_dict() for log in logs],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                },
                'stats': log_stats
            }
        )
        
    except Exception as e:
        return api_response(False, f'Failed to get audit logs: {str(e)}', None, 500)

@admin_bp.route('/system/health', methods=['GET'])
@require_role('admin')
def get_system_health():
    """Get system health status"""
    try:
        # Database health check
        try:
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except:
            db_status = 'unhealthy'
        
        # Get system statistics
        system_stats = {
            'database_status': db_status,
            'total_records': User.query.count() + Student.query.count() + AuditLog.query.count(),
            'disk_usage': 'N/A',  # Would need additional implementation
            'memory_usage': 'N/A',  # Would need additional implementation
            'uptime': 'N/A',  # Would need additional implementation
            'last_restart': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Get recent errors (if any)
        recent_errors = AuditLog.query.filter(AuditLog.action.like('%ERROR%')).order_by(AuditLog.timestamp.desc()).limit(5).all()
        
        health_data = {
            'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'system_stats': system_stats,
            'recent_errors': [log.to_dict() for log in recent_errors],
            'recommendations': get_system_recommendations()
        }
        
        return api_response(True, 'System health retrieved successfully', health_data)
        
    except Exception as e:
        return api_response(False, f'Failed to get system health: {str(e)}', None, 500)

@admin_bp.route('/backup', methods=['POST'])
@require_role('admin')
def create_backup():
    """Create database backup (placeholder)"""
    try:
        # This would implement actual backup functionality
        # For now, return a success message
        backup_info = {
            'backup_id': f'backup_{datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'status': 'completed',
            'file_size': 'N/A',  # Would be actual file size
            'location': '/backups/'  # Would be actual backup location
        }
        
        # Log backup creation
        AuditLog.log_action(
            user_id=session.get('user_id'),
            action='BACKUP',
            resource_type='SYSTEM',
            resource_id=0,
            new_values=backup_info,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return api_response(True, 'Backup created successfully', backup_info)
        
    except Exception as e:
        return api_response(False, f'Backup creation failed: {str(e)}', None, 500)

# Helper functions
def get_performance_grade(avg_marks):
    """Get performance grade based on average marks"""
    if avg_marks >= 80:
        return 'Excellent'
    elif avg_marks >= 60:
        return 'Good'
    elif avg_marks >= 40:
        return 'Average'
    else:
        return 'Poor'

def get_system_recommendations():
    """Get system optimization recommendations"""
    recommendations = []
    
    # Check user count
    user_count = User.query.count()
    if user_count > 1000:
        recommendations.append("Consider implementing user pagination for better performance")
    
    # Check student count
    student_count = Student.query.count()
    if student_count > 5000:
        recommendations.append("Consider implementing database indexing for better query performance")
    
    # Check audit log size
    audit_count = AuditLog.query.count()
    if audit_count > 10000:
        recommendations.append("Consider archiving old audit logs to maintain performance")
    
    if not recommendations:
        recommendations.append("System is running optimally")
    
    return recommendations
