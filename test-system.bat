@echo off
echo 🔍 Campus Connect - System Check
echo =====================================
echo.

echo 📋 Step 1: Checking Backend Server...
cd backend
python app.py > nul 2>&1
timeout /t 3 > nul

curl -s http://localhost:5000/health > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend server is running!
) else (
    echo ❌ Backend server is not running!
    echo 🚀 Starting backend server...
    start /B python app.py
    timeout /t 5 > nul
)

echo.
echo 📋 Step 2: Checking Database...
if exist "instance\database.db" (
    echo ✅ Database file exists!
    for %%F in ("instance\database.db") do echo 📊 Database size: %%~zF bytes
) else (
    echo ❌ Database file not found!
    echo 🗄️ Creating database...
    python app.py
    timeout /t 3 > nul
)

echo.
echo 📋 Step 3: Testing API Endpoints...
curl -s http://localhost:5000/health > temp_health.txt 2>nul
findstr "OK" temp_health.txt > nul
if %errorlevel% equ 0 (
    echo ✅ Health check endpoint working!
) else (
    echo ❌ Health check endpoint failed!
)

curl -s http://localhost:5000/api/students > temp_students.txt 2>nul
findstr "[" temp_students.txt > nul
if %errorlevel% equ 0 (
    echo ✅ Students API endpoint working!
) else (
    echo ❌ Students API endpoint failed!
)

echo.
echo 📋 Step 4: Opening Test Pages...
echo 🌐 Opening login page...
start http://localhost:5000/simple-login.html

echo 🌐 Opening system check list...
start SYSTEM-CHECK-LIST.md

echo.
echo 📋 Step 5: Quick Test Summary...
echo.
echo 🔧 What to test manually:
echo 1. Login with admin/admin123
echo 2. Check dashboard shows real numbers (not zeros)
echo 3. Click "View Reports" - should show charts
echo 4. Click "Settings" - should show analytics
echo 5. Go to student management - should show 35+ students
echo 6. Add/edit/delete a student
echo 7. Refresh page - data should persist
echo.

echo 🎯 Expected Results:
echo - Total Students: 35+
echo - Total Faculty: 10
echo - Total Courses: 16
echo - Total Departments: 10
echo.

echo 🚀 System check complete!
echo 📖 Follow SYSTEM-CHECK-LIST.md for detailed testing
echo.

pause

REM Cleanup
del temp_health.txt 2>nul
del temp_students.txt 2>nul
