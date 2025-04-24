// JavaScript functionality for the pharmacy dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date formatting for expiry dates
    const expiryDateElements = document.querySelectorAll('.expiry-date');
    expiryDateElements.forEach(element => {
        const dateString = element.getAttribute('data-date');
        if (dateString) {
            const formattedDate = formatDate(dateString);
            element.textContent = formattedDate;
            
            // Add color coding based on expiry date
            if (isPastDate(dateString)) {
                element.classList.add('text-danger');
                element.closest('tr').classList.add('bg-light-danger');
            } else if (isExpiringSoon(dateString)) {
                element.classList.add('text-warning');
                element.closest('tr').classList.add('bg-light-warning');
            }
        }
    });
    
    // Initialize medicine stock indicators
    const stockElements = document.querySelectorAll('.stock-quantity');
    stockElements.forEach(element => {
        const quantity = parseInt(element.textContent);
        if (quantity <= 5) {
            element.classList.add('text-danger');
        } else if (quantity <= 20) {
            element.classList.add('text-warning');
        } else {
            element.classList.add('text-success');
        }
    });
    
    // Handle medicine deletion confirmation
    const deleteButtons = document.querySelectorAll('.delete-medicine-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const medicineId = this.getAttribute('data-id');
            const medicineName = this.getAttribute('data-name');
            
            if (confirm(`Are you sure you want to delete ${medicineName}? This action cannot be undone.`)) {
                // Get the form and submit it
                const form = document.getElementById(`delete-medicine-form-${medicineId}`);
                if (form) {
                    form.submit();
                }
            }
        });
    });
    
    // Handle prescription status updates
    const statusSelects = document.querySelectorAll('.prescription-status-select');
    statusSelects.forEach(select => {
        select.addEventListener('change', function() {
            const prescriptionId = this.getAttribute('data-id');
            const form = document.getElementById(`prescription-status-form-${prescriptionId}`);
            if (form) {
                form.submit();
            }
        });
    });
    
    // Dashboard chart initialization
    const expiringChart = document.getElementById('expiring-medicines-chart');
    if (expiringChart && typeof Chart !== 'undefined') {
        // Get data from the data attribute
        const medicines = JSON.parse(expiringChart.getAttribute('data-medicines') || '[]');
        
        // Group by month
        const monthCounts = {};
        
        medicines.forEach(medicine => {
            const date = new Date(medicine.expiry_date);
            const monthYear = `${date.getMonth() + 1}/${date.getFullYear()}`;
            
            if (!monthCounts[monthYear]) {
                monthCounts[monthYear] = 0;
            }
            
            monthCounts[monthYear]++;
        });
        
        // Sort keys by date
        const sortedMonths = Object.keys(monthCounts).sort((a, b) => {
            const [aMonth, aYear] = a.split('/').map(Number);
            const [bMonth, bYear] = b.split('/').map(Number);
            
            if (aYear !== bYear) {
                return aYear - bYear;
            }
            
            return aMonth - bMonth;
        });
        
        // Create chart
        new Chart(expiringChart, {
            type: 'bar',
            data: {
                labels: sortedMonths,
                datasets: [{
                    label: 'Expiring Medicines',
                    data: sortedMonths.map(month => monthCounts[month]),
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Medicines'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Month/Year'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Medicines Expiring by Month'
                    }
                }
            }
        });
    }
    
    // Stock level chart
    const stockChart = document.getElementById('stock-level-chart');
    if (stockChart && typeof Chart !== 'undefined') {
        // Get data from the data attribute
        const medicines = JSON.parse(stockChart.getAttribute('data-medicines') || '[]');
        
        // Get top 10 medicines by stock
        const sortedMedicines = [...medicines].sort((a, b) => b.stock_quantity - a.stock_quantity).slice(0, 10);
        
        // Create chart
        new Chart(stockChart, {
            type: 'bar',
            data: {
                labels: sortedMedicines.map(m => m.name),
                datasets: [{
                    label: 'Stock Quantity',
                    data: sortedMedicines.map(m => m.stock_quantity),
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Quantity'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Medicine'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Top 10 Medicines by Stock Level'
                    }
                }
            }
        });
    }
    
    // Check for expiring medicines notification
    const expiringMedicinesCount = document.getElementById('expiring-medicines-count');
    if (expiringMedicinesCount) {
        const count = parseInt(expiringMedicinesCount.textContent);
        if (count > 0) {
            // Show notification if not dismissed previously
            const dismissedNotification = localStorage.getItem('dismissed-expiring-notification');
            const today = new Date().toDateString();
            
            if (dismissedNotification !== today) {
                const notification = document.createElement('div');
                notification.className = 'alert alert-warning alert-dismissible fade show';
                notification.innerHTML = `
                    <strong>Warning!</strong> You have ${count} medicine(s) expiring soon.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                
                // Insert at the top of the dashboard
                const dashboardContent = document.querySelector('.dashboard-content');
                if (dashboardContent) {
                    dashboardContent.insertBefore(notification, dashboardContent.firstChild);
                    
                    // Add dismiss handler
                    const closeButton = notification.querySelector('.btn-close');
                    if (closeButton) {
                        closeButton.addEventListener('click', function() {
                            localStorage.setItem('dismissed-expiring-notification', today);
                        });
                    }
                }
            }
        }
    }
});
