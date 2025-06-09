/**
 * Main JavaScript for MedFinder
 * Handles general UI interactions and functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Prescription Upload modal handling
    const prescriptionModal = document.getElementById('prescriptionModal');
    if (prescriptionModal) {
        prescriptionModal.addEventListener('show.bs.modal', function(event) {
            // Button that triggered the modal
            const button = event.relatedTarget;
            
            // Extract pharmacy info from data attributes
            const pharmacyId = button.getAttribute('data-pharmacy-id');
            const pharmacyName = button.getAttribute('data-pharmacy-name');
            
            // Update the modal's content
            const selectedPharmacyId = document.getElementById('selected-pharmacy-id');
            const selectedPharmacyName = document.getElementById('selected-pharmacy-name');
            
            if (selectedPharmacyId && selectedPharmacyName) {
                selectedPharmacyId.value = pharmacyId;
                selectedPharmacyName.textContent = pharmacyName;
            }
        });
    }
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Countdown timer for expiring medicines
    const countdownElements = document.querySelectorAll('.expiry-countdown');
    countdownElements.forEach(el => {
        const expiryDate = new Date(el.getAttribute('data-expiry-date'));
        updateCountdown(el, expiryDate);
        
        // Update every day
        setInterval(() => {
            updateCountdown(el, expiryDate);
        }, 86400000); // 24 hours
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