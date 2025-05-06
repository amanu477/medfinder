/**
 * Functions for handling location-related features
 */

// Get user's location and set it in the forms
function getUserLocation() {
    // Check if geolocation is supported
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(successCallback, errorCallback);
    } else {
        console.error('Geolocation is not supported by this browser.');
    }
}

// Success callback when location is obtained
function successCallback(position) {
    const userLat = position.coords.latitude;
    const userLng = position.coords.longitude;
    
    // Add to all forms that need location
    const locationForms = document.querySelectorAll('.needs-location');
    locationForms.forEach(form => {
        // Look for existing lat/lng inputs, or create them
        let latInput = form.querySelector('input[name="lat"]');
        let lngInput = form.querySelector('input[name="lng"]');
        
        if (!latInput) {
            latInput = document.createElement('input');
            latInput.type = 'hidden';
            latInput.name = 'lat';
            form.appendChild(latInput);
        }
        
        if (!lngInput) {
            lngInput = document.createElement('input');
            lngInput.type = 'hidden';
            lngInput.name = 'lng';
            form.appendChild(lngInput);
        }
        
        latInput.value = userLat;
        lngInput.value = userLng;
    });
    
    // Look for specific location inputs
    const userLatInputs = document.querySelectorAll('#user-latitude');
    const userLngInputs = document.querySelectorAll('#user-longitude');
    
    userLatInputs.forEach(input => input.value = userLat);
    userLngInputs.forEach(input => input.value = userLng);
    
    // Trigger an event that location has been obtained
    document.dispatchEvent(new CustomEvent('userLocationObtained', {
        detail: { lat: userLat, lng: userLng }
    }));
}

// Error callback when location cannot be obtained
function errorCallback(error) {
    console.error('Error getting location:', error.message);
    
    // Trigger an event that location failed
    document.dispatchEvent(new CustomEvent('userLocationFailed', {
        detail: { error: error.message }
    }));
}

// Initialize location detection
document.addEventListener('DOMContentLoaded', function() {
    getUserLocation();
    
    // Add event listeners for location buttons
    const locationButtons = document.querySelectorAll('.get-location-btn');
    locationButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            getUserLocation();
        });
    });
});