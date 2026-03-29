# College Management System - Student Management Routes
# Production-ready REST API for student CRUD operations

from flask import Blueprint, request, jsonify, session
from models import Student, User, db, AuditLog, check_permission
from .auth import require_auth, require_role, api_response
import datetime

student_bp = Blueprint('student', __name__, url_prefix='/api/students')

# Helper function to check student access permissions
def check_student_access(action, student_id=None):
    """Check if current user has permission to perform action on student"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    user_department = session.get('user_department')
    
    # Admin can do everything
    if user_role == 'admin':
        return True
    
    # HOD can view and manage students in their department
    if user_role == 'hod':
        if action in ['view', 'read']:
            return True
        if student_id:
            student = Student.query.get(student_id)
            return student and student.department == user_department
    
    # Faculty can add students and manage students in their department
    if user_role == 'faculty':
        if action in ['view', 'read']:
            return True
        if action == 'create':
            return True  # Faculty can add students
        if student_id:
            student = Student.query.get(student_id)
            return student and (student.department == user_department or student.created_by == user_id)
    
    # Students can only view their own data
    if user_role == 'student':
        if action == 'view' and student_id:
            student = Student.query.get(student_id)
            return student and student.roll == session.get('username')
    
    return False

@student_bp.route('/', methods=['GET'])
@require_auth
def get_students():
    """Get students with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        department = request.args.get('department', '')
        semester = request.args.get('semester', '')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        
        # Build base query based on user role
        user_role = session.get('user_role')
        user_department = session.get('user_department')
        user_id = session.get('user_id')
        username = session.get('username')
        
        if user_role == 'student':
            # Students can only see themselves
            query = Student.query.filter(Student.roll == username)
        elif user_role == 'faculty':
            # Faculty can see students in their department or added by them
            query = Student.query.filter(
                (Student.department == user_department) | (Student.created_by == user_id)
            )
        elif user_role == 'hod':
            # HOD can see students in their department
            query = Student.query.filter(Student.department == user_department)
        else:
            # Admin can see all students
            query = Student.query
        
        # Apply filters
        if department:
            query = query.filter(Student.department == department)
        
        if semester:
            query = query.filter(Student.semester == semester)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Student.name.like(search_term)) |
                (Student.roll.like(search_term))
            )
        
        # Apply sorting
        if sort_by == 'name':
            query = query.order_by(Student.name.asc() if sort_order == 'asc' else Student.name.desc())
        elif sort_by == 'roll':
            query = query.order_by(Student.roll.asc() if sort_order == 'asc' else Student.roll.desc())
        elif sort_by == 'marks':
            query = query.order_by(Student.marks.asc() if sort_order == 'asc' else Student.marks.desc())
        elif sort_by == 'department':
            query = query.order_by(Student.department.asc() if sort_order == 'asc' else Student.department.desc())
        else:
            query = query.order_by(Student.name.asc())
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        students = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Get statistics
        stats = {}
        if user_role != 'student':
            all_students = Student.query.all()
            if user_role == 'faculty':
                all_students = [s for s in all_students if s.department == user_department or s.created_by == user_id]
            elif user_role == 'hod':
                all_students = [s for s in all_students if s.department == user_department]
            
            if all_students:
                total_marks = sum(s.marks for s in all_students)
                avg_marks = round(total_marks / len(all_students), 2)
                top_student = max(all_students, key=lambda x: x.marks)
                
                stats = {
                    'total_students': len(all_students),
                    'average_marks': avg_marks,
                    'top_student': top_student.to_dict() if top_student else None
                }
        
        return api_response(
            True,
            'Students retrieved successfully',
            {
                'students': [student.to_dict() for student in students],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                },
                'stats': stats
            }
        )
        
    except Exception as e:
        return api_response(False, f'Failed to get students: {str(e)}', None, 500)

@student_bp.route('/', methods=['POST'])
@require_role('admin', 'faculty')
def create_student():
    """Create a new student"""
    try:
        data = request.get_json()
        
        if not data or not all(key in data for key in ['name', 'roll', 'department']):
            return api_response(False, 'Missing required fields: name, roll, department', None, 400)
        
        name = data['name'].strip()
        roll = data['roll'].strip()
        department = data['department'].strip()
        marks = data.get('marks', 0)
        semester = data.get('semester', '1')
        
        # Validate input
        if len(name) < 2:
            return api_response(False, 'Name must be at least 2 characters long', None, 400)
        
        if len(roll) < 3:
            return api_response(False, 'Roll number must be at least 3 characters long', None, 400)
        
        if not department:
            return api_response(False, 'Department is required', None, 400)
        
        # Validate marks
        try:
            marks = int(marks)
            if marks < 0 or marks > 100:
                return api_response(False, 'Marks must be between 0 and 100', None, 400)
        except (ValueError, TypeError):
            return api_response(False, 'Marks must be a valid number', None, 400)
        
        # Check if roll number already exists
        existing_student = Student.query.filter_by(roll=roll).first()
        if existing_student:
            return api_response(False, 'Roll number already exists', None, 409)
        
        # Check faculty department permission
        user_role = session.get('user_role')
        user_department = session.get('user_department')
        
        if user_role == 'faculty' and department != user_department:
            return api_response(False, 'You can only add students to your department', None, 403)
        
        # Create student
        student = Student(
            name=name,
            roll=roll,
            department=department,
            marks=marks,
            semester=semester,
            created_by=session.get('user_id')
        )
        
        db.session.add(student)
        db.session.commit()
        
        # Log the creation
        AuditLog.log_action(
            user_id=session.get('user_id'),
            action='CREATE',
            resource_type='STUDENT',
            resource_id=student.id,
            new_values=student.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return api_response(True, 'Student created successfully', {'student': student.to_dict()}, 201)
        
    except Exception as e:
        db.session.rollback()
        return api_response(False, f'Student creation failed: {str(e)}', None, 500)

@student_bp.route('/<int:student_id>', methods=['GET'])
@require_auth
def get_student(student_id):
    """Get a specific student by ID"""
    try:
        if not check_student_access('view', student_id):
            return api_response(False, 'Permission denied', None, 403)
        
        student = Student.query.get(student_id)
        if not student:
            return api_response(False, 'Student not found', None, 404)
        
        return api_response(True, 'Student retrieved successfully', {'student': student.to_dict()})
        
    except Exception as e:
        return api_response(False, f'Failed to get student: {str(e)}', None, 500)

@student_bp.route('/<int:student_id>', methods=['PUT'])
@require_auth
def update_student(student_id):
    """Update a student"""
    try:
        if not check_student_access('update', student_id):
            return api_response(False, 'Permission denied', None, 403)
        
        student = Student.query.get(student_id)
        if not student:
            return api_response(False, 'Student not found', None, 404)
        
        data = request.get_json()
        if not data:
            return api_response(False, 'No data provided', None, 400)
        
        # Store old values for audit
        old_values = student.to_dict()
        
        # Update allowed fields
        if 'name' in data:
            name = data['name'].strip()
            if len(name) < 2:
                return api_response(False, 'Name must be at least 2 characters long', None, 400)
            student.name = name
        
        if 'roll' in data:
            roll = data['roll'].strip()
            if len(roll) < 3:
                return api_response(False, 'Roll number must be at least 3 characters long', None, 400)
            
            # Check if roll number is used by another student
            existing_student = Student.query.filter(Student.roll == roll, Student.id != student_id).first()
            if existing_student:
                return api_response(False, 'Roll number already exists', None, 409)
            
            student.roll = roll
        
        if 'department' in data:
            department = data['department'].strip()
            if not department:
                return api_response(False, 'Department is required', None, 400)
            
            # Check faculty department permission
            user_role = session.get('user_role')
            user_department = session.get('user_department')
            
            if user_role == 'faculty' and department != user_department and student.created_by != session.get('user_id'):
                return api_response(False, 'You can only update students in your department', None, 403)
            
            student.department = department
        
        if 'semester' in data:
            student.semester = str(data['semester'])
        
        if 'marks' in data:
            marks = data['marks']
            try:
                marks = int(marks)
                if marks < 0 or marks > 100:
                    return api_response(False, 'Marks must be between 0 and 100', None, 400)
                student.marks = marks
            except (ValueError, TypeError):
                return api_response(False, 'Marks must be a valid number', None, 400)
        
        db.session.commit()
        
        # Log the update
        AuditLog.log_action(
            user_id=session.get('user_id'),
            action='UPDATE',
            resource_type='STUDENT',
            resource_id=student.id,
            old_values=old_values,
            new_values=student.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return api_response(True, 'Student updated successfully', {'student': student.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return api_response(False, f'Student update failed: {str(e)}', None, 500)

@student_bp.route('/<int:student_id>', methods=['DELETE'])
@require_auth
def delete_student(student_id):
    """Delete a student"""
    try:
        if not check_student_access('delete', student_id):
            return api_response(False, 'Permission denied', None, 403)
        
        student = Student.query.get(student_id)
        if not student:
            return api_response(False, 'Student not found', None, 404)
        
        # Store old values for audit
        old_values = student.to_dict()
        
        # Additional permission check for deletion
        user_role = session.get('user_role')
        user_id = session.get('user_id')
        
        # Faculty can only delete students they added
        if user_role == 'faculty' and student.created_by != user_id:
            return api_response(False, 'You can only delete students you added', None, 403)
        
        db.session.delete(student)
        db.session.commit()
        
        # Log the deletion
        AuditLog.log_action(
            user_id=user_id,
            action='DELETE',
            resource_type='STUDENT',
            resource_id=student.id,
            old_values=old_values,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return api_response(True, 'Student deleted successfully', None)
        
    except Exception as e:
        db.session.rollback()
        return api_response(False, f'Student deletion failed: {str(e)}', None, 500)

@student_bp.route('/stats', methods=['GET'])
@require_auth
def get_student_stats():
    """Get student statistics"""
    try:
        user_role = session.get('user_role')
        user_department = session.get('user_department')
        user_id = session.get('user_id')
        username = session.get('username')
        
        # Get students based on user role
        if user_role == 'student':
            # Students can only see their own stats
            student = Student.query.filter(Student.roll == username).first()
            if not student:
                return api_response(False, 'Student record not found', None, 404)
            
            stats = {
                'total_students': 1,
                'average_marks': student.marks,
                'top_student': student.to_dict(),
                'department_stats': [{
                    'department': student.department,
                    'total_students': 1,
                    'avg_marks': student.marks,
                    'max_marks': student.marks,
                    'min_marks': student.marks
                }],
                'performance_distribution': {
                    'excellent': 1 if student.marks >= 80 else 0,
                    'good': 1 if 60 <= student.marks < 80 else 0,
                    'average': 1 if 40 <= student.marks < 60 else 0,
                    'poor': 1 if student.marks < 40 else 0,
                    'total': 1
                }
            }
        else:
            # Get students based on role permissions
            if user_role == 'faculty':
                students = Student.query.filter(
                    (Student.department == user_department) | (Student.created_by == user_id)
                ).all()
            elif user_role == 'hod':
                students = Student.query.filter(Student.department == user_department).all()
            else:  # admin
                students = Student.query.all()
            
            if students:
                total_marks = sum(s.marks for s in students)
                avg_marks = round(total_marks / len(students), 2)
                top_student = max(students, key=lambda x: x.marks)
                
                # Department stats
                dept_stats = {}
                for student in students:
                    dept = student.department
                    if dept not in dept_stats:
                        dept_stats[dept] = {
                            'total_students': 0,
                            'total_marks': 0,
                            'max_marks': student.marks,
                            'min_marks': student.marks
                        }
                    
                    dept_stats[dept]['total_students'] += 1
                    dept_stats[dept]['total_marks'] += student.marks
                    dept_stats[dept]['max_marks'] = max(dept_stats[dept]['max_marks'], student.marks)
                    dept_stats[dept]['min_marks'] = min(dept_stats[dept]['min_marks'], student.marks)
                
                # Calculate averages
                department_stats = []
                for dept, stats in dept_stats.items():
                    department_stats.append({
                        'department': dept,
                        'total_students': stats['total_students'],
                        'avg_marks': round(stats['total_marks'] / stats['total_students'], 2),
                        'max_marks': stats['max_marks'],
                        'min_marks': stats['min_marks']
                    })
                
                # Performance distribution
                excellent = sum(1 for s in students if s.marks >= 80)
                good = sum(1 for s in students if 60 <= s.marks < 80)
                average = sum(1 for s in students if 40 <= s.marks < 60)
                poor = sum(1 for s in students if s.marks < 40)
                
                stats = {
                    'total_students': len(students),
                    'average_marks': avg_marks,
                    'top_student': top_student.to_dict(),
                    'department_stats': department_stats,
                    'performance_distribution': {
                        'excellent': excellent,
                        'good': good,
                        'average': average,
                        'poor': poor,
                        'total': len(students)
                    }
                }
            else:
                stats = {
                    'total_students': 0,
                    'average_marks': 0,
                    'top_student': None,
                    'department_stats': [],
                    'performance_distribution': {
                        'excellent': 0,
                        'good': 0,
                        'average': 0,
                        'poor': 0,
                        'total': 0
                    }
                }
        
        return api_response(True, 'Student statistics retrieved successfully', stats)
        
    except Exception as e:
        return api_response(False, f'Failed to get student statistics: {str(e)}', None, 500)

@student_bp.route('/departments', methods=['GET'])
@require_auth
def get_departments():
    """Get list of departments"""
    try:
        user_role = session.get('user_role')
        user_department = session.get('user_department')
        
        if user_role == 'student':
            # Students only see their own department
            departments = [user_department] if user_department else []
        elif user_role in ['faculty', 'hod']:
            # Faculty and HOD see their department
            departments = [user_department] if user_department else []
        else:
            # Admin sees all departments
            departments = db.session.query(Student.department).distinct().all()
            departments = [dept[0] for dept in departments if dept[0]]
        
        return api_response(True, 'Departments retrieved successfully', {'departments': departments})
        
    except Exception as e:
        return api_response(False, f'Failed to get departments: {str(e)}', None, 500)

@student_bp.route('/search', methods=['GET'])
@require_auth
def search_students():
    """Search students with advanced filtering"""
    try:
        query = request.args.get('q', '').strip()
        department = request.args.get('department', '')
        semester = request.args.get('semester', '')
        min_marks = request.args.get('min_marks', type=int)
        max_marks = request.args.get('max_marks', type=int)
        
        if not query and not department and not semester and min_marks is None and max_marks is None:
            return api_response(False, 'At least one search parameter is required', None, 400)
        
        # Build base query based on user role
        user_role = session.get('user_role')
        user_department = session.get('user_department')
        user_id = session.get('user_id')
        username = session.get('username')
        
        if user_role == 'student':
            base_query = Student.query.filter(Student.roll == username)
        elif user_role == 'faculty':
            base_query = Student.query.filter(
                (Student.department == user_department) | (Student.created_by == user_id)
            )
        elif user_role == 'hod':
            base_query = Student.query.filter(Student.department == user_department)
        else:
            base_query = Student.query
        
        # Apply search filters
        if query:
            search_term = f"%{query}%"
            base_query = base_query.filter(
                (Student.name.like(search_term)) |
                (Student.roll.like(search_term))
            )
        
        if department:
            base_query = base_query.filter(Student.department == department)
        
        if semester:
            base_query = base_query.filter(Student.semester == semester)
        
        if min_marks is not None:
            base_query = base_query.filter(Student.marks >= min_marks)
        
        if max_marks is not None:
            base_query = base_query.filter(Student.marks <= max_marks)
        
        # Execute query
        students = base_query.all()
        
        return api_response(
            True,
            f'Found {len(students)} students',
            {
                'students': [student.to_dict() for student in students],
                'count': len(students)
            }
        )
        
    except Exception as e:
        return api_response(False, f'Search failed: {str(e)}', None, 500)
