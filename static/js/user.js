// Sample data for purchase history
const purchaseHistory = [
    {
        id: 1,
        title: "Sách Giáo Khoa Toán Lớp 10",
        image: "https://via.placeholder.com/80",
        seller: "Nguyễn Văn B",
        price: "50.000đ",
        date: "15/04/2023",
        status: "completed"
    },
    {
        id: 2,
        title: "Bộ Dụng Cụ Vẽ Kỹ Thuật",
        image: "https://via.placeholder.com/80",
        seller: "Trần Thị C",
        price: "120.000đ",
        date: "02/05/2023",
        status: "completed"
    },
    {
        id: 3,
        title: "Máy Tính Casio FX-570VN Plus",
        image: "https://via.placeholder.com/80",
        seller: "Lê Văn D",
        price: "200.000đ",
        date: "18/05/2023",
        status: "processing"
    },
    {
        id: 4,
        title: "Balo Học Sinh",
        image: "https://via.placeholder.com/80",
        seller: "Phạm Thị E",
        price: "150.000đ",
        date: "10/06/2023",
        status: "cancelled"
    },
    {
        id: 5,
        title: "Bộ Sách Tham Khảo Lớp 12",
        image: "https://via.placeholder.com/80",
        seller: "Hoàng Văn F",
        price: "350.000đ",
        date: "22/06/2023",
        status: "completed"
    }
];

// DOM Elements
const profileTabs = document.querySelectorAll('.profile-tab');
const tabContents = document.querySelectorAll('.tab-content');
const purchaseList = document.querySelector('.purchase-list');
const purchaseStatusFilter = document.getElementById('purchase-status');
const purchaseDateFilter = document.getElementById('purchase-date');
const editProfileBtn = document.querySelector('.edit-profile-btn');
const editProfileModal = document.getElementById('edit-profile-modal');
const closeModalBtn = document.querySelector('.close-modal');
const cancelEditBtn = document.querySelector('.cancel-edit');
const editProfileForm = document.getElementById('edit-profile-form');

// Initialize the profile page
function init() {
    renderPurchaseHistory();
    setupEventListeners();
}

// Render purchase history
function renderPurchaseHistory(statusFilter = 'all') {
    purchaseList.innerHTML = '';
    
    const filteredHistory = statusFilter === 'all' 
        ? purchaseHistory 
        : purchaseHistory.filter(item => item.status === statusFilter);
    
    if (filteredHistory.length === 0) {
        purchaseList.innerHTML = '<p class="placeholder-text">Không có giao dịch nào phù hợp với bộ lọc.</p>';
        return;
    }
    
    filteredHistory.forEach(purchase => {
        const statusText = getStatusText(purchase.status);
        const statusClass = `status-${purchase.status}`;
        
        const purchaseItem = document.createElement('div');
        purchaseItem.className = 'purchase-item';
        
        purchaseItem.innerHTML = `
            <div class="purchase-header">
                <div class="purchase-date">Ngày mua: ${purchase.date}</div>
                <div class="purchase-status ${statusClass}">${statusText}</div>
            </div>
            <div class="purchase-content">
                <div class="purchase-image">
                    <img src="${purchase.image}" alt="${purchase.title}">
                </div>
                <div class="purchase-details">
                    <div class="purchase-title">${purchase.title}</div>
                    <div class="purchase-seller">Người bán: ${purchase.seller}</div>
                    <div class="purchase-price">${purchase.price}</div>
                    <div class="purchase-actions">
                        <button class="btn btn-outline btn-sm">Xem chi tiết</button>
                        ${purchase.status === 'completed' ? '<button class="btn btn-outline btn-sm">Đánh giá</button>' : ''}
                        ${purchase.status === 'processing' ? '<button class="btn btn-outline btn-sm">Hủy đơn</button>' : ''}
                    </div>
                </div>
            </div>
        `;
        
        purchaseList.appendChild(purchaseItem);
    });
}

// Get status text based on status code
function getStatusText(status) {
    switch (status) {
        case 'completed':
            return 'Đã hoàn thành';
        case 'processing':
            return 'Đang xử lý';
        case 'cancelled':
            return 'Đã hủy';
        default:
            return 'Không xác định';
    }
}

// Setup event listeners
function setupEventListeners() {
    // Profile tabs
    profileTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            profileTabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            const targetContent = document.getElementById(tab.dataset.target);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
    
    // Purchase status filter
    purchaseStatusFilter.addEventListener('change', () => {
        renderPurchaseHistory(purchaseStatusFilter.value);
    });
    
    // Edit profile button
    editProfileBtn.addEventListener('click', () => {
        editProfileModal.classList.remove('hidden');
    });
    
    // Close modal button
    closeModalBtn.addEventListener('click', () => {
        editProfileModal.classList.add('hidden');
    });
    
    // Cancel edit button
    cancelEditBtn.addEventListener('click', () => {
        editProfileModal.classList.add('hidden');
    });
    
    // Edit profile form submission
    editProfileForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Get form values
        const name = document.getElementById('edit-name').value;
        const email = document.getElementById('edit-email').value;
        const phone = document.getElementById('edit-phone').value;
        const address = document.getElementById('edit-address').value;
        
        // Validate form
        if (!name || !email) {
            alert('Vui lòng điền đầy đủ thông tin cần thiết.');
            return;
        }
        
        // Update user info (would connect to backend in a real app)
        console.log('Updated profile:', { name, email, phone, address });
        
        // Update UI
        document.querySelector('.user-name').textContent = name;
        document.querySelector('.user-email').textContent = email;
        
        // Close modal
        editProfileModal.classList.add('hidden');
        
        // Show success message
        alert('Cập nhật hồ sơ thành công!');
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === editProfileModal) {
            editProfileModal.classList.add('hidden');
        }
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);