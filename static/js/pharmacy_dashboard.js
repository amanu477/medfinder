/**
 * Pharmacy Dashboard JavaScript functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
    
    // Initialize datatables if available
    if (typeof $.fn.DataTable !== 'undefined') {
        $('.datatable').DataTable({
            responsive: true,
            order: [[0, 'desc']]
        });
    }
    
    // Handle status updates via AJAX
    const statusUpdateForms = document.querySelectorAll('.status-update-form');
    statusUpdateForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const url = form.getAttribute('action');
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showAlert('Status updated successfully!', 'success');
                    
                    // Update UI
                    const prescriptionId = form.getAttribute('data-prescription-id');
                    const statusBadge = document.querySelector(`.status-badge-${prescriptionId}`);
                    if (statusBadge) {
                        statusBadge.textContent = data.status_display;
                        
                        // Update badge color
                        statusBadge.className = 'badge ';
                        if (data.status === 'pending') {
                            statusBadge.className += 'bg-warning';
                        } else if (data.status === 'approved') {
                            statusBadge.className += 'bg-success';
                        } else if (data.status === 'rejected') {
                            statusBadge.className += 'bg-danger';
                        } else {
                            statusBadge.className += 'bg-info';
                        }
                    }
                    
                    // Close the modal if it exists
                    const modalId = form.closest('.modal').id;
                    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
                    if (modal) {
                        modal.hide();
                    }
                } else {
                    // Show error message
                    showAlert(data.error || 'An error occurred', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('An error occurred while updating the status', 'danger');
            });
        });
    });
    
    // Medicine stock level warnings
    const stockInputs = document.querySelectorAll('.stock-input');
    stockInputs.forEach(input => {
        input.addEventListener('change', function() {
            const value = parseInt(this.value);
            const warningElement = this.nextElementSibling;
            
            if (value <= 5) {
                warningElement.textContent = 'Low stock!';
                warningElement.classList.remove('d-none');
                warningElement.classList.add('text-danger');
            } else if (value <= 10) {
                warningElement.textContent = 'Stock getting low';
                warningElement.classList.remove('d-none');
                warningElement.classList.add('text-warning');
            } else {
                warningElement.classList.add('d-none');
            }
        });
        
        // Trigger on load
        input.dispatchEvent(new Event('change'));
    });
    
    // Initialize medicine expiry date warning
    const expiryDateInputs = document.querySelectorAll('.expiry-date-input');
    expiryDateInputs.forEach(input => {
        input.addEventListener('change', function() {
            const expiryDate = new Date(this.value);
            const today = new Date();
            const thirtyDaysLater = new Date();
            thirtyDaysLater.setDate(today.getDate() + 30);
            
            const warningElement = this.nextElementSibling;
            
            if (expiryDate < today) {
                warningElement.textContent = 'This medicine has expired!';
                warningElement.classList.remove('d-none');
                warningElement.classList.add('text-danger');
            } else if (expiryDate <= thirtyDaysLater) {
                warningElement.textContent = 'Expiring soon!';
                warningElement.classList.remove('d-none');
                warningElement.classList.add('text-warning');
            } else {
                warningElement.classList.add('d-none');
            }
        });
        
        // Trigger on load
        input.dispatchEvent(new Event('change'));
    });
});

/**
 * Show a Bootstrap alert
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.role = 'alert';
    
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alertElement);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertElement);
        bsAlert.close();
    }, 5000);
}

/**
 * Initialize dashboard charts
 */
function initializeCharts() {
    // Medicine Stock Chart
    const stockChartCanvas = document.getElementById('medicineStockChart');
    if (stockChartCanvas) {
        const ctx = stockChartCanvas.getContext('2d');
        
        // Get data from the data attributes
        const labels = JSON.parse(stockChartCanvas.getAttribute('data-labels'));
        const data = JSON.parse(stockChartCanvas.getAttribute('data-values'));
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Stock Level',
                    data: data,
                    backgroundColor: '#4e73df',
                    borderColor: '#4e73df',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Prescription Status Chart
    const prescriptionChartCanvas = document.getElementById('prescriptionStatusChart');
    if (prescriptionChartCanvas) {
        const ctx = prescriptionChartCanvas.getContext('2d');
        
        // Get data from the data attributes
        const statusLabels = JSON.parse(prescriptionChartCanvas.getAttribute('data-labels'));
        const statusData = JSON.parse(prescriptionChartCanvas.getAttribute('data-values'));
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: statusLabels,
                datasets: [{
                    data: statusData,
                    backgroundColor: ['#f6c23e', '#1cc88a', '#e74a3b', '#36b9cc'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                cutout: '60%'
            }
        });
    }
}