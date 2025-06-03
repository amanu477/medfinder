// Location-based search functionality
let userLocation = null;

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

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Add location button for manual activation
    addLocationButton();
    
    // Automatically try to get location (users can deny)
    initializeLocation();
});