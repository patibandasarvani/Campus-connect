@echo off
echo 🚀 QUICK VERCEL DEPLOYMENT
echo ========================
echo.

echo 📋 Step 1: Check if Vercel is installed
vercel --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Vercel not installed. Installing...
    npm install -g vercel
)

echo 📋 Step 2: Go to project folder
cd /d "%~dp0"
echo ✅ Current directory: %CD%

echo 📋 Step 3: Deploy to Vercel
echo 🌐 Deploying to: https://campus-connect.vercel.app
echo.

vercel --prod

echo.
echo ✅ Deployment complete!
echo 🌐 Check: https://campus-connect.vercel.app
pause
