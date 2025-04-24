from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
import json
import math

from .models import Customer, Prescription
from pharmacy.models import Pharmacy, Medicine
from .forms import PrescriptionForm

def home(request):
    """Home page view with search functionality"""
    return render(request, 'home.html')

def search_medicines(request):
    """Search medicines and return results sorted by pharmacy proximity"""
    query = request.GET.get('query', '')
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    
    if not query:
        return render(request, 'search_results.html', {'medicines': [], 'query': ''})
    
    # Filter medicines by name (case-insensitive)
    medicines = Medicine.objects.filter(
        Q(name__icontains=query) & 
        Q(is_available=True) & 
        Q(expiry_date__gt=timezone.now().date())
    ).select_related('pharmacy')
    
    # If location is provided, manually calculate distance
    if lat and lng:
        try:
            user_lat = float(lat)
            user_lng = float(lng)
            
            # Get all medicines
            medicines = list(medicines)
            
            # Define a function to calculate distance using Haversine formula
            def calculate_distance(pharmacy_lat, pharmacy_lng):
                # Earth radius in kilometers
                R = 6371.0
                
                # Convert degrees to radians
                lat1_rad = math.radians(user_lat)
                lon1_rad = math.radians(user_lng)
                lat2_rad = math.radians(pharmacy_lat)
                lon2_rad = math.radians(pharmacy_lng)
                
                # Differences
                dlon = lon2_rad - lon1_rad
                dlat = lat2_rad - lat1_rad
                
                # Haversine formula
                a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                distance = R * c
                
                return distance
            
            # Calculate distance for each medicine's pharmacy
            for medicine in medicines:
                if hasattr(medicine.pharmacy, 'latitude') and hasattr(medicine.pharmacy, 'longitude'):
                    medicine.distance = calculate_distance(
                        medicine.pharmacy.latitude, 
                        medicine.pharmacy.longitude
                    )
                else:
                    medicine.distance = float('inf')  # If no coordinates, put at the end
            
            # Sort by distance
            medicines = sorted(medicines, key=lambda m: getattr(m, 'distance', float('inf')))
            
        except (ValueError, TypeError):
            # If conversion fails, just return unsorted results
            pass
    
    return render(request, 'search_results.html', {
        'medicines': medicines,
        'query': query
    })

def upload_prescription(request):
    """View for customers to upload prescriptions via modal forms"""
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            prescription = form.save(commit=False)
            
            # Create or update customer
            customer, created = Customer.objects.get_or_create(
                email=prescription.customer_email,
                defaults={
                    'name': prescription.customer_name,
                    'phone': prescription.customer_phone,
                }
            )
            
            prescription.customer = customer
            
            # Set customer location if provided
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat and lng:
                try:
                    customer.latitude = float(lat)
                    customer.longitude = float(lng)
                    customer.save()
                except (ValueError, TypeError):
                    pass
            
            prescription.save()
            
            # If pharmacy is specified, assign it
            pharmacy_id = request.POST.get('pharmacy_id')
            if pharmacy_id:
                try:
                    pharmacy = Pharmacy.objects.get(id=pharmacy_id)
                    prescription.pharmacy = pharmacy
                    prescription.save()
                except (Pharmacy.DoesNotExist, ValueError):
                    pass
                
            return redirect('prescription_success')
    
    # For non-POST requests, redirect to home
    return redirect('home')

def prescription_success(request):
    """Success page after prescription submission"""
    return render(request, 'prescription_success.html')

@csrf_exempt
def get_nearby_pharmacies(request):
    """API endpoint to get nearby pharmacies based on user's location"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_lat = float(data.get('lat'))
            user_lng = float(data.get('lng'))
            
            # Get all active pharmacies
            pharmacies = Pharmacy.objects.filter(is_active=True)
            
            # Calculate distance for each pharmacy
            pharmacy_distances = []
            for pharmacy in pharmacies:
                # Skip if no coordinates
                if not pharmacy.latitude or not pharmacy.longitude:
                    continue
                
                # Calculate distance using Haversine formula
                # Earth radius in kilometers
                R = 6371.0
                
                # Convert degrees to radians
                lat1_rad = math.radians(user_lat)
                lon1_rad = math.radians(user_lng)
                lat2_rad = math.radians(pharmacy.latitude)
                lon2_rad = math.radians(pharmacy.longitude)
                
                # Differences
                dlon = lon2_rad - lon1_rad
                dlat = lat2_rad - lat1_rad
                
                # Haversine formula
                a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                distance = R * c
                
                pharmacy_distances.append((pharmacy, distance))
            
            # Sort by distance and get top 10
            pharmacy_distances.sort(key=lambda x: x[1])
            nearest_pharmacies = pharmacy_distances[:10]
            
            # Format the results
            results = []
            for pharmacy, distance in nearest_pharmacies:
                results.append({
                    'id': pharmacy.id,
                    'name': pharmacy.name,
                    'address': pharmacy.address,
                    'distance': distance,
                    'phone': pharmacy.phone,
                })
            
            return JsonResponse({'pharmacies': results})
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid location data'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
