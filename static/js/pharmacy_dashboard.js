/**
 * Pharmacy Dashboard JavaScript
 * Handles dashboard-specific functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize chart for inventory analytics if the element exists
    const inventoryChartElement = document.getElementById('inventoryChart');
    if (inventoryChartElement) {
        const ctx = inventoryChartElement.getContext('2d');
        
        // Sample data - In a real application, this would come from the backend
        const inventoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Available', 'Expiring Soon', 'Out of Stock'],
                datasets: [{
                    data: [
                        document.getElementById('available-count').dataset.count,
                        document.getElementById('expiring-count').dataset.count,
                        document.getElementById('outofstock-count').dataset.count
                    ],
                    backgroundColor: [
                        '#00d97e', // success
                        '#f6c343', // warning
                        '#e63757'  // danger
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Initialize chart for prescription analytics if the element exists
    const prescriptionChartElement = document.getElementById('prescriptionChart');
    if (prescriptionChartElement) {
        const ctx = prescriptionChartElement.getContext('2d');
        
        // Sample data - In a real application, this would come from the backend
        const prescriptionChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['January', 'February', 'March', 'April', 'May', 'June'],
                datasets: [{
                    label: 'Prescriptions',
                    data: [12, 19, 8, 15, 25, 17],
                    backgroundColor: '#2c7be5',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    // Update countdown for expiring medicines
    const countdownElements = document.querySelectorAll('.expiry-countdown');
    countdownElements.forEach(el => {
        const expiryDate = new Date(el.getAttribute('data-expiry-date'));
        updateCountdown(el, expiryDate);
    });
    
    // Status form handling with confirmation
    const statusForms = document.querySelectorAll('.status-form');
    statusForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const status = form.querySelector('input[name="status"]').value;
            let confirmMessage = '';
            
            switch(status) {
                case 'approved':
                    confirmMessage = 'Are you sure you want to approve this prescription?';
                    break;
                case 'rejected':
                    confirmMessage = 'Are you sure you want to reject this prescription?';
                    break;
                case 'completed':
                    confirmMessage = 'Are you sure you want to mark this prescription as completed?';
                    break;
                default:
                    break;
            }
            
            if (confirmMessage && !confirm(confirmMessage)) {
                e.preventDefault();
            }
        });
    });
});

/**
 * Update the countdown display for expiring medicines
 */
function updateCountdown(element, expiryDate) {
    const now = new Date();
    const diff = expiryDate - now;
    
    // Calculate days remaining
    const daysRemaining = Math.ceil(diff / (1000 * 60 * 60 * 24));
    
    if (daysRemaining <= 0) {
        element.textContent = 'Expired';
        element.classList.add('text-danger');
    } else if (daysRemaining <= 30) {
        element.textContent = `${daysRemaining} days left`;
        element.classList.add('text-warning');
    } else {
        element.textContent = `${daysRemaining} days left`;
    }
}