@echo off
echo 🎓 Campus Connect - Frontend Launcher
echo =====================================
echo.

echo 🚀 Starting Backend API Server...
cd /d "%~dp0backend"
start /B python app.py
timeout /t 3 >nul

echo 🌐 Starting Static File Server...
start /B python static_server.py
timeout /t 3 >nul

echo 📋 Opening Frontend Pages...
echo.

echo 🏠 Opening Login Page...
start http://localhost:8080/simple-login.html

echo 📊 Opening Dashboard...
start http://localhost:8080/dashboard-fixed.html

echo 📚 Opening Course Management...
start http://localhost:8080/courses.html

echo 👥 Opening Student Management...
start http://localhost:8080/frontend/students-enhanced.html

echo 🎨 Opening Workflow Diagrams...
start WORKFLOW-DIAGRAMS.html

echo 📖 Opening Frontend Fix Guide...
start FRONTEND-FIX-GUIDE.md

echo.
echo ✅ Campus Connect Started Successfully!
echo.
echo 🔗 Server Information:
echo    Backend API: http://localhost:5000
echo    Frontend: http://localhost:8080
echo.
echo 🔐 Default Login Credentials:
echo    Admin: admin/admin123
echo    Faculty: faculty/faculty123
echo    Student: student/student123
echo.
echo 🎯 Next Steps:
echo 1. Test login with different user types
echo 2. Check dashboard shows real statistics
echo 3. Test student and course management
echo 4. Verify reports and charts work
echo 5. Test all CRUD operations
echo.
echo 🎉 Your Campus Connect System is now running!
echo.

pause
