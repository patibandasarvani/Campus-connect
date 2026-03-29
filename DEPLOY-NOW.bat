@echo off
echo 🚀 DEPLOYING CAMPUS CONNECT TO VERCEL
echo =====================================
echo.

echo 📋 Step 1: Navigate to project directory
cd /d "C:\Users\P SARAVANI\CascadeProjects\Campus-Connect-GitHub\connect up"
echo ✅ Project directory: %CD%
echo.

echo 📋 Step 2: Check Vercel CLI
vercel --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Vercel CLI not found. Installing...
    npm install -g vercel
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install Vercel CLI
        pause
        exit /b 1
    )
)
echo ✅ Vercel CLI ready
echo.

echo 📋 Step 3: Check login status
vercel whoami
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Not logged in. Please login...
    vercel login
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to login to Vercel
        pause
        exit /b 1
    )
)
echo ✅ Logged in to Vercel
echo.

echo 📋 Step 4: Deploy to Vercel
echo 🌐 Your app will be deployed to: https://campus-connect.vercel.app
echo 📱 Frontend pages will work (200 students included)
echo ⚠️  Note: Backend API will be static (no database)
echo.
echo 🚀 Starting deployment...
echo.

vercel --prod
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Deployment failed
    pause
    exit /b 1
)

echo.
echo ✅ DEPLOYMENT SUCCESSFUL!
echo.
echo 🌐 Your application is now live at:
echo    https://campus-connect.vercel.app
echo.
echo 📱 Access pages:
echo    Login: https://campus-connect.vercel.app/simple-login.html
echo    Dashboard: https://campus-connect.vercel.app/dashboard-fixed.html
echo    Students: https://campus-connect.vercel.app/frontend/students-enhanced.html
echo    Courses: https://campus-connect.vercel.app/courses.html
echo.
echo 🎯 Features available:
echo    ✅ 200 students with sequential IDs
echo    ✅ Student management interface
echo    ✅ Course management system
echo    ✅ Dashboard with charts
echo    ✅ Mobile responsive design
echo    ✅ HTTPS security
echo    ✅ Global CDN
echo.
echo 🎉 Your Campus Connect is now LIVE on Vercel!
echo.

pause
