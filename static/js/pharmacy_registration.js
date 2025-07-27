// Automatic location capture for pharmacy registration
document.addEventListener('DOMContentLoaded', function() {
    const getLocationBtn = document.querySelector('.get-location-btn');
    const manualLocationBtn = document.querySelector('.toggle-manual-location');
    const manualLocationSection = document.getElementById('manual-location-section');
    const latitudeField = document.getElementById('id_latitude');
    const longitudeField = document.getElementById('id_longitude');
    const manualLatField = document.getElementById('manual-latitude');
    const manualLonField = document.getElementById('manual-longitude');
    const locationStatus = document.getElementById('location-status');
    const locationMessage = document.getElementById('location-message');

    // Automatic location detection
    if (getLocationBtn) {
        getLocationBtn.addEventListener('click', function() {
            if (!navigator.geolocation) {
                showLocationStatus('error', 'Geolocation is not supported by this browser.');
                return;
            }

            // Show loading
            getLocationBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Getting Location...';
            getLocationBtn.disabled = true;
            showLocationStatus('info', 'Requesting your location...');

            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    
                    // Update hidden form fields
                    if (latitudeField) latitudeField.value = lat;
                    if (longitudeField) longitudeField.value = lon;
                    
                    // Update display
                    showLocationStatus('success', `Location captured successfully! Latitude: ${lat.toFixed(6)}, Longitude: ${lon.toFixed(6)}`);
                    
                    // Reset button
                    getLocationBtn.innerHTML = '<i class="fas fa-check me-2"></i> Location Captured';
                    getLocationBtn.disabled = false;
                    getLocationBtn.classList.remove('btn-outline-primary');
                    getLocationBtn.classList.add('btn-success');
                    
                    console.log('Pharmacy location captured:', lat, lon);
                },
                function(error) {
                    let errorMsg = 'Failed to get location. ';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg += 'Location access denied. Please enable location access and try again.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMsg += 'Location information unavailable.';
                            break;
                        case error.TIMEOUT:
                            errorMsg += 'Location request timeout.';
                            break;
                        default:
                            errorMsg += 'Unknown error occurred.';
                            break;
                    }
                    
                    showLocationStatus('error', errorMsg);
                    
                    // Reset button
                    getLocationBtn.innerHTML = '<i class="fas fa-map-marker-alt me-2"></i> Get Current Location';
                    getLocationBtn.disabled = false;
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000
                }
            );
        });
    }

    // Manual location entry
    if (manualLocationBtn) {
        manualLocationBtn.addEventListener('click', function() {
            if (manualLocationSection) {
                manualLocationSection.classList.toggle('d-none');
                const isVisible = !manualLocationSection.classList.contains('d-none');
                
                manualLocationBtn.innerHTML = isVisible 
                    ? '<i class="fas fa-eye-slash me-2"></i> Hide Manual Entry'
                    : '<i class="fas fa-edit me-2"></i> Enter Location Manually';
                
                if (isVisible) {
                    showLocationStatus('info', 'Enter your pharmacy coordinates manually.');
                }
            }
        });
    }

    // Manual coordinate input handlers
    if (manualLatField && manualLonField) {
        function updateFromManualEntry() {
            const lat = parseFloat(manualLatField.value);
            const lon = parseFloat(manualLonField.value);
            
            if (!isNaN(lat) && !isNaN(lon)) {
                if (latitudeField) latitudeField.value = lat;
                if (longitudeField) longitudeField.value = lon;
                
                showLocationStatus('success', `Manual coordinates set: Latitude: ${lat}, Longitude: ${lon}`);
                console.log('Manual pharmacy coordinates set:', lat, lon);
            }
        }
        
        manualLatField.addEventListener('input', updateFromManualEntry);
        manualLonField.addEventListener('input', updateFromManualEntry);
    }

    // Form submission validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const lat = latitudeField ? latitudeField.value : '';
            const lon = longitudeField ? longitudeField.value : '';
            
            if (!lat || !lon) {
                e.preventDefault();
                showLocationStatus('error', 'Please capture your pharmacy location before submitting. This helps customers find your pharmacy and see accurate distances.');
                
                // Scroll to location section
                const locationSection = document.getElementById('location-status');
                if (locationSection) {
                    locationSection.scrollIntoView({ behavior: 'smooth' });
                }
                
                return false;
            }
        });
    }

    function showLocationStatus(type, message) {
        if (locationStatus && locationMessage) {
            locationStatus.classList.remove('d-none', 'alert-info', 'alert-success', 'alert-danger');
            
            switch(type) {
                case 'success':
                    locationStatus.classList.add('alert-success');
                    break;
                case 'error':
                    locationStatus.classList.add('alert-danger');
                    break;
                default:
                    locationStatus.classList.add('alert-info');
            }
            
            locationMessage.textContent = message;
        }
    }

    // Show initial message
    showLocationStatus('info', 'Click "Get Current Location" to automatically capture your pharmacy\'s coordinates, or enter them manually.');
});