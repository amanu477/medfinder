from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Pharmacy, Medicine
from .forms import PharmacyRegistrationForm, MedicineForm, PharmacyProfileForm
from core.models import Prescription

@ensure_csrf_cookie
def pharmacy_login(request):
    """Custom login view for pharmacies that handles CSRF better"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'redirect': '/pharmacy/dashboard/'})
                return redirect('pharmacy_dashboard')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        form = AuthenticationForm()
    
    return render(request, 'pharmacy/login.html', {'form': form})

@ensure_csrf_cookie
def register(request):
    """Register a new pharmacy"""
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        pharmacy_form = PharmacyRegistrationForm(request.POST)
        
        if user_form.is_valid() and pharmacy_form.is_valid():
            user = user_form.save()
            pharmacy = pharmacy_form.save(commit=False)
            pharmacy.user = user
            
            # Set lat/lng directly
            pharmacy.latitude = float(request.POST.get('latitude'))
            pharmacy.longitude = float(request.POST.get('longitude'))
            pharmacy.save()
            
            # Log the user in
            username = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            
            return redirect('pharmacy_dashboard')
    else:
        user_form = UserCreationForm()
        pharmacy_form = PharmacyRegistrationForm()
    
    return render(request, 'pharmacy/register.html', {
        'user_form': user_form,
        'pharmacy_form': pharmacy_form
    })

@login_required
def dashboard(request):
    """Pharmacy dashboard"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    
    # Get all medicines for this pharmacy
    medicines = Medicine.objects.filter(pharmacy=pharmacy)
    
    # Get expiring medicines
    expiring_medicines = pharmacy.get_expiring_medicines()
    
    # Get prescriptions for this pharmacy
    prescriptions = Prescription.objects.filter(pharmacy=pharmacy).order_by('-created_at')
    
    # Count of pending prescriptions
    pending_count = prescriptions.filter(status='pending').count()
    
    return render(request, 'pharmacy/dashboard.html', {
        'pharmacy': pharmacy,
        'medicines': medicines,
        'expiring_medicines': expiring_medicines,
        'prescriptions': prescriptions,
        'pending_count': pending_count
    })

@login_required
def medicine_list(request):
    """List all medicines for a pharmacy"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    medicines = Medicine.objects.filter(pharmacy=pharmacy).order_by('-created_at')
    
    return render(request, 'pharmacy/medicine_list.html', {
        'medicines': medicines
    })

@login_required
@ensure_csrf_cookie
def add_medicine(request):
    """Add a new medicine"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.pharmacy = pharmacy
            medicine.save()
            messages.success(request, 'Medicine added successfully!')
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    
    return render(request, 'pharmacy/medicine_form.html', {
        'form': form,
        'action': 'Add'
    })

@login_required
@ensure_csrf_cookie
def edit_medicine(request, medicine_id):
    """Edit an existing medicine"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    medicine = get_object_or_404(Medicine, id=medicine_id, pharmacy=pharmacy)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully!')
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    
    return render(request, 'pharmacy/medicine_form.html', {
        'form': form,
        'medicine': medicine,
        'action': 'Edit'
    })

@login_required
@ensure_csrf_cookie
def delete_medicine(request, medicine_id):
    """Delete a medicine"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    medicine = get_object_or_404(Medicine, id=medicine_id, pharmacy=pharmacy)
    
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully!')
        return redirect('medicine_list')
    
    return render(request, 'pharmacy/delete_confirm.html', {
        'medicine': medicine
    })

@login_required
@ensure_csrf_cookie
def pharmacy_profile(request):
    """Edit pharmacy profile"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    
    if request.method == 'POST':
        form = PharmacyProfileForm(request.POST, instance=pharmacy)
        if form.is_valid():
            updated_pharmacy = form.save(commit=False)
            
            # Update location if coordinates provided
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat and lng:
                updated_pharmacy.latitude = float(lat)
                updated_pharmacy.longitude = float(lng)
            
            updated_pharmacy.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('pharmacy_dashboard')
    else:
        form = PharmacyProfileForm(instance=pharmacy)
    
    # Use existing latitude and longitude for the map
    latitude = pharmacy.latitude
    longitude = pharmacy.longitude
    
    return render(request, 'pharmacy/profile.html', {
        'form': form,
        'pharmacy': pharmacy,
        'latitude': latitude,
        'longitude': longitude
    })

@login_required
def prescription_list(request):
    """List prescriptions for a pharmacy"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    prescriptions = Prescription.objects.filter(pharmacy=pharmacy).order_by('-created_at')
    
    return render(request, 'pharmacy/prescriptions.html', {
        'prescriptions': prescriptions
    })

@login_required
@ensure_csrf_cookie
def update_prescription_status(request, prescription_id):
    """Update prescription status"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    prescription = get_object_or_404(Prescription, id=prescription_id, pharmacy=pharmacy)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in Prescription.STATUS_CHOICES]:
            prescription.status = new_status
            prescription.save()
            messages.success(request, f'Prescription status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('prescription_list')
