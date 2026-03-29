@echo off
echo 🚀 Deploying Campus Connect to Vercel...
echo =====================================
echo.

echo 📋 Checking prerequisites...
where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js/npm not found. Please install Node.js first.
    echo 📥 Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js/npm found
echo.

echo 📦 Installing Vercel CLI...
npm install -g vercel
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install Vercel CLI
    pause
    exit /b 1
)

echo ✅ Vercel CLI installed
echo.

echo 🔐 Logging into Vercel...
echo 📋 This will open your browser to login to Vercel
echo 📋 Please connect your GitHub account
echo.
pause

vercel login
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to login to Vercel
    pause
    exit /b 1
)

echo ✅ Successfully logged into Vercel
echo.

echo 🚀 Deploying to Vercel...
echo 📋 This will deploy your Campus Connect application
echo 📋 Your app will be available at: https://campus-connect.vercel.app
echo.
pause

vercel --prod
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Deployment failed
    pause
    exit /b 1
)

echo ✅ Successfully deployed to Vercel!
echo.
echo 🌐 Your application is now live at:
echo    https://campus-connect.vercel.app
echo.
echo 🎯 Features available:
echo    ✅ 200 students with sequential IDs
echo    ✅ Complete student management
echo    ✅ Course management system
echo    ✅ Dashboard with analytics
echo    ✅ Mobile responsive design
echo    ✅ HTTPS and global CDN
echo.
echo 📋 Test your deployment:
echo    1. Open https://campus-connect.vercel.app
echo    2. Login with admin/admin123
echo    3. Check dashboard shows 200 students
echo    4. Test student management features
echo.
echo 🎉 Your Campus Connect is now live on Vercel!
echo.

pause
