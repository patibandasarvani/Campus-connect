@echo off
echo 🎓 Campus Connect - Project Launcher
echo =====================================
echo.

echo 🚀 Starting Backend Server...
cd /d "%~dp0backend"
start /B python app.py
timeout /t 3 >nul

echo 🌐 Opening Project Pages...
echo.

echo 📋 Opening Main Application...
start http://localhost:5000

echo 📊 Opening Dashboard...
start http://localhost:5000/dashboard-fixed.html

echo 📚 Opening Course Management...
start http://localhost:5000/courses.html

echo 👥 Opening Student Management...
start http://localhost:5000/frontend/students-enhanced.html

echo 📖 Opening Documentation...
start FRONTEND-FIX-GUIDE.md

echo 🎨 Opening Workflow Diagrams...
start WORKFLOW-DIAGRAMS.html

echo.
echo ✅ Campus Connect Project Started Successfully!
echo.
echo 🔐 Default Login Credentials:
echo    Admin: admin/admin123
echo    Faculty: faculty/faculty123
echo    Student: student/student123
echo.
echo 📊 Expected Statistics:
echo    Students: 35+
echo    Faculty: 10
echo    Courses: 16
echo    Departments: 10
echo.
echo 🎯 Next Steps:
echo 1. Test login with different user types
echo 2. Check dashboard shows real statistics
echo 3. Test student and course management
echo 4. Verify reports and charts work
echo 5. Test all CRUD operations
echo.
echo 🚀 Your Campus Connect System is now running!
echo.

pause
