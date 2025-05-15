function cancel() {
    alert("Bạn có chắc chắn muốn hủy giao dịch không?");
    // Clear selected item from localStorage
    localStorage.removeItem('selectedItem');
    window.location.href = '/home';
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
        window.location.href = '/home';
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

// Setup event listeners
function setupEventListeners() {
    // Payment option selection
    paymentOptions.forEach(option => {
        option.addEventListener('click', () => {
            // Remove selected class from all options
            paymentOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to clicked option
            option.classList.add('selected');
            
            // Enable complete payment button
            completePaymentBtn.disabled = false;
            
            // Store selected payment method
            transactionData.paymentMethod = option.dataset.method;
        });
    });
    
    // Complete payment button
    completePaymentBtn.addEventListener('click', () => {
        // Set timestamp
        transactionData.timestamp = new Date().toISOString();
        
        // Log transaction data (would be saved to database in a real app)
        console.log('Transaction data to save:', transactionData);
        
        // Show success modal
        successModal.classList.remove('hidden');
    });
    
    // Back to home button in success modal
    backToHomeBtn.addEventListener('click', () => {
        window.location.href = '/home';
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);

function savePurchaseToLocalStorage(transaction) {
    // Get existing purchases or initialize empty array
    const purchases = JSON.parse(localStorage.getItem('purchases') || '[]');
    
    // Add new purchase to array
    purchases.push(transaction);
    
    // Save back to localStorage
    localStorage.setItem('purchases', JSON.stringify(purchases));
    //gotta save to database
}

// Inside setupEventListeners function, update the completePaymentBtn click handler
completePaymentBtn.addEventListener('click', () => {
    // Set timestamp
    transactionData.timestamp = new Date().toISOString();
    
    // Save purchase to localStorage
    savePurchaseToLocalStorage(transactionData);
    
    // Remove the selected item from localStorage since purchase is complete
    localStorage.removeItem('selectedItem');
    
    // Log transaction data (would be saved to database in a real app)
    console.log('Transaction data saved:', transactionData);
    
    // Show success modal
    successModal.classList.remove('hidden');
});