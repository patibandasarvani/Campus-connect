# 🚀 Deployment Guide - Campus Connect

## 📋 **Deployment Checklist**

### ✅ **Pre-Deployment Checks**
- [ ] Backend server runs successfully on port 5000
- [ ] Database is properly initialized
- [ ] All frontend pages load correctly
- [ ] Login functionality works
- [ ] Data persistence is working
- [ ] Charts and analytics display properly
- [ ] All navigation links work
- [ ] Export/import functions work

---

## 🌐 **Deployment Options**

### **Option 1: GitHub Pages (Frontend Only)**

#### **Steps:**
1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/Campus-Connect.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**
   - Go to repository settings
   - Scroll to "GitHub Pages"
   - Source: Deploy from a branch
   - Branch: main
   - Folder: /root
   - Save

3. **Update API Endpoint**
   - Edit `frontend/college-api.js`
   - Change base URL to your backend URL

#### **Limitations:**
- Frontend only (no backend)
- No database persistence
- Read-only mode

---

### **Option 2: Vercel (Frontend) + Railway (Backend)**

#### **Frontend Deployment (Vercel):**

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy to Vercel**
   ```bash
   vercel --prod
   ```

3. **Configure vercel.json**
   ```json
   {
     "rewrites": [
       { "source": "/api/(.*)", "destination": "https://your-backend-url.railway.app/api/$1" }
     ]
   }
   ```

#### **Backend Deployment (Railway):**

1. **Create Railway Account**
   - Sign up at railway.app
   - Connect GitHub repository

2. **Configure Railway**
   - Add environment variables
   - Set port to 5000
   - Deploy automatically

3. **Update Frontend API URL**
   - Edit frontend files to use Railway URL

---

### **Option 3: Heroku (Full Stack)**

#### **Backend Setup:**

1. **Create Procfile**
   ```text
   web: python app.py
   ```

2. **Create requirements.txt**
   ```text
   Flask==2.3.0
   Flask-SQLAlchemy==3.0.5
   Flask-CORS==4.0.0
   python-dotenv==1.0.0
   ```

3. **Deploy to Heroku**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

#### **Frontend Setup:**
- Upload frontend files to Heroku static folder
- Or use CDN for frontend

---

### **Option 4: Self-Hosted (VPS/Dedicated Server)**

#### **Server Requirements:**
- Ubuntu 20.04+ / CentOS 8+
- 2GB+ RAM
- 20GB+ Storage
- Python 3.7+

#### **Installation Steps:**

1. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx
   ```

2. **Setup Application**
   ```bash
   git clone https://github.com/yourusername/Campus-Connect.git
   cd Campus-Connect/backend
   pip3 install -r requirements.txt
   ```

3. **Configure Gunicorn**
   ```bash
   pip3 install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Setup Nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           root /path/to/Campus-Connect;
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## 🔧 **Configuration Files**

### **.env (Backend)**
```env
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/database.db
```

### **package.json (Frontend)**
```json
{
  "name": "campus-connect",
  "version": "1.0.0",
  "scripts": {
    "start": "python -m http.server 8000"
  }
}
```

### **vercel.json**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/backend/app.py"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
```

---

## 🗄️ **Database Setup**

### **SQLite (Default)**
- Location: `backend/instance/database.db`
- Auto-created on first run
- No additional setup required

### **PostgreSQL (Production)**
1. **Install PostgreSQL**
   ```bash
   sudo apt install postgresql postgresql-contrib
   ```

2. **Create Database**
   ```sql
   CREATE DATABASE campus_connect;
   CREATE USER campus_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE campus_connect TO campus_user;
   ```

3. **Update Models**
   ```python
   # In models.py
   DATABASE_URL = 'postgresql://campus_user:your_password@localhost/campus_connect'
   ```

---

## 🔐 **Security Configuration**

### **Environment Variables**
```env
SECRET_KEY=your-very-secret-key-here
FLASK_ENV=production
DATABASE_URL=your-database-url
CORS_ORIGINS=https://yourdomain.com
```

### **HTTPS Setup**
1. **Install Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Get SSL Certificate**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

---

## 📊 **Performance Optimization**

### **Backend Optimization**
- Use connection pooling
- Implement caching
- Optimize database queries
- Use WSGI server (Gunicorn/uWSGI)

### **Frontend Optimization**
- Minify CSS/JS
- Use CDN for static assets
- Implement lazy loading
- Optimize images

---

## 🔍 **Testing Before Deployment**

### **Automated Tests**
```bash
# Backend tests
python -m pytest tests/

# Frontend tests
npm test
```

### **Manual Testing Checklist**
- [ ] Login works for all user types
- [ ] Dashboard loads with real data
- [ ] Student management functions
- [ ] Course management functions
- [ ] Reports generate correctly
- [ ] Charts display properly
- [ ] Data persists across refresh
- [ ] Export functions work
- [ ] Mobile responsive design

---

## 🚨 **Common Deployment Issues**

### **Issue: Backend Not Connecting**
**Solution:**
- Check if port 5000 is open
- Verify firewall settings
- Check backend logs

### **Issue: Database Not Found**
**Solution:**
- Ensure database file exists
- Check file permissions
- Verify database path

### **Issue: CORS Errors**
**Solution:**
- Configure CORS origins
- Update API endpoints
- Check proxy settings

### **Issue: Charts Not Displaying**
**Solution:**
- Ensure Canvas API support
- Check browser compatibility
- Verify data loading

---

## 📱 **Mobile Optimization**

### **Responsive Design**
- Meta viewport tag
- Flexible grid layout
- Touch-friendly interface
- Optimized charts for mobile

### **Performance**
- Compressed images
- Minified assets
- Lazy loading
- Service worker (PWA)

---

## 🔄 **CI/CD Pipeline**

### **GitHub Actions**
```yaml
name: Deploy
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to production
      run: echo "Deploying..."
```

---

## 📞 **Support**

### **Monitoring**
- Set up application monitoring
- Error tracking (Sentry)
- Performance monitoring
- Uptime monitoring

### **Backup Strategy**
- Database backups
- File system backups
- Git repository backup
- Disaster recovery plan

---

## 🎯 **Post-Deployment**

### **Verification Steps**
1. Test all user flows
2. Verify data persistence
3. Check performance
4. Test mobile responsiveness
5. Validate security measures

### **Maintenance**
- Regular updates
- Security patches
- Performance monitoring
- User feedback collection

---

**🚀 Ready for Deployment!**

Follow this guide to deploy Campus Connect to your preferred platform. Choose the option that best fits your requirements and budget.
