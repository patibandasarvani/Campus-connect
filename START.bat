@echo off
echo 🎓 Starting Campus Connect College Management System...
echo.

echo 📋 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.7+ first.
    echo 📥 Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found!
echo.

echo 📦 Installing dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies!
    pause
    exit /b 1
)

echo ✅ Dependencies installed!
echo.

echo 🗄️ Initializing database...
python app.py >nul 2>&1
timeout /t 2 >nul

echo ✅ Database initialized!
echo.

echo 🚀 Starting backend server...
echo 📍 Backend will be available at: http://localhost:5000
echo 📍 Open frontend at: http://localhost:5000/simple-login.html
echo.
echo 🔐 Default Login Credentials:
echo    Admin: admin/admin123
echo    Faculty: faculty/faculty123
echo    Student: student/student123
echo.
echo 🌐 Opening browser...
start http://localhost:5000/simple-login.html

python app.py
