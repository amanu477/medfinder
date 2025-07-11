// Location-based search functionality
var userLocation = null;

// Get user's current location
function getUserLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation is not supported by this browser'));
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                };
                resolve(userLocation);
            },
            (error) => {
                let errorMsg = 'Unknown error occurred';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMsg = 'Location access denied by user';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMsg = 'Location information unavailable';
                        break;
                    case error.TIMEOUT:
                        errorMsg = 'Location request timeout';
                        break;
                }
                reject(new Error(errorMsg));
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 minutes
            }
        );
    });
}

// Update search form to include location
function updateSearchFormWithLocation() {
    const searchForm = document.querySelector('.search-form');
    if (!searchForm || !userLocation) return;

    // Add hidden inputs for coordinates
    let latInput = searchForm.querySelector('input[name="lat"]');
    let lonInput = searchForm.querySelector('input[name="lon"]');

    if (!latInput) {
        latInput = document.createElement('input');
        latInput.type = 'hidden';
        latInput.name = 'lat';
        searchForm.appendChild(latInput);
    }

    if (!lonInput) {
        lonInput = document.createElement('input');
        lonInput.type = 'hidden';
        lonInput.name = 'lon';
        searchForm.appendChild(lonInput);
    }

    latInput.value = userLocation.lat;
    lonInput.value = userLocation.lon;
}

// Show location status to user
function showLocationStatus(message, isError = false) {
    // Remove existing status
    const existingStatus = document.querySelector('.location-status');
    if (existingStatus) {
        existingStatus.remove();
    }

    // Create status element
    const statusDiv = document.createElement('div');
    statusDiv.className = `location-status alert ${isError ? 'alert-warning' : 'alert-info'} alert-dismissible fade show mt-2`;
    statusDiv.innerHTML = `
        <i class="fas ${isError ? 'fa-exclamation-triangle' : 'fa-map-marker-alt'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insert after search container
    const searchContainer = document.querySelector('.search-container');
    if (searchContainer) {
        searchContainer.appendChild(statusDiv);
    }
}

// Initialize location functionality
function initializeLocation() {
    // Try to get user location automatically
    getUserLocation()
        .then((location) => {
            updateSearchFormWithLocation();
            showLocationStatus('Location enabled - search results will be sorted by distance from you');
        })
        .catch((error) => {
            console.log('Location error:', error);
            showLocationStatus('Location not available - search results will be shown without proximity sorting', true);
        });
}

// Add location request button
function addLocationButton() {
    const searchContainer = document.querySelector('.search-container');
    if (!searchContainer) return;

    const locationBtn = document.createElement('button');
    locationBtn.type = 'button';
    locationBtn.className = 'btn btn-outline-secondary btn-sm mt-2';
    locationBtn.innerHTML = '<i class="fas fa-location-arrow me-1"></i> Use My Location';
    
    locationBtn.addEventListener('click', () => {
        locationBtn.disabled = true;
        locationBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Getting Location...';
        
        getUserLocation()
            .then((location) => {
                updateSearchFormWithLocation();
                showLocationStatus('Location enabled - search results will be sorted by distance');
                locationBtn.innerHTML = '<i class="fas fa-check me-1"></i> Location Enabled';
                locationBtn.className = 'btn btn-success btn-sm mt-2';
            })
            .catch((error) => {
                showLocationStatus(error.message, true);
                locationBtn.disabled = false;
                locationBtn.innerHTML = '<i class="fas fa-location-arrow me-1"></i> Use My Location';
            });
    });

    searchContainer.appendChild(locationBtn);
}

// Handle pharmacy registration location functionality
function handlePharmacyLocationButton() {
    const locationBtn = document.querySelector('.get-location-btn');
    const manualToggleBtn = document.querySelector('.toggle-manual-location');
    const manualSection = document.getElementById('manual-location-section');
    const manualLatInput = document.getElementById('manual-latitude');
    const manualLonInput = document.getElementById('manual-longitude');
    
    if (!locationBtn) return;

    // Handle automatic location detection
    locationBtn.addEventListener('click', () => {
        const latInput = document.querySelector('input[name="latitude"]');
        const lonInput = document.querySelector('input[name="longitude"]');
        const statusDiv = document.getElementById('location-status');
        const messageSpan = document.getElementById('location-message');

        if (!latInput || !lonInput) return;

        // Update button state
        locationBtn.disabled = true;
        locationBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Getting Location...';

        getUserLocation()
            .then((location) => {
                // Update form fields
                latInput.value = location.lat;
                lonInput.value = location.lon;

                // Clear manual inputs
                if (manualLatInput) manualLatInput.value = '';
                if (manualLonInput) manualLonInput.value = '';

                // Show success message
                statusDiv.classList.remove('d-none', 'alert-info', 'alert-warning');
                statusDiv.classList.add('alert-success');
                messageSpan.textContent = `Location obtained: ${location.lat.toFixed(6)}, ${location.lon.toFixed(6)}`;

                // Update button
                locationBtn.innerHTML = '<i class="fas fa-check me-2"></i> Location Obtained';
                locationBtn.className = 'btn btn-success';

                // Hide manual section if open
                if (manualSection && !manualSection.classList.contains('d-none')) {
                    manualSection.classList.add('d-none');
                    manualToggleBtn.innerHTML = '<i class="fas fa-edit me-2"></i> Enter Location Manually';
                }

                // Dispatch custom event
                document.dispatchEvent(new CustomEvent('userLocationObtained', {
                    detail: location
                }));
            })
            .catch((error) => {
                // Show error message
                statusDiv.classList.remove('d-none', 'alert-info', 'alert-success');
                statusDiv.classList.add('alert-warning');
                messageSpan.textContent = `Error: ${error.message}. Try entering coordinates manually.`;

                // Reset button
                locationBtn.disabled = false;
                locationBtn.innerHTML = '<i class="fas fa-map-marker-alt me-2"></i> Get Current Location';
            });
    });

    // Handle manual location toggle
    if (manualToggleBtn && manualSection) {
        manualToggleBtn.addEventListener('click', () => {
            const isHidden = manualSection.classList.contains('d-none');
            
            if (isHidden) {
                // Show manual section
                manualSection.classList.remove('d-none');
                manualToggleBtn.innerHTML = '<i class="fas fa-times me-2"></i> Cancel Manual Entry';
                manualToggleBtn.className = 'btn btn-outline-danger';
                
                // Update status message
                const statusDiv = document.getElementById('location-status');
                const messageSpan = document.getElementById('location-message');
                statusDiv.classList.remove('d-none', 'alert-success', 'alert-warning');
                statusDiv.classList.add('alert-info');
                messageSpan.textContent = 'Enter your pharmacy coordinates manually below.';
            } else {
                // Hide manual section
                manualSection.classList.add('d-none');
                manualToggleBtn.innerHTML = '<i class="fas fa-edit me-2"></i> Enter Location Manually';
                manualToggleBtn.className = 'btn btn-outline-secondary';
                
                // Clear manual inputs
                if (manualLatInput) manualLatInput.value = '';
                if (manualLonInput) manualLonInput.value = '';
            }
        });
    }

    // Handle manual coordinate input changes
    if (manualLatInput && manualLonInput) {
        console.log('Manual location inputs found, setting up event listeners');
        
        const updateFormWithManualLocation = () => {
            const latInput = document.querySelector('input[name="latitude"]');
            const lonInput = document.querySelector('input[name="longitude"]');
            const statusDiv = document.getElementById('location-status');
            const messageSpan = document.getElementById('location-message');

            console.log('Updating manual location, lat input:', latInput, 'lon input:', lonInput);

            const lat = parseFloat(manualLatInput.value);
            const lon = parseFloat(manualLonInput.value);

            console.log('Manual coordinates entered:', lat, lon);

            if (!isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
                // Valid coordinates
                if (latInput && lonInput) {
                    latInput.value = lat;
                    lonInput.value = lon;
                    console.log('Form fields updated with manual coordinates');
                }

                if (statusDiv && messageSpan) {
                    statusDiv.classList.remove('d-none', 'alert-info', 'alert-warning');
                    statusDiv.classList.add('alert-success');
                    messageSpan.textContent = `Manual coordinates set: ${lat.toFixed(6)}, ${lon.toFixed(6)}`;
                }

                // Reset automatic button
                locationBtn.innerHTML = '<i class="fas fa-map-marker-alt me-2"></i> Get Current Location';
                locationBtn.className = 'btn btn-outline-primary';
                locationBtn.disabled = false;
            } else if (manualLatInput.value !== '' || manualLonInput.value !== '') {
                // Invalid coordinates (only show error if user has entered something)
                if (statusDiv && messageSpan) {
                    statusDiv.classList.remove('d-none', 'alert-success', 'alert-info');
                    statusDiv.classList.add('alert-warning');
                    messageSpan.textContent = 'Please enter valid coordinates (Latitude: -90 to 90, Longitude: -180 to 180)';
                }
            }
        };

        manualLatInput.addEventListener('input', updateFormWithManualLocation);
        manualLonInput.addEventListener('input', updateFormWithManualLocation);
        manualLatInput.addEventListener('change', updateFormWithManualLocation);
        manualLonInput.addEventListener('change', updateFormWithManualLocation);
    } else {
        console.log('Manual location inputs not found');
    }
}

// Update customer location on server
function updateCustomerLocation(lat, lon) {
    fetch('/customer/update-location/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            latitude: lat,
            longitude: lon
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Customer location updated successfully');
        } else {
            console.error('Failed to update customer location:', data.error);
        }
    })
    .catch(error => {
        console.error('Error updating customer location:', error);
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Handle pharmacy registration location
    handlePharmacyLocationButton();
    
    // Add location button for search pages
    addLocationButton();
    
    // Automatically try to get location for search pages
    initializeLocation();
    
    // Auto-update customer location for authenticated customers
    if (window.location.pathname.includes('/customer/')) {
        getUserLocation()
            .then((location) => {
                updateCustomerLocation(location.lat, location.lon);
            })
            .catch((error) => {
                console.log('Customer location update failed:', error);
            });
    }
});