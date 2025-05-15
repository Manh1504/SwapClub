function selectPayment(method) {
    // Remove selected class from all options
    document.querySelectorAll('.payment-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Hide all payment details
    document.querySelectorAll('.payment-details').forEach(detail => {
        detail.classList.remove('active');
    });
    
    // Add selected class to clicked option
    const selectedOption = document.querySelector(`.payment-option[onclick="selectPayment('${method}')"]`);
    if (selectedOption) {
        selectedOption.classList.add('selected');
    }
    
    // Show relevant payment details
    const paymentDetails = document.getElementById(`${method}-details`);
    if (paymentDetails) {
        paymentDetails.classList.add('active');
    }
}

document.getElementById('payment_initialized').addEventListener('click', function() {
    window.alert('Transaction Successful!');
});