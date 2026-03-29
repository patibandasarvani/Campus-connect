#!/bin/bash

echo "🎓 Starting Campus Connect College Management System..."
echo

echo "📋 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.7+ first."
    echo "📥 Download from: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python3 found!"
echo

echo "📦 Installing dependencies..."
cd backend
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies!"
    exit 1
fi

echo "✅ Dependencies installed!"
echo

echo "🗄️ Initializing database..."
python3 app.py > /dev/null 2>&1 &
sleep 2

echo "✅ Database initialized!"
echo

echo "🚀 Starting backend server..."
echo "📍 Backend will be available at: http://localhost:5000"
echo "📍 Open frontend at: http://localhost:5000/simple-login.html"
echo
echo "🔐 Default Login Credentials:"
echo "   Admin: admin/admin123"
echo "   Faculty: faculty/faculty123"
echo "   Student: student/student123"
echo
echo "🌐 Opening browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5000/simple-login.html
elif command -v open &> /dev/null; then
    open http://localhost:5000/simple-login.html
else
    echo "Please open: http://localhost:5000/simple-login.html"
fi

python3 app.py
