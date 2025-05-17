function cancel() {
    confirm("Bạn có chắc chắn muốn hủy giao dịch không?");
    if (confirm) {
        localStorage.removeItem('selectedItem');
        window.location.href = '/api/posts';
    }
}


// Get elements
const itemSummary = document.getElementById('item-summary');
const paymentOptions = document.querySelectorAll('.payment-option-card');
const completePaymentBtn = document.getElementById('complete-payment');
const successModal = document.getElementById('success-modal');
const backToHomeBtn = document.getElementById('back-to-home');

// Transaction data to be saved to database later
let transactionData = {
    item: null,
    paymentMethod: null,
    timestamp: null
};

// Initialize the payment page
function init() {
    // Get item data from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const itemId = urlParams.get('id');
    const itemData = getItemFromLocalStorage(itemId);
    
    if (itemData) {
        renderItemSummary(itemData);
        transactionData.item = itemData;
    } else {
        // Redirect back to main page if no item data
        window.location.href = '/api/posts';
    }
    
    // Setup event listeners
    setupEventListeners();
}

// Get item data from localStorage
function getItemFromLocalStorage(id) {
    const storedItem = localStorage.getItem('selectedItem');
    return storedItem ? JSON.parse(storedItem) : null;
}

// Render item summary
function renderItemSummary(item) {
    itemSummary.innerHTML = `
        <div class="summary-item">
            <div class="summary-item-header">
                <img src="${item.image}" alt="${item.title}" class="summary-item-image">
                <div>
                    <div class="summary-item-title">${item.title}</div>
                    <div class="summary-item-seller">Người bán: ${item.seller}</div>
                </div>
            </div>
            <div class="summary-item-price">${item.price}</div>
        </div>
        
        <div class="summary-divider"></div>
        
        <div class="summary-total">
            <span>Tổng cộng:</span>
            <span class="summary-total-price">${item.price}</span>
        </div>
    `;
}

async function transaction_confirmed() {
    const invoice = [{username: localStorage.getItem('username'),
        item: localStorage.getItem('selectedItem'),
        paymentMethod: getElementById('payment-option-card').data-method,
        price: localStorage.getItem('selectedItem').price,
    }];
    try {
        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(invoice)
        });
        if (!response.ok) {
            alert('Lỗi khi tạo giao dịch');
        }

        const data = await response.json();
        console.log('Giao dịch thành công:', data);
        alert('Giao dịch thành công');
        window.location.href = '/api/posts';
    }
    catch (error) {
        console.error('Lỗi:', error);
        alert('Đã xảy ra lỗi trong quá trình tạo giao dịch');
    }
}
