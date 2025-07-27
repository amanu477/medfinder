// Enhanced pharmacy registration with location capture
document.addEventListener('DOMContentLoaded', function() {
    // Wait for other scripts to load first
    setTimeout(function() {
        console.log('Enhanced pharmacy registration script loaded');
        
        const getLocationBtn = document.querySelector('.get-location-btn');
        const manualLocationBtn = document.querySelector('.toggle-manual-location');
        const manualLocationSection = document.getElementById('manual-location-section');
        const latitudeField = document.getElementById('id_latitude');
        const longitudeField = document.getElementById('id_longitude');
        const manualLatField = document.getElementById('manual-latitude');
        const manualLonField = document.getElementById('manual-longitude');
        const locationStatus = document.getElementById('location-status');
        const locationMessage = document.getElementById('location-message');

        console.log('Found elements:', {
            getLocationBtn: !!getLocationBtn,
            manualLocationBtn: !!manualLocationBtn,
            manualLocationSection: !!manualLocationSection,
            latitudeField: !!latitudeField,
            longitudeField: !!longitudeField
        });

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

        // Override/enhance the existing manual location functionality
        if (manualLocationBtn && manualLocationSection) {
            // Remove existing event listeners by cloning the button
            const newBtn = manualLocationBtn.cloneNode(true);
            manualLocationBtn.parentNode.replaceChild(newBtn, manualLocationBtn);
            
            newBtn.addEventListener('click', function() {
                console.log('Enhanced manual location button clicked');
                
                // Toggle visibility
                if (manualLocationSection.classList.contains('d-none')) {
                    manualLocationSection.classList.remove('d-none');
                    newBtn.innerHTML = '<i class="fas fa-eye-slash me-2"></i> Hide Manual Entry';
                    newBtn.classList.remove('btn-outline-secondary');
                    newBtn.classList.add('btn-outline-warning');
                    showLocationStatus('info', 'Enter your pharmacy coordinates manually.');
                    
                    // Focus on latitude field
                    if (manualLatField) {
                        setTimeout(() => manualLatField.focus(), 100);
                    }
                } else {
                    manualLocationSection.classList.add('d-none');
                    newBtn.innerHTML = '<i class="fas fa-edit me-2"></i> Enter Location Manually';
                    newBtn.classList.remove('btn-outline-warning');
                    newBtn.classList.add('btn-outline-secondary');
                    showLocationStatus('info', 'Click "Get Current Location" to automatically capture your coordinates.');
                }
            });
        }

    // Manual coordinate input handlers
    if (manualLatField && manualLonField) {
        function updateFromManualEntry() {
            const lat = parseFloat(manualLatField.value);
            const lon = parseFloat(manualLonField.value);
            
            console.log('Manual coordinates entered:', lat, lon);
            
            if (!isNaN(lat) && !isNaN(lon)) {
                if (latitudeField) latitudeField.value = lat;
                if (longitudeField) longitudeField.value = lon;
                
                showLocationStatus('success', `Manual coordinates set: Latitude: ${lat}, Longitude: ${lon}`);
                console.log('Manual pharmacy coordinates set:', lat, lon);
            } else if (manualLatField.value || manualLonField.value) {
                showLocationStatus('info', 'Please enter both latitude and longitude coordinates.');
            }
        }
        
        manualLatField.addEventListener('input', updateFromManualEntry);
        manualLonField.addEventListener('input', updateFromManualEntry);
        manualLatField.addEventListener('blur', updateFromManualEntry);
        manualLonField.addEventListener('blur', updateFromManualEntry);
    } else {
        console.log('Manual coordinate fields not found:', {
            manualLatField: !!manualLatField,
            manualLonField: !!manualLonField
        });
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
        
    }, 500); // Wait 500ms for other scripts to load
});