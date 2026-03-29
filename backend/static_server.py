# Static File Server for Frontend
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='../')

@app.route('/')
def index():
    return send_from_directory('../', 'simple-login.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('../', filename)

if __name__ == '__main__':
    print("🌐 Static File Server Starting...")
    print("📍 Frontend available at: http://localhost:8080")
    print("📡 Main page: http://localhost:8080/simple-login.html")
    print("📊 Dashboard: http://localhost:8080/dashboard-fixed.html")
    print("📚 Courses: http://localhost:8080/courses.html")
    print("👥 Students: http://localhost:8080/frontend/students-enhanced.html")
    app.run(host='0.0.0.0', port=8080, debug=True)
