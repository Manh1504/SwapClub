// DOM Elements
const authTabs = document.querySelectorAll('.auth-tab');
const authForms = document.querySelectorAll('.auth-form');
const togglePasswordButtons = document.querySelectorAll('.toggle-password');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');

// Initialize the auth page
function init() {
    setupEventListeners();
}

// Setup event listeners
function setupEventListeners() {
    // Auth tabs
    authTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and forms
            authTabs.forEach(t => t.classList.remove('active'));
            authForms.forEach(f => f.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding form
            tab.classList.add('active');
            const targetForm = document.getElementById(tab.dataset.target);
            if (targetForm) {
                targetForm.classList.add('active');
            }
        });
    });    
    // Toggle password visibility
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', () => {
            const passwordInput = button.parentElement.querySelector('input');
            const icon = button.querySelector('i');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
    
    // Login form submission
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const rememberMe = document.getElementById('remember-me').checked;
        
        // Validate form
        if (!email || !password) {
            alert('Vui lòng điền đầy đủ thông tin đăng nhập.');
            return;
        }

    });

    
    // Register form submission
    registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const name = document.getElementById('register-name').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('register-confirm-password').value;
        const agreeTerms = document.getElementById('agree-terms').checked;
        
        // Validate form
        if (!name || !email || !password || !confirmPassword) {
            alert('Vui lòng điền đầy đủ thông tin đăng ký.');
            return;
        }
        
        if (password !== confirmPassword) {
            alert('Mật khẩu xác nhận không khớp.');
            return;
        }
    });
}

    // Hàm đăng nhập tài khoản
const login = async (username, password) => {
  try {
    const response = await fetch('/api/users/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error('Đăng nhập thất bại');
    }

    const data = await response.json();
    window.location.href = '/api/posts'; // Chuyển hướng đến trang chính sau khi đăng nhập thành công
    
    // Lưu token vào localStorage nếu có
    if (data.token) {
      localStorage.setItem('token', data.token);
      localStorage.setItem('username', username);
    }
    
    return {
      success: true,
      data: data
    };
  } catch (error) {
    console.error('Lỗi:', error.message);
    return {
      success: false,
      message: error.message
    };
  }
};

// Hàm đăng xuất
// function logout() {
//   localStorage.removeItem('token');
//   localStorage.removeItem('username');
//   window.location.href = '/login'; // Chuyển hướng đến trang đăng nhập
//   return { success: false };
// }

// Hàm kiểm tra đã đăng nhập chưa
const isLoggedIn = () => {
  return localStorage.getItem('token') !== null;
};

// Hàm đăng ký tài khoản
const register = async (userData) => {
  try {
    const response = await fetch('/api/users/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error('Đăng ký thất bại');
    }

    const data = await response.json();
    localStorage.setItem('token', data.token);
    localStorage.setItem('username', userData.username);
    window.location.href = '/api/posts'; // Chuyển hướng đến trang chính sau khi đăng ký thành công
    
    return {
      success: true,
      data: data
    };
  } catch (error) {
    console.error('Lỗi:', error.message);
    return {
      success: false,
      message: error.message
    };
  }
};



