# 🎓 Campus Connect - College Management System

A comprehensive, modern College Management System built with Flask (backend) and HTML/CSS/JavaScript (frontend). Features student management, course management, faculty tracking, and real-time analytics with interactive charts.

## 🚀 Features

### 📊 **Dashboard Analytics**
- Real-time statistics and metrics
- Interactive charts and graphs
- Department-wise analytics
- Performance tracking
- Visual data representation

### 👥 **Student Management**
- Complete CRUD operations
- 35+ pre-loaded students across 10 departments
- Performance tracking with marks and attendance
- Department-based filtering
- Data persistence and backup

### 📚 **Course Management**
- 16 courses across multiple departments
- Course scheduling and management
- Student enrollment tracking
- Faculty assignment
- Credit hour management

### 👨‍🏫 **Faculty Management**
- 10 faculty members across all departments
- Department-based assignments
- Course allocation
- Contact information management

### 📈 **Reports & Analytics**
- Comprehensive reporting system
- Visual charts (Canvas-based)
- Department-wise statistics
- Top performing students
- Export and print functionality

### ⚙️ **System Settings**
- User profile management
- System configuration options
- Data management tools
- Export/import functionality
- Backend synchronization

## 🏗️ **Project Structure**

```
Campus-Connect-GitHub/
├── backend/                    # Flask Backend API
│   ├── app.py                 # Main Flask application
│   ├── models.py              # Database models
│   ├── requirements.txt       # Python dependencies
│   ├── routes/                # API routes
│   └── instance/              # Database storage
│       └── database.db        # SQLite database
├── frontend/                   # Frontend assets
│   ├── api.js                 # API service
│   ├── college-api.js         # Enhanced API service
│   ├── students-enhanced.html # Student management
│   └── styles.css             # Styling
├── simple-login.html          # Login page
├── dashboard-fixed.html        # Main dashboard
├── courses.html               # Course management
└── README.md                  # This file
```

## 🗄️ **Backend Data Storage**

The backend uses **SQLite database** located at:
```
backend/instance/database.db
```

### Database Schema:
- **Users**: Authentication and user management
- **Students**: Student records and performance
- **Faculty**: Faculty information and assignments
- **Courses**: Course catalog and scheduling
- **Departments**: Department management

### Data Persistence:
- **Primary**: SQLite database (backend/instance/database.db)
- **Fallback**: localStorage (client-side)
- **Sync**: Automatic synchronization between backend and frontend

## 🛠️ **Installation & Setup**

### Prerequisites:
- Python 3.7+
- pip (Python package manager)
- Modern web browser

### Backend Setup:

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize database:**
   ```bash
   python app.py
   ```
   The database will be automatically created in `backend/instance/database.db`

4. **Start the backend server:**
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000`

### Frontend Setup:

1. **Open the main application:**
   - Open `simple-login.html` in your web browser
   - Or use a live server for better development experience

2. **Default Login Credentials:**
   - **Admin**: `admin/admin123`
   - **Faculty**: `faculty/faculty123`
   - **Student**: `student/student123`

## 🚀 **Deployment Instructions**

### Local Development:
1. Start the backend server (`python app.py`)
2. Open `simple-login.html` in browser
3. Login with any default credentials

### Production Deployment:

#### Option 1: **Heroku Deployment**
1. Create a `Procfile`:
   ```
   web: python app.py
   ```
2. Deploy to Heroku with SQLite support

#### Option 2: **Vercel/Netlify (Frontend) + Railway/Render (Backend)**
1. Deploy frontend to Vercel/Netlify
2. Deploy backend to Railway/Render
3. Update API endpoints in frontend

#### Option 3: **Self-Hosted**
1. Use Apache/Nginx with WSGI
2. Configure SSL certificates
3. Set up reverse proxy

## 📊 **System Overview**

### **Departments (10):**
- Computer Science
- Mathematics
- Physics
- Chemistry
- Biology
- Electrical Engineering
- Mechanical Engineering
- Civil Engineering
- Business Administration
- Economics

### **Sample Data:**
- **35+ Students** with realistic data
- **16 Courses** across departments
- **10 Faculty** members
- **Real performance metrics**

### **Key Features:**
- ✅ Real-time data synchronization
- ✅ Interactive charts and analytics
- ✅ Role-based access control
- ✅ Data persistence and backup
- ✅ Responsive design
- ✅ Export functionality
- ✅ Print-ready reports

## 🔧 **Configuration**

### Backend Configuration:
- Database: SQLite (default)
- Port: 5000 (default)
- Debug mode: Enabled for development

### Frontend Configuration:
- API endpoint: `http://localhost:5000/api`
- Fallback: localStorage
- Refresh interval: 30 seconds

## 📱 **Browser Compatibility**

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

## 🔐 **Security Features**

- Session-based authentication
- Role-based access control
- Input validation
- SQL injection protection
- XSS protection

## 📈 **Performance**

- Optimized database queries
- Client-side caching
- Lazy loading
- Compressed assets
- Efficient chart rendering

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 **API Endpoints**

### Authentication:
- `POST /api/login` - User login
- `POST /api/logout` - User logout

### Students:
- `GET /api/students` - Get all students
- `POST /api/students` - Create student
- `PUT /api/students/:id` - Update student
- `DELETE /api/students/:id` - Delete student

### Similar endpoints for faculty, courses, departments

## 🐛 **Troubleshooting**

### Common Issues:

1. **Backend not connecting:**
   - Check if backend server is running on port 5000
   - Verify firewall settings

2. **Data not persisting:**
   - Check browser localStorage permissions
   - Verify database connectivity

3. **Charts not displaying:**
   - Ensure Canvas API is supported
   - Check browser console for errors

4. **Login issues:**
   - Clear browser cache
   - Verify backend authentication

## 📞 **Support**

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 **Future Enhancements**

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Email notifications
- [ ] File upload capabilities
- [ ] Multi-language support
- [ ] Advanced reporting features

---

**🎓 Campus Connect - Modern College Management System**

*Built with ❤️ using Flask, HTML5, CSS3, and JavaScript*
