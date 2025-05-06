from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from math import radians, cos, sin, asin, sqrt
from .models import Customer, Prescription
from pharmacy.models import Pharmacy, Medicine
from .forms import PrescriptionForm

def home(request):
    """Home page view with search functionality"""
    return render(request, 'home.html')

def search_medicines(request):
    """Search medicines and return results sorted by pharmacy proximity"""
    query = request.GET.get('query', '')
    user_lat = request.GET.get('lat', None)
    user_lng = request.GET.get('lng', None)
    
    if not query:
        return render(request, 'search_results.html', {'query': query, 'medicines': []})
    
    # Search for medicines that match the query and are available
    medicines = Medicine.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_available=True,
        pharmacy__is_active=True,
        stock_quantity__gt=0,
        expiry_date__gt=timezone.now().date()
    ).select_related('pharmacy')
    
    # Calculate distance if user location is provided
    if user_lat and user_lng:
        user_lat = float(user_lat)
        user_lng = float(user_lng)
        
        for medicine in medicines:
            medicine.distance = calculate_distance(
                user_lat, user_lng,
                medicine.pharmacy.latitude, medicine.pharmacy.longitude
            )
        
        # Sort medicines by distance
        medicines = sorted(medicines, key=lambda x: x.distance if hasattr(x, 'distance') else float('inf'))
    
    return render(request, 'search_results.html', {
        'query': query,
        'medicines': medicines,
        'user_lat': user_lat,
        'user_lng': user_lng
    })

def upload_prescription(request):
    """View for customers to upload prescriptions"""
    # Get nearby pharmacies
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    
    pharmacies = Pharmacy.objects.filter(is_active=True)
    
    # Calculate distances if location provided
    if user_lat and user_lng:
        user_lat = float(user_lat)
        user_lng = float(user_lng)
        
        for pharmacy in pharmacies:
            if pharmacy.latitude and pharmacy.longitude:
                pharmacy.distance = calculate_distance(
                    user_lat, user_lng,
                    pharmacy.latitude, pharmacy.longitude
                )
        
        # Sort pharmacies by distance
        pharmacies = sorted(pharmacies, key=lambda x: x.distance if hasattr(x, 'distance') else float('inf'))
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            prescription = form.save(commit=False)
            
            # Associate with pharmacy if provided
            pharmacy_id = request.POST.get('pharmacy_id')
            if pharmacy_id:
                pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
                prescription.pharmacy = pharmacy
            
            # Associate with customer if logged in
            if request.user.is_authenticated and hasattr(request.user, 'customer'):
                prescription.customer = request.user.customer
            
            prescription.save()
            messages.success(request, 'Prescription uploaded successfully!')
            return redirect('prescription_success')
    else:
        form = PrescriptionForm()
    
    return render(request, 'prescription_upload.html', {
        'form': form,
        'pharmacies': pharmacies,
        'user_lat': user_lat,
        'user_lng': user_lng
    })

def prescription_success(request):
    """Success page after prescription submission"""
    # Get the latest prescription for the current user or session
    if request.user.is_authenticated and hasattr(request.user, 'customer'):
        prescription = Prescription.objects.filter(
            customer=request.user.customer
        ).order_by('-created_at').first()
    else:
        # Try to get the last prescription by email from session
        email = request.session.get('prescription_email')
        if email:
            prescription = Prescription.objects.filter(
                customer_email=email
            ).order_by('-created_at').first()
        else:
            # If no prescription found, redirect to home
            messages.warning(request, 'No prescription found.')
            return redirect('home')
    
    return render(request, 'prescription_success.html', {
        'prescription': prescription
    })

@csrf_exempt
def get_nearby_pharmacies(request):
    """API endpoint to get nearby pharmacies based on user's location"""
    if request.method == 'POST':
        lat = float(request.POST.get('lat', 0))
        lng = float(request.POST.get('lng', 0))
        
        if lat and lng:
            pharmacies = Pharmacy.objects.filter(is_active=True)
            pharmacy_list = []
            
            for pharmacy in pharmacies:
                if pharmacy.latitude and pharmacy.longitude:
                    distance = calculate_distance(
                        lat, lng,
                        pharmacy.latitude, pharmacy.longitude
                    )
                    
                    # Only include pharmacies within 20km
                    if distance <= 20:
                        pharmacy_list.append({
                            'id': pharmacy.id,
                            'name': pharmacy.name,
                            'address': pharmacy.address,
                            'phone': pharmacy.phone,
                            'distance': round(distance, 1),
                            'latitude': pharmacy.latitude,
                            'longitude': pharmacy.longitude
                        })
            
            # Sort by distance
            pharmacy_list = sorted(pharmacy_list, key=lambda x: x['distance'])
            
            return JsonResponse({
                'success': True,
                'pharmacies': pharmacy_list
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    return c * r