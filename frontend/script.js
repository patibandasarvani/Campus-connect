// College Management System - Frontend JavaScript
// Production-ready API integration and UI management

// API Configuration
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// Global State
let currentUser = null;
let students = [];
let isLoading = false;

// DOM Elements
const pages = {
    login: document.querySelector('.login-container'),
    dashboard: null // Will be set when dashboard page is loaded
};

// Utility Functions
function showPage(pageId) {
    // Hide all pages
    Object.values(pages).forEach(page => {
        if (page) page.classList.remove('active');
    });
    
    // Show selected page
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
    }
}

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert ${type}`;
    alert.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(100%)';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function setLoading(element, loading = true) {
    if (loading) {
        element.disabled = true;
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    } else {
        element.disabled = false;
        // Restore original text (you may need to store it)
        if (element.id === 'loginBtn') {
            element.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
        } else if (element.id === 'registerBtn') {
            element.innerHTML = '<i class="fas fa-user-plus"></i> Register';
        }
    }
}

// API Functions
async function apiCall(endpoint, options = {}) {
    try {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'include',
            ...options
        };

        const response = await fetch(url, config);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || `HTTP error! status: ${response.status}`);
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Authentication Functions
async function login(username, password) {
    try {
        const data = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (data.success) {
            currentUser = data.data.user;
            showAlert('Login successful!', 'success');
            showDashboard();
            return true;
        } else {
            showAlert(data.message || 'Login failed', 'error');
            return false;
        }
    } catch (error) {
        showAlert('Login failed: ' + error.message, 'error');
        return false;
    }
}

async function register(userData) {
    try {
        const data = await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });

        if (data.success) {
            showAlert('Registration successful! Please login.', 'success');
            showPage('loginPage');
            return true;
        } else {
            showAlert(data.message || 'Registration failed', 'error');
            return false;
        }
    } catch (error) {
        showAlert('Registration failed: ' + error.message, 'error');
        return false;
    }
}

async function logout() {
    try {
        await apiCall('/auth/logout', { method: 'GET' });
        currentUser = null;
        showAlert('Logged out successfully', 'success');
        showPage('loginPage');
    } catch (error) {
        showAlert('Logout failed: ' + error.message, 'error');
    }
}

// Dashboard Functions
async function showDashboard() {
    showPage('dashboardPage');
    
    if (currentUser) {
        // Update welcome message
        const welcomeMessage = document.getElementById('welcomeMessage');
        const userRole = document.getElementById('userRole');
        
        if (welcomeMessage) {
            welcomeMessage.textContent = `Welcome, ${currentUser.full_name || currentUser.username}!`;
        }
        
        if (userRole) {
            userRole.textContent = `Role: ${currentUser.role.charAt(0).toUpperCase() + currentUser.role.slice(1)}`;
        }
        
        // Load dashboard data based on role
        await loadDashboardData();
        await loadStudents();
    }
}

async function loadDashboardData() {
    try {
        let endpoint = '';
        
        if (currentUser.role === 'admin') {
            endpoint = '/admin/dashboard';
        } else {
            endpoint = '/students/stats';
        }
        
        const data = await apiCall(endpoint);
        
        if (data.success) {
            updateStatsCards(data.data);
            updateQuickActions(currentUser.role);
        }
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

function updateStatsCards(stats) {
    const statsGrid = document.getElementById('statsGrid');
    if (!statsGrid) return;
    
    let statsHTML = '';
    
    if (stats.total_students !== undefined) {
        statsHTML += `
            <div class="stat-card primary">
                <div class="stat-icon">
                    <i class="fas fa-users"></i>
                </div>
                <div class="stat-content">
                    <h3>${stats.total_students}</h3>
                    <p>Total Students</p>
                </div>
            </div>
        `;
    }
    
    if (stats.average_marks !== undefined) {
        statsHTML += `
            <div class="stat-card success">
                <div class="stat-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <div class="stat-content">
                    <h3>${stats.average_marks}</h3>
                    <p>Average Marks</p>
                </div>
            </div>
        `;
    }
    
    if (stats.top_student) {
        statsHTML += `
            <div class="stat-card warning">
                <div class="stat-icon">
                    <i class="fas fa-trophy"></i>
                </div>
                <div class="stat-content">
                    <h3>${stats.top_student.name}</h3>
                    <p>Top Student</p>
                </div>
            </div>
        `;
    }
    
    statsGrid.innerHTML = statsHTML;
}

function updateQuickActions(role) {
    const quickActions = document.getElementById('quickActions');
    if (!quickActions) return;
    
    let actionsHTML = '<h3>Quick Actions</h3><div class="action-buttons">';
    
    if (role === 'admin') {
        actionsHTML += `
            <button class="action-btn primary" onclick="showAddStudentModal()">
                <i class="fas fa-user-plus"></i>
                <span>Add Student</span>
            </button>
            <button class="action-btn success" onclick="showUserManagement()">
                <i class="fas fa-users-cog"></i>
                <span>Manage Users</span>
            </button>
            <button class="action-btn warning" onclick="showReports()">
                <i class="fas fa-chart-bar"></i>
                <span>View Reports</span>
            </button>
        `;
    } else if (role === 'faculty' || role === 'hod') {
        actionsHTML += `
            <button class="action-btn primary" onclick="showAddStudentModal()">
                <i class="fas fa-user-plus"></i>
                <span>Add Student</span>
            </button>
            <button class="action-btn success" onclick="refreshStudents()">
                <i class="fas fa-sync"></i>
                <span>Refresh Data</span>
            </button>
        `;
    } else {
        actionsHTML += `
            <button class="action-btn info" onclick="refreshStudents()">
                <i class="fas fa-sync"></i>
                <span>Refresh</span>
            </button>
        `;
    }
    
    actionsHTML += '</div>';
    quickActions.innerHTML = actionsHTML;
}

// Student Management Functions
async function loadStudents() {
    const loadingState = document.getElementById('studentsLoading');
    const emptyState = document.getElementById('studentsEmpty');
    const tableBody = document.getElementById('studentsTableBody');
    
    if (loadingState) loadingState.style.display = 'block';
    if (emptyState) emptyState.style.display = 'none';
    if (tableBody) tableBody.innerHTML = '';
    
    try {
        const data = await apiCall('/students');
        
        if (data.success) {
            students = data.data.students || [];
            
            if (loadingState) loadingState.style.display = 'none';
            
            if (students.length === 0) {
                if (emptyState) emptyState.style.display = 'block';
            } else {
                renderStudentsTable(students);
            }
        }
    } catch (error) {
        if (loadingState) loadingState.style.display = 'none';
        showAlert('Failed to load students: ' + error.message, 'error');
    }
}

function renderStudentsTable(studentsList) {
    const tableBody = document.getElementById('studentsTableBody');
    if (!tableBody) return;
    
    let tableHTML = '';
    
    studentsList.forEach(student => {
        const performanceClass = getPerformanceClass(student.marks);
        const performanceText = getPerformanceText(student.marks);
        
        tableHTML += `
            <tr>
                <td>${student.id}</td>
                <td>${student.name}</td>
                <td>${student.roll}</td>
                <td>${student.department}</td>
                <td>${student.semester}</td>
                <td>${student.marks}</td>
                <td>
                    <span class="performance-badge ${performanceClass}">${performanceText}</span>
                </td>
                <td>
                    <div class="action-buttons">
                        ${canEditStudent(student) ? `
                            <button class="btn btn-sm btn-primary" onclick="editStudent(${student.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                        ` : ''}
                        ${canDeleteStudent(student) ? `
                            <button class="btn btn-sm btn-danger" onclick="deleteStudent(${student.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = tableHTML;
}

function getPerformanceClass(marks) {
    if (marks >= 80) return 'excellent';
    if (marks >= 60) return 'good';
    if (marks >= 40) return 'average';
    return 'poor';
}

function getPerformanceText(marks) {
    if (marks >= 80) return 'Excellent';
    if (marks >= 60) return 'Good';
    if (marks >= 40) return 'Average';
    return 'Poor';
}

function canEditStudent(student) {
    if (!currentUser) return false;
    if (currentUser.role === 'admin') return true;
    if (currentUser.role === 'faculty') return true;
    return false;
}

function canDeleteStudent(student) {
    if (!currentUser) return false;
    if (currentUser.role === 'admin') return true;
    if (currentUser.role === 'faculty' && student.created_by === currentUser.id) return true;
    return false;
}

async function addStudent(studentData) {
    try {
        const data = await apiCall('/students', {
            method: 'POST',
            body: JSON.stringify(studentData)
        });
        
        if (data.success) {
            showAlert('Student added successfully!', 'success');
            closeStudentModal();
            await loadStudents();
            return true;
        } else {
            showAlert(data.message || 'Failed to add student', 'error');
            return false;
        }
    } catch (error) {
        showAlert('Failed to add student: ' + error.message, 'error');
        return false;
    }
}

async function updateStudent(studentId, studentData) {
    try {
        const data = await apiCall(`/students/${studentId}`, {
            method: 'PUT',
            body: JSON.stringify(studentData)
        });
        
        if (data.success) {
            showAlert('Student updated successfully!', 'success');
            closeStudentModal();
            await loadStudents();
            return true;
        } else {
            showAlert(data.message || 'Failed to update student', 'error');
            return false;
        }
    } catch (error) {
        showAlert('Failed to update student: ' + error.message, 'error');
        return false;
    }
}

async function deleteStudent(studentId) {
    if (!confirm('Are you sure you want to delete this student?')) {
        return;
    }
    
    try {
        const data = await apiCall(`/students/${studentId}`, {
            method: 'DELETE'
        });
        
        if (data.success) {
            showAlert('Student deleted successfully!', 'success');
            await loadStudents();
        } else {
            showAlert(data.message || 'Failed to delete student', 'error');
        }
    } catch (error) {
        showAlert('Failed to delete student: ' + error.message, 'error');
    }
}

// Modal Functions
function showAddStudentModal() {
    const modal = document.getElementById('studentModal');
    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('studentForm');
    
    if (modal) {
        modal.classList.add('active');
        modalTitle.textContent = 'Add Student';
        form.reset();
        document.getElementById('studentId').value = '';
    }
}

function editStudent(studentId) {
    const student = students.find(s => s.id === studentId);
    if (!student) return;
    
    const modal = document.getElementById('studentModal');
    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('studentForm');
    
    if (modal) {
        modal.classList.add('active');
        modalTitle.textContent = 'Edit Student';
        
        // Populate form
        document.getElementById('studentId').value = student.id;
        document.getElementById('studentName').value = student.name;
        document.getElementById('studentRoll').value = student.roll;
        document.getElementById('studentDepartment').value = student.department;
        document.getElementById('studentSemester').value = student.semester;
        document.getElementById('studentMarks').value = student.marks;
        updateMarksDisplay(student.marks);
    }
}

function closeStudentModal() {
    const modal = document.getElementById('studentModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Form Validation and UI Functions
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const toggle = input.nextElementSibling;
    const icon = toggle.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

function updateMarksDisplay(marks) {
    const marksValue = document.getElementById('marksValue');
    if (marksValue) {
        marksValue.textContent = marks;
    }
}

function checkPasswordStrength(password) {
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');
    
    if (!strengthFill || !strengthText) return;
    
    let strength = 0;
    let color = '#dc3545';
    let text = 'Very Weak';
    
    if (password.length >= 6) strength++;
    if (password.length >= 10) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    
    const strengthLevels = ['', 'Very Weak', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
    const strengthColors = ['#dc3545', '#dc3545', '#ffc107', '#ffc107', '#28a745', '#28a745', '#20c997'];
    const strengthWidths = ['0%', '16.66%', '33.33%', '50%', '66.66%', '83.33%', '100%'];
    
    strengthFill.style.width = strengthWidths[strength];
    strengthFill.style.backgroundColor = strengthColors[strength];
    strengthText.textContent = strengthLevels[strength] || 'Password strength';
}

// Search and Filter Functions
function searchStudents() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const departmentFilter = document.getElementById('departmentFilter').value;
    const semesterFilter = document.getElementById('semesterFilter').value;
    
    const filteredStudents = students.filter(student => {
        const matchesSearch = !searchTerm || 
            student.name.toLowerCase().includes(searchTerm) ||
            student.roll.toLowerCase().includes(searchTerm);
        
        const matchesDepartment = !departmentFilter || student.department === departmentFilter;
        const matchesSemester = !semesterFilter || student.semester === semesterFilter;
        
        return matchesSearch && matchesDepartment && matchesSemester;
    });
    
    renderStudentsTable(filteredStudents);
}

function filterStudents() {
    searchStudents();
}

async function refreshStudents() {
    await loadStudents();
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Login Form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('loginUsername').value.trim();
            const password = document.getElementById('loginPassword').value;
            
            if (!username || !password) {
                showAlert('Please enter both username and password', 'error');
                return;
            }
            
            await login(username, password);
        });
    }
    
    // Register Form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                username: document.getElementById('registerUsername').value.trim(),
                password: document.getElementById('registerPassword').value,
                confirm_password: document.getElementById('registerConfirmPassword').value,
                full_name: document.getElementById('registerFullName').value.trim(),
                email: document.getElementById('registerEmail').value.trim(),
                role: document.getElementById('registerRole').value,
                department: document.getElementById('registerDepartment').value
            };
            
            // Validation
            if (!formData.username || !formData.password || !formData.role || !formData.department) {
                showAlert('Please fill in all required fields', 'error');
                return;
            }
            
            if (formData.password !== formData.confirm_password) {
                showAlert('Passwords do not match', 'error');
                return;
            }
            
            if (formData.password.length < 6) {
                showAlert('Password must be at least 6 characters long', 'error');
                return;
            }
            
            await register(formData);
        });
    }
    
    // Password Strength Checker
    const registerPassword = document.getElementById('registerPassword');
    if (registerPassword) {
        registerPassword.addEventListener('input', function() {
            checkPasswordStrength(this.value);
        });
    }
    
    // Student Form
    const studentForm = document.getElementById('studentForm');
    if (studentForm) {
        studentForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const studentId = document.getElementById('studentId').value;
            const formData = {
                name: document.getElementById('studentName').value.trim(),
                roll: document.getElementById('studentRoll').value.trim(),
                department: document.getElementById('studentDepartment').value,
                semester: document.getElementById('studentSemester').value,
                marks: parseInt(document.getElementById('studentMarks').value)
            };
            
            // Validation
            if (!formData.name || !formData.roll || !formData.department) {
                showAlert('Please fill in all required fields', 'error');
                return;
            }
            
            if (isNaN(formData.marks) || formData.marks < 0 || formData.marks > 100) {
                showAlert('Marks must be between 0 and 100', 'error');
                return;
            }
            
            if (studentId) {
                await updateStudent(studentId, formData);
            } else {
                await addStudent(formData);
            }
        });
    }
    
    // Marks Input
    const studentMarks = document.getElementById('studentMarks');
    if (studentMarks) {
        studentMarks.addEventListener('input', function() {
            updateMarksDisplay(this.value);
        });
    }
    
    // Modal Close on Outside Click
    const studentModal = document.getElementById('studentModal');
    if (studentModal) {
        studentModal.addEventListener('click', function(e) {
            if (e.target === studentModal) {
                closeStudentModal();
            }
        });
    }
    
    // Check authentication on page load
    checkAuthentication();
});

// Check if user is already authenticated
async function checkAuthentication() {
    try {
        const data = await apiCall('/auth/check');
        if (data.success) {
            currentUser = data.data.user;
            showDashboard();
        }
    } catch (error) {
        // User is not authenticated, show login page
        showPage('loginPage');
    }
}

// Placeholder functions for future features
function showUserManagement() {
    showAlert('User management feature coming soon!', 'info');
}

function showReports() {
    showAlert('Reports feature coming soon!', 'info');
}

// Export functions for global use
window.CollegeManagement = {
    showAlert,
    login,
    register,
    logout,
    loadStudents,
    showAddStudentModal,
    editStudent,
    deleteStudent,
    searchStudents,
    filterStudents,
    refreshStudents
};
