// Location-related functionality for the platform

// Store user's location
let userLocation = null;

// Get user's current location
function getUserLocation() {
    return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => {
                    const location = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    userLocation = location;
                    localStorage.setItem('userLocation', JSON.stringify(location));
                    resolve(location);
                },
                error => {
                    console.error('Error getting location:', error.message);
                    reject(error);
                },
                { timeout: 10000, enableHighAccuracy: true }
            );
        } else {
            const error = new Error('Geolocation is not supported by this browser.');
            console.error(error.message);
            reject(error);
        }
    });
}

// Try to get cached location or request a new one
function initUserLocation() {
    const cachedLocation = localStorage.getItem('userLocation');
    
    if (cachedLocation) {
        userLocation = JSON.parse(cachedLocation);
        return Promise.resolve(userLocation);
    } else {
        return getUserLocation();
    }
}

// Add location data to forms that need it
function addLocationToForm() {
    const forms = document.querySelectorAll('form.needs-location');
    
    forms.forEach(form => {
        // Get existing fields or create them
        let latInput = form.querySelector('input[name="latitude"]') || form.querySelector('input[name="lat"]');
        let lngInput = form.querySelector('input[name="longitude"]') || form.querySelector('input[name="lng"]');
        
        if (!latInput) {
            latInput = document.createElement('input');
            latInput.type = 'hidden';
            latInput.name = 'latitude';
            form.appendChild(latInput);
        }
        
        if (!lngInput) {
            lngInput = document.createElement('input');
            lngInput.type = 'hidden';
            lngInput.name = 'longitude';
            form.appendChild(lngInput);
        }
        
        // Also populate user-latitude and user-longitude fields if they exist (for modals)
        const userLatField = document.getElementById('user-latitude');
        const userLngField = document.getElementById('user-longitude');
        
        // Set values if we have user location
        if (userLocation) {
            latInput.value = userLocation.lat;
            lngInput.value = userLocation.lng;
            
            // Update the specific fields if they exist
            if (userLatField) userLatField.value = userLocation.lat;
            if (userLngField) userLngField.value = userLocation.lng;
        } else {
            // Try to get location when form is submitted
            form.addEventListener('submit', async function(e) {
                if (!userLocation) {
                    e.preventDefault();
                    try {
                        const location = await getUserLocation();
                        latInput.value = location.lat;
                        lngInput.value = location.lng;
                        
                        // Update the specific fields if they exist
                        if (userLatField) userLatField.value = location.lat;
                        if (userLngField) userLngField.value = location.lng;
                        
                        form.submit();
                    } catch (error) {
                        alert('Unable to get your location. Please enable location services and try again.');
                    }
                }
            });
        }
    });
}

// Initialize Google Maps for location selection
function initMap(mapElementId, latInputId, lngInputId, initialLat = 0, initialLng = 0) {
    const mapElement = document.getElementById(mapElementId);
    if (!mapElement) return;
    
    const latInput = document.getElementById(latInputId);
    const lngInput = document.getElementById(lngInputId);
    
    // Use initial coordinates or default to user location
    let lat = initialLat || (userLocation ? userLocation.lat : 0);
    let lng = initialLng || (userLocation ? userLocation.lng : 0);
    
    // If we have values in the inputs, use those
    if (latInput.value && lngInput.value) {
        lat = parseFloat(latInput.value);
        lng = parseFloat(lngInput.value);
    }
    
    const map = new google.maps.Map(mapElement, {
        center: { lat, lng },
        zoom: 15
    });
    
    // Add a marker at the center
    let marker = new google.maps.Marker({
        position: { lat, lng },
        map: map,
        draggable: true
    });
    
    // Update input fields when marker is dragged
    google.maps.event.addListener(marker, 'dragend', function() {
        const position = marker.getPosition();
        latInput.value = position.lat();
        lngInput.value = position.lng();
    });
    
    // Allow clicking on map to move marker
    google.maps.event.addListener(map, 'click', function(event) {
        marker.setPosition(event.latLng);
        latInput.value = event.latLng.lat();
        lngInput.value = event.latLng.lng();
    });
    
    // Add search box to the map
    const input = document.createElement('input');
    input.className = 'map-search-box';
    input.type = 'text';
    input.placeholder = 'Search for a location';
    
    const searchBox = new google.maps.places.SearchBox(input);
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
    
    // Bias the SearchBox results towards current map's viewport
    map.addListener('bounds_changed', function() {
        searchBox.setBounds(map.getBounds());
    });
    
    searchBox.addListener('places_changed', function() {
        const places = searchBox.getPlaces();
        
        if (places.length === 0) return;
        
        const place = places[0];
        
        if (!place.geometry || !place.geometry.location) {
            console.log("Returned place contains no geometry");
            return;
        }
        
        // Update marker and inputs
        marker.setPosition(place.geometry.location);
        latInput.value = place.geometry.location.lat();
        lngInput.value = place.geometry.location.lng();
        
        // Center map on the new location
        map.setCenter(place.geometry.location);
    });
}

// Calculate distance between two points
function calculateDistance(lat1, lng1, lat2, lng2) {
    if (!lat1 || !lng1 || !lat2 || !lng2) return null;
    
    const R = 6371; // Radius of the earth in km
    const dLat = deg2rad(lat2 - lat1);
    const dLng = deg2rad(lng2 - lng1);
    
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
        Math.sin(dLng/2) * Math.sin(dLng/2);
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const distance = R * c; // Distance in km
    
    return distance;
}

function deg2rad(deg) {
    return deg * (Math.PI/180);
}

// Format distance for display
function formatDistance(distance) {
    if (distance === null) return 'Unknown distance';
    
    if (distance < 1) {
        return `${Math.round(distance * 1000)} m`;
    } else {
        return `${distance.toFixed(1)} km`;
    }
}

// When document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize user location
    initUserLocation()
        .then(location => {
            console.log('User location initialized:', location);
            addLocationToForm();
            
            // Add location to search form if it exists
            const searchForm = document.getElementById('search-form');
            if (searchForm) {
                const latInput = document.createElement('input');
                latInput.type = 'hidden';
                latInput.name = 'lat';
                latInput.value = location.lat;
                
                const lngInput = document.createElement('input');
                lngInput.type = 'hidden';
                lngInput.name = 'lng';
                lngInput.value = location.lng;
                
                searchForm.appendChild(latInput);
                searchForm.appendChild(lngInput);
            }
            
            // Initialize locations on search results if available
            const pharmacyDistances = document.querySelectorAll('.pharmacy-distance[data-lat][data-lng]');
            pharmacyDistances.forEach(element => {
                const pharmacyLat = parseFloat(element.getAttribute('data-lat'));
                const pharmacyLng = parseFloat(element.getAttribute('data-lng'));
                
                const distance = calculateDistance(location.lat, location.lng, pharmacyLat, pharmacyLng);
                if (distance !== null) {
                    element.textContent = formatDistance(distance);
                }
            });
        })
        .catch(error => {
            console.error('Error initializing location:', error);
        });
    
    // Initialize map if needed
    const mapElement = document.getElementById('location-map');
    if (mapElement) {
        // The Google Maps script should be loaded for this to work
        if (typeof google !== 'undefined' && google.maps) {
            const latInput = document.getElementById('latitude');
            const lngInput = document.getElementById('longitude');
            
            const initialLat = latInput.value ? parseFloat(latInput.value) : null;
            const initialLng = lngInput.value ? parseFloat(lngInput.value) : null;
            
            initMap('location-map', 'latitude', 'longitude', initialLat, initialLng);
        } else {
            console.error('Google Maps API not loaded');
        }
    }
});
