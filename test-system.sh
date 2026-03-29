#!/bin/bash

echo "🔍 Campus Connect - System Check"
echo "====================================="
echo

echo "📋 Step 1: Checking Backend Server..."
cd backend
python3 app.py > /dev/null 2>&1 &
sleep 3

if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Backend server is running!"
else
    echo "❌ Backend server is not running!"
    echo "🚀 Starting backend server..."
    python3 app.py > /dev/null 2>&1 &
    sleep 5
fi

echo
echo "📋 Step 2: Checking Database..."
if [ -f "instance/database.db" ]; then
    echo "✅ Database file exists!"
    echo "📊 Database size: $(stat -f%z instance/database.db) bytes"
else
    echo "❌ Database file not found!"
    echo "🗄️ Creating database..."
    python3 app.py
    sleep 3
fi

echo
echo "📋 Step 3: Testing API Endpoints..."
if curl -s http://localhost:5000/health | grep -q "OK"; then
    echo "✅ Health check endpoint working!"
else
    echo "❌ Health check endpoint failed!"
fi

if curl -s http://localhost:5000/api/students | grep -q "\["; then
    echo "✅ Students API endpoint working!"
else
    echo "❌ Students API endpoint failed!"
fi

echo
echo "📋 Step 4: Opening Test Pages..."
echo "🌐 Opening login page..."
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5000/simple-login.html
elif command -v open > /dev/null; then
    open http://localhost:5000/simple-login.html
else
    echo "Please open: http://localhost:5000/simple-login.html"
fi

echo "🌐 Opening system check list..."
if command -v xdg-open > /dev/null; then
    xdg-open SYSTEM-CHECK-LIST.md
elif command -v open > /dev/null; then
    open SYSTEM-CHECK-LIST.md
else
    echo "Please open: SYSTEM-CHECK-LIST.md"
fi

echo
echo "📋 Step 5: Quick Test Summary..."
echo
echo "🔧 What to test manually:"
echo "1. Login with admin/admin123"
echo "2. Check dashboard shows real numbers (not zeros)"
echo "3. Click 'View Reports' - should show charts"
echo "4. Click 'Settings' - should show analytics"
echo "5. Go to student management - should show 35+ students"
echo "6. Add/edit/delete a student"
echo "7. Refresh page - data should persist"
echo
echo "🎯 Expected Results:"
echo "- Total Students: 35+"
echo "- Total Faculty: 10"
echo "- Total Courses: 16"
echo "- Total Departments: 10"
echo
echo "🚀 System check complete!"
echo "📖 Follow SYSTEM-CHECK-LIST.md for detailed testing"
echo

read -p "Press Enter to continue..."
