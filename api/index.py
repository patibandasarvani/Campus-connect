# Vercel Serverless Function for Campus Connect
# Main API handler for Vercel deployment

import sys
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import Flask app from backend
try:
    from app import app as flask_app
    from models import db, Student, User
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.admin import admin_bp
except ImportError as e:
    print(f"Import error: {e}")

def handler(request):
    """Main handler for Vercel serverless functions"""
    
    # Create Flask app if not imported
    try:
        app = flask_app
        
        # Register blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(student_bp)
        app.register_blueprint(admin_bp)
        
        # Configure for Vercel
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///campus_connect.db')
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
        
        # Initialize database
        with app.app_context():
            db.create_all()
        
        # Handle request
        with app.app_context():
            return app(request.environ, lambda status, headers: None)
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Server error: {str(e)}',
                'message': 'Failed to initialize Flask app'
            })
        }

# Vercel serverless function entry point
def lambda_handler(event, context):
    """AWS Lambda style handler for Vercel"""
    return handler(event)
