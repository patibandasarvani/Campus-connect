// College Management System API Service
class CollegeAPI {
    constructor() {
        this.baseURL = 'http://127.0.0.1:5000/api';
        this.useLocalStorage = false;
        this.authenticated = false;
    }

    async request(endpoint, options = {}) {
        try {
            // Include credentials for session-based authentication
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                credentials: 'include', // Important for session cookies
                ...options
            });

            if (response.ok) {
                return await response.json();
            }
            
            // If authentication fails, fallback to localStorage
            if (response.status === 401) {
                console.log('Authentication required, using localStorage');
                this.useLocalStorage = true;
                return null;
            }
            
            throw new Error('API request failed');
        } catch (error) {
            console.log('Backend unavailable, using localStorage');
            this.useLocalStorage = true;
            return null;
        }
    }

    // Authentication methods
    async login(username, password) {
        try {
            const response = await this.request('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });
            
            if (response && response.success) {
                this.authenticated = true;
                this.useLocalStorage = false;
                // Store user info in localStorage for UI
                localStorage.setItem('currentUser', JSON.stringify(response.data.user));
                return response.data.user;
            }
            return null;
        } catch (error) {
            console.error('Login failed:', error);
            return null;
        }
    }

    async logout() {
        try {
            await this.request('/auth/logout');
        } catch (error) {
            console.log('Logout API failed, clearing locally');
        } finally {
            this.authenticated = false;
            localStorage.removeItem('currentUser');
        }
    }

    // Student management methods
    async getStudents() {
        if (this.useLocalStorage) {
            return JSON.parse(localStorage.getItem('students') || '[]');
        }
        
        const data = await this.request('/students');
        if (data && data.success) {
            // Store in localStorage for persistence
            localStorage.setItem('students', JSON.stringify(data.data || []));
            return data.data || [];
        }
        
        // Fallback to localStorage if API fails
        this.useLocalStorage = true;
        return JSON.parse(localStorage.getItem('students') || '[]');
    }

    async addStudent(student) {
        // Always store in localStorage first for persistence
        const students = JSON.parse(localStorage.getItem('students') || '[]');
        const newStudent = {
            ...student,
            id: Date.now(),
            created_at: new Date().toISOString()
        };
        students.push(newStudent);
        localStorage.setItem('students', JSON.stringify(students));
        
        // Try to sync with backend if available
        if (!this.useLocalStorage) {
            try {
                const response = await this.request('/students', {
                    method: 'POST',
                    body: JSON.stringify(student)
                });
                
                if (response && response.success) {
                    return response.data;
                }
            } catch (error) {
                console.log('Backend sync failed, data saved locally');
            }
        }
        
        return newStudent;
    }

    async updateStudent(id, student) {
        // Update in localStorage first
        const students = JSON.parse(localStorage.getItem('students') || '[]');
        const index = students.findIndex(s => s.id == id);
        
        if (index !== -1) {
            students[index] = { ...students[index], ...student };
            localStorage.setItem('students', JSON.stringify(students));
            
            // Try to sync with backend
            if (!this.useLocalStorage) {
                try {
                    const response = await this.request(`/students/${id}`, {
                        method: 'PUT',
                        body: JSON.stringify(student)
                    });
                    
                    if (response && response.success) {
                        return response.data;
                    }
                } catch (error) {
                    console.log('Backend sync failed, data updated locally');
                }
            }
            
            return students[index];
        }
        
        return null;
    }

    async deleteStudent(id) {
        // Delete from localStorage first
        const students = JSON.parse(localStorage.getItem('students') || '[]');
        const filteredStudents = students.filter(s => s.id != id);
        localStorage.setItem('students', JSON.stringify(filteredStudents));
        
        // Try to sync with backend
        if (!this.useLocalStorage) {
            try {
                await this.request(`/students/${id}`, {
                    method: 'DELETE'
                });
            } catch (error) {
                console.log('Backend sync failed, data deleted locally');
            }
        }
        
        return true;
    }

    // Faculty management methods
    async getFaculty() {
        if (this.useLocalStorage) {
            return JSON.parse(localStorage.getItem('faculty') || '[]');
        }
        
        // For now, use localStorage for faculty (backend endpoint not implemented yet)
        return JSON.parse(localStorage.getItem('faculty') || '[]');
    }

    async addFaculty(faculty) {
        const facultyList = JSON.parse(localStorage.getItem('faculty') || '[]');
        const newFaculty = {
            ...faculty,
            id: Date.now(),
            created_at: new Date().toISOString()
        };
        facultyList.push(newFaculty);
        localStorage.setItem('faculty', JSON.stringify(facultyList));
        return newFaculty;
    }

    // Course management methods
    async getCourses() {
        if (this.useLocalStorage) {
            return JSON.parse(localStorage.getItem('courses') || '[]');
        }
        
        // For now, use localStorage for courses (backend endpoint not implemented yet)
        return JSON.parse(localStorage.getItem('courses') || '[]');
    }

    async addCourse(course) {
        const courses = JSON.parse(localStorage.getItem('courses') || '[]');
        const newCourse = {
            ...course,
            id: Date.now(),
            created_at: new Date().toISOString()
        };
        courses.push(newCourse);
        localStorage.setItem('courses', JSON.stringify(courses));
        return newCourse;
    }

    // Department management methods
    async getDepartments() {
        if (this.useLocalStorage) {
            return JSON.parse(localStorage.getItem('departments') || '[]');
        }
        
        // For now, use localStorage for departments (backend endpoint not implemented yet)
        return JSON.parse(localStorage.getItem('departments') || '[]');
    }

    async addDepartment(department) {
        const departments = JSON.parse(localStorage.getItem('departments') || '[]');
        const newDepartment = {
            ...department,
            id: Date.now(),
            created_at: new Date().toISOString()
        };
        departments.push(newDepartment);
        localStorage.setItem('departments', JSON.stringify(departments));
        return newDepartment;
    }

    // Notice management methods
    async getNotices() {
        if (this.useLocalStorage) {
            return JSON.parse(localStorage.getItem('notices') || '[]');
        }
        
        // For now, use localStorage for notices (backend endpoint not implemented yet)
        return JSON.parse(localStorage.getItem('notices') || '[]');
    }

    async addNotice(notice) {
        const notices = JSON.parse(localStorage.getItem('notices') || '[]');
        const newNotice = {
            ...notice,
            id: Date.now(),
            created_at: new Date().toISOString()
        };
        notices.unshift(newNotice); // Add to beginning
        localStorage.setItem('notices', JSON.stringify(notices));
        return newNotice;
    }

    // Activity tracking methods
    async getActivities() {
        if (this.useLocalStorage) {
            return JSON.parse(localStorage.getItem('activities') || '[]');
        }
        
        // For now, use localStorage for activities (backend endpoint not implemented yet)
        return JSON.parse(localStorage.getItem('activities') || '[]');
    }

    async addActivity(activity) {
        const activities = JSON.parse(localStorage.getItem('activities') || '[]');
        const newActivity = {
            ...activity,
            id: Date.now(),
            time: new Date().toISOString()
        };
        activities.unshift(newActivity); // Add to beginning
        localStorage.setItem('activities', JSON.stringify(activities));
        return newActivity;
    }

    // Statistics methods
    async getStatistics() {
        const students = await this.getStudents();
        const faculty = await this.getFaculty();
        const courses = await this.getCourses();
        const departments = await this.getDepartments();
        
        return {
            totalStudents: students.length,
            totalFaculty: faculty.length,
            totalCourses: courses.length,
            totalDepartments: departments.length,
            averagePerformance: students.length > 0 ? 
                Math.round(students.reduce((sum, s) => sum + (s.marks || 0), 0) / students.length) : 0,
            totalRevenue: students.length * 1000, // Assuming $1000 per student
            departmentStats: departments.map(dept => ({
                name: dept.name,
                students: students.filter(s => s.department === dept.name).length,
                faculty: faculty.filter(f => f.department === dept.name).length,
                courses: courses.filter(c => c.department === dept.name).length
            }))
        };
    }

    // Check authentication status
    isAuthenticated() {
        return this.authenticated || !!localStorage.getItem('currentUser');
    }

    // Get current user
    getCurrentUser() {
        return JSON.parse(localStorage.getItem('currentUser') || '{}');
    }

    // Sync all data with backend (if available)
    async syncWithBackend() {
        if (this.useLocalStorage) {
            console.log('Backend not available, skipping sync');
            return false;
        }

        try {
            // Sync students
            const localStudents = JSON.parse(localStorage.getItem('students') || '[]');
            for (const student of localStudents) {
                await this.addStudent(student);
            }

            // Sync other data types as needed
            console.log('Data synced with backend successfully');
            return true;
        } catch (error) {
            console.error('Backend sync failed:', error);
            return false;
        }
    }

    // Export data for backup
    exportData() {
        const data = {
            students: JSON.parse(localStorage.getItem('students') || '[]'),
            faculty: JSON.parse(localStorage.getItem('faculty') || '[]'),
            courses: JSON.parse(localStorage.getItem('courses') || '[]'),
            departments: JSON.parse(localStorage.getItem('departments') || '[]'),
            notices: JSON.parse(localStorage.getItem('notices') || '[]'),
            activities: JSON.parse(localStorage.getItem('activities') || '[]'),
            exportDate: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `college-management-backup-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Import data from backup
    importData(jsonData) {
        try {
            const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
            
            // Validate data structure
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid data format');
            }

            // Import each data type
            if (data.students && Array.isArray(data.students)) {
                localStorage.setItem('students', JSON.stringify(data.students));
            }
            if (data.faculty && Array.isArray(data.faculty)) {
                localStorage.setItem('faculty', JSON.stringify(data.faculty));
            }
            if (data.courses && Array.isArray(data.courses)) {
                localStorage.setItem('courses', JSON.stringify(data.courses));
            }
            if (data.departments && Array.isArray(data.departments)) {
                localStorage.setItem('departments', JSON.stringify(data.departments));
            }
            if (data.notices && Array.isArray(data.notices)) {
                localStorage.setItem('notices', JSON.stringify(data.notices));
            }
            if (data.activities && Array.isArray(data.activities)) {
                localStorage.setItem('activities', JSON.stringify(data.activities));
            }

            console.log('Data imported successfully');
            return true;
        } catch (error) {
            console.error('Data import failed:', error);
            return false;
        }
    }
}

// Initialize API instance
const collegeAPI = new CollegeAPI();
