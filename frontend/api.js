// API Service for Campus Connect
class CampusAPI {
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

    // Check authentication status
    isAuthenticated() {
        return this.authenticated || !!localStorage.getItem('currentUser');
    }

    // Get current user
    getCurrentUser() {
        return JSON.parse(localStorage.getItem('currentUser') || '{}');
    }
}

// Initialize API instance
const api = new CampusAPI();
