# College Management System - Main Flask Application
# Production-ready REST API with CORS and proper configuration

from flask import Flask, jsonify, request, session, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import os
from werkzeug.exceptions import HTTPException

# Import models and routes
from models import db, init_database
from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp

# Initialize Flask app
app = Flask(__name__)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'college-management-system-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Load configuration
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

# Configure CORS for frontend-backend communication
CORS(app, 
     origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5500', 'http://127.0.0.1:5500'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True,
     expose_headers=['Content-Type'])

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'message': 'Bad request',
        'error': str(error)
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'message': 'Unauthorized access',
        'error': str(error)
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'message': 'Access forbidden',
        'error': str(error)
    }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Resource not found',
        'error': str(error)
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'message': 'Method not allowed',
        'error': str(error)
    }), 405

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'success': False,
        'message': 'Internal server error',
        'error': str(error)
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    db.session.rollback()
    return jsonify({
        'success': False,
        'message': 'An unexpected error occurred',
        'error': str(e)
    }), 500

# Root endpoint
@app.route('/')
def index():
    return send_from_directory('../', 'simple-login.html')

# Serve static files with specific extensions
@app.route('/<path:filename>')
def serve_static(filename):
    # Only serve static files, not API routes
    if '.' in filename and filename.split('.')[-1] in ['html', 'css', 'js', 'png', 'jpg', 'jpeg', 'gif', 'ico', 'svg']:
        return send_from_directory('../', filename)
    else:
        # Let API routes handle other paths
        from flask import abort
        abort(404)

# API Info endpoint
@app.route('/api/info')
def api_info():
    return jsonify({
        'success': True,
        'message': 'College Management System API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'students': '/api/students',
            'admin': '/api/admin'
        },
        'documentation': {
            'register': 'POST /api/auth/register',
            'login': 'POST /api/auth/login',
            'logout': 'GET /api/auth/logout',
            'get_students': 'GET /api/students',
            'create_student': 'POST /api/students',
            'update_student': 'PUT /api/students/<id>',
            'delete_student': 'DELETE /api/students/<id>',
            'admin_dashboard': 'GET /api/admin/dashboard'
        }
    })

# Health check endpoint
@app.route('/health')
def health_check():
    try:
        # Test database connection using SQLAlchemy
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': 'connected',
            'message': 'API is running'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

# Session management
@app.before_request
def before_request():
    """Set up session and request handling"""
    # Make session permanent
    session.permanent = True
    
    # Log request for debugging (remove in production)
    if app.debug:
        print(f"[{request.method}] {request.path} - {request.remote_addr}")

@app.after_request
def after_request(response):
    """Modify response after request"""
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response

# Database initialization
def init_database_on_startup():
    """Create database tables before first request"""
    with app.app_context():
        try:
            init_database()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")

# Initialize database on startup
init_database_on_startup()

# CLI commands
@app.cli.command()
def init_db():
    """Initialize the database"""
    """Initialize the database with default data"""
    with app.app_context():
        try:
            init_database()
            print("✅ Database initialized successfully")
            print("👤 Default admin user created: username=admin, password=admin123")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")

@app.cli.command()
def create_admin():
    """Create an admin user"""
    """Create an admin user interactively"""
    from models import User
    
    with app.app_context():
        username = input("Enter admin username: ").strip()
        password = input("Enter admin password: ").strip()
        email = input("Enter admin email (optional): ").strip()
        full_name = input("Enter admin full name (optional): ").strip()
        
        if not username or not password:
            print("❌ Username and password are required")
            return
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            print("❌ User already exists")
            return
        
        # Create admin user
        admin = User(
            username=username,
            role='admin',
            email=email if email else None,
            full_name=full_name if full_name else None,
            department='Administration'
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ Admin user '{username}' created successfully")

@app.cli.command()
def reset_db():
    """Reset the database (dangerous!)"""
    """Reset the database - all data will be lost"""
    if input("⚠️  This will delete all data. Are you sure? (yes/no): ").lower() != 'yes':
        print("❌ Database reset cancelled")
        return
    
    with app.app_context():
        try:
            db.drop_all()
            db.create_all()
            init_database()
            print("✅ Database reset successfully")
        except Exception as e:
            print(f"❌ Database reset failed: {e}")

# Development server configuration
if __name__ == '__main__':
    # Create database if it doesn't exist
    with app.app_context():
        try:
            init_database()
        except Exception as e:
            print(f"Database initialization warning: {e}")
    
    # Run the development server
    print("🚀 Starting College Management System API Server...")
    print("📡 Server will be available at: http://127.0.0.1:5000")
    print("🔗 API Documentation: http://127.0.0.1:5000/api/info")
    print("💚 Health Check: http://127.0.0.1:5000/health")
    
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    )
