import math
from django.db.models import Q

def haversine_distance(lat1, lon1, lat2, lon2):
    """Fast distance calculation between two points in kilometers"""
    # Convert to radians once
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Optimized haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat*0.5)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon*0.5)**2
    
    # Earth radius in km
    return 6371 * 2 * math.asin(math.sqrt(a))

def get_nearby_pharmacies_with_medicine(user_lat, user_lon, medicine_query, max_distance_km=50):
    """
    Get pharmacies that have the requested medicine, sorted by distance from user
    """
    from pharmacy.models import Medicine, Pharmacy
    
    # Find medicines matching the query
    medicines = Medicine.objects.filter(
        Q(name__icontains=medicine_query) | Q(description__icontains=medicine_query),
        is_available=True,
        stock_quantity__gt=0
    ).select_related('pharmacy')
    
    # Get unique pharmacies that have the medicine
    pharmacy_distances = []
    seen_pharmacies = set()
    
    for medicine in medicines:
        pharmacy = medicine.pharmacy
        if pharmacy.id in seen_pharmacies or not pharmacy.latitude or not pharmacy.longitude:
            continue
            
        seen_pharmacies.add(pharmacy.id)
        
        # Calculate distance
        distance = haversine_distance(
            user_lat, user_lon,
            float(pharmacy.latitude), float(pharmacy.longitude)
        )
        
        # Only include pharmacies within max distance
        if distance <= max_distance_km:
            pharmacy_distances.append({
                'pharmacy': pharmacy,
                'distance': distance,
                'medicines': medicines.filter(pharmacy=pharmacy)
            })
    
    # Sort by distance
    pharmacy_distances.sort(key=lambda x: x['distance'])
    
    return pharmacy_distances

def get_medicines_by_proximity(user_lat, user_lon, medicine_query, max_distance_km=50):
    """
    Get medicines sorted by pharmacy proximity to user
    """
    from pharmacy.models import Medicine
    
    # Find medicines matching the query
    medicines = Medicine.objects.filter(
        Q(name__icontains=medicine_query) | Q(description__icontains=medicine_query),
        is_available=True,
        stock_quantity__gt=0
    ).select_related('pharmacy')
    
    # Calculate distances and sort
    medicine_distances = []
    
    for medicine in medicines:
        pharmacy = medicine.pharmacy
        if not pharmacy.latitude or not pharmacy.longitude:
            # Add medicines from pharmacies without location at the end
            medicine_distances.append({
                'medicine': medicine,
                'distance': float('inf')
            })
            continue
            
        distance = haversine_distance(
            user_lat, user_lon,
            float(pharmacy.latitude), float(pharmacy.longitude)
        )
        
        if distance <= max_distance_km:
            medicine_distances.append({
                'medicine': medicine,
                'distance': distance
            })
    
    # Sort by distance (nearest first)
    medicine_distances.sort(key=lambda x: x['distance'])
    
    return [item['medicine'] for item in medicine_distances]