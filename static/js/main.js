/**
 * Main JavaScript for the MedFinder application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle prescription upload modal
    const prescriptionModal = document.getElementById('prescriptionModal');
    if (prescriptionModal) {
        const modal = new bootstrap.Modal(prescriptionModal);
        
        const uploadButtons = document.querySelectorAll('.upload-rx-btn');
        const pharmacyInfoDiv = document.getElementById('pharmacy-info');
        const selectedPharmacyName = document.getElementById('selected-pharmacy-name');
        const selectedPharmacyId = document.getElementById('selected-pharmacy-id');
        
        uploadButtons.forEach(button => {
            button.addEventListener('click', function() {
                const pharmacyId = this.getAttribute('data-pharmacy-id');
                const pharmacyName = this.getAttribute('data-pharmacy-name');
                
                if (pharmacyId && pharmacyName) {
                    // Show pharmacy info and set values
                    if (pharmacyInfoDiv) pharmacyInfoDiv.classList.remove('d-none');
                    if (selectedPharmacyName) selectedPharmacyName.textContent = pharmacyName;
                    if (selectedPharmacyId) selectedPharmacyId.value = pharmacyId;
                } else {
                    // Hide pharmacy info if no pharmacy selected
                    if (pharmacyInfoDiv) pharmacyInfoDiv.classList.add('d-none');
                    if (selectedPharmacyId) selectedPharmacyId.value = '';
                }
            });
        });
    }
    
    // Handle auto-dismiss alerts
    const autoDismissAlerts = document.querySelectorAll('.alert-auto-dismiss');
    autoDismissAlerts.forEach(alert => {
        setTimeout(() => {
            const alertInstance = new bootstrap.Alert(alert);
            alertInstance.close();
        }, 5000); // Auto-dismiss after 5 seconds
    });
});