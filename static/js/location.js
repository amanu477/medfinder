/**
 * Location Service JavaScript
 * Handles geolocation for the pharmacy finder application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get all location buttons
    const locationButtons = document.querySelectorAll('.get-location-btn');
    
    // Add click event listeners to all location buttons
    locationButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            getLocation();
        });
    });
    
    // If we have latitude and longitude fields, try to auto-get location
    const latField = document.getElementById('user-latitude');
    const lngField = document.getElementById('user-longitude');
    
    if (latField && lngField) {
        // Try to get location automatically
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => {
                    latField.value = position.coords.latitude;
                    lngField.value = position.coords.longitude;
                    
                    // Dispatch an event so other components can respond
                    const event = new CustomEvent('userLocationObtained', {
                        detail: {
                            lat: position.coords.latitude,
                            lng: position.coords.longitude
                        }
                    });
                    document.dispatchEvent(event);
                    
                    // Update UI if necessary
                    updateLocationUI(true);
                },
                error => {
                    console.error('Error getting location:', error);
                    updateLocationUI(false);
                },
                { enableHighAccuracy: true }
            );
        }
    }
});

/**
 * Get the user's location using the Geolocation API
 */
function getLocation() {
    if (navigator.geolocation) {
        // Change button text to show loading
        const locationButtons = document.querySelectorAll('.get-location-btn');
        locationButtons.forEach(button => {
            button.textContent = 'Getting location...';
            button.disabled = true;
        });
        
        navigator.geolocation.getCurrentPosition(
            position => {
                // Get the latitude and longitude
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
                
                // Update any hidden fields
                updateLocationFields(latitude, longitude);
                
                // Dispatch an event so other components can respond
                const event = new CustomEvent('userLocationObtained', {
                    detail: {
                        lat: latitude,
                        lng: longitude
                    }
                });
                document.dispatchEvent(event);
                
                // Update UI
                updateLocationUI(true);
            },
            error => {
                console.error('Error getting location:', error);
                updateLocationUI(false);
                
                // Re-enable buttons
                locationButtons.forEach(button => {
                    button.textContent = 'Get my location';
                    button.disabled = false;
                });
                
                // Show error message
                alert('Could not get your location. Please try again or enter your location manually.');
            },
            { enableHighAccuracy: true }
        );
    } else {
        alert('Geolocation is not supported by your browser. Please enter your location manually.');
    }
}

/**
 * Update the hidden location fields with the user's coordinates
 */
function updateLocationFields(latitude, longitude) {
    const latField = document.getElementById('user-latitude');
    const lngField = document.getElementById('user-longitude');
    
    if (latField && lngField) {
        latField.value = latitude;
        lngField.value = longitude;
    }
}

/**
 * Update the UI to reflect the location status
 */
function updateLocationUI(success) {
    const locationButtons = document.querySelectorAll('.get-location-btn');
    
    locationButtons.forEach(button => {
        if (success) {
            button.textContent = 'Location obtained';
            button.classList.add('text-success');
        } else {
            button.textContent = 'Get my location';
            button.classList.remove('text-success');
        }
        button.disabled = false;
    });
}