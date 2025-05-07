from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from .models import Customer, Prescription
from pharmacy.models import Pharmacy, Medicine
from .forms import PrescriptionForm

def home(request):
    """Home page view with search functionality"""
    return render(request, 'home.html')

def search_medicines(request):
    """Search medicines and return results"""
    query = request.GET.get('query', '')
    
    if not query:
        return render(request, 'search_results.html', {'query': query, 'medicines': []})
    
    # Search for medicines that match the query and are available
    medicines = Medicine.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_available=True,
        pharmacy__is_active=True,
        stock_quantity__gt=0,
        expiry_date__gt=timezone.now().date()
    ).select_related('pharmacy').order_by('name')
    
    return render(request, 'search_results.html', {
        'query': query,
        'medicines': medicines
    })

def upload_prescription(request):
    """View for customers to upload prescriptions"""
    # Get all active pharmacies
    pharmacies = Pharmacy.objects.filter(is_active=True).order_by('name')
    
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
        'pharmacies': pharmacies
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

# Removed location-based API endpoints as requested