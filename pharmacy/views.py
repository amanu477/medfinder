from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Pharmacy, Medicine
from .forms import PharmacyRegistrationForm, PharmacyUserForm, MedicineForm, PharmacyProfileForm, PharmacyVerificationForm
from customer.models import Prescription, Order, OrderItem

def pharmacy_login(request):
    """Custom login view for pharmacies"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('pharmacy_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'pharmacy/login.html', {'form': form})

def register(request):
    """Register a new pharmacy"""
    if request.method == 'POST':
        user_form = PharmacyUserForm(request.POST)
        pharmacy_form = PharmacyRegistrationForm(request.POST)
        
        if user_form.is_valid() and pharmacy_form.is_valid():
            user = user_form.save()
            
            # Create pharmacy profile
            pharmacy = pharmacy_form.save(commit=False)
            pharmacy.user = user
            
            # Get coordinates if provided
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat and lng:
                pharmacy.latitude = float(lat)
                pharmacy.longitude = float(lng)
            
            pharmacy.save()
            
            # Log the user in automatically and redirect to verification
            login(request, user)
            messages.success(request, 'Registration successful! Please upload verification documents to complete your pharmacy setup.')
            return redirect('pharmacy_verification')
    else:
        user_form = PharmacyUserForm()
        pharmacy_form = PharmacyRegistrationForm()
    
    return render(request, 'pharmacy/register.html', {
        'user_form': user_form,
        'pharmacy_form': pharmacy_form
    })

@login_required
def pharmacy_verification(request):
    """Pharmacy verification document upload"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    
    # Check if already verified
    if pharmacy.verification_status == 'verified':
        messages.info(request, 'Your pharmacy is already verified!')
        return redirect('pharmacy_dashboard')
    
    if request.method == 'POST':
        form = PharmacyVerificationForm(request.POST, request.FILES, instance=pharmacy)
        if form.is_valid():
            pharmacy = form.save(commit=False)
            pharmacy.verification_status = 'pending'
            pharmacy.save()
            
            messages.success(request, 'Verification documents uploaded successfully! Your application is now under review. You will be notified once approved.')
            return redirect('verification_pending')
    else:
        form = PharmacyVerificationForm(instance=pharmacy)
    
    return render(request, 'pharmacy/verification.html', {
        'form': form,
        'pharmacy': pharmacy
    })

@login_required
def verification_pending(request):
    """Show verification pending status"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    
    if pharmacy.verification_status == 'verified':
        return redirect('pharmacy_dashboard')
    
    return render(request, 'pharmacy/verification_pending.html', {
        'pharmacy': pharmacy
    })

@login_required
def dashboard(request):
    """Pharmacy dashboard"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    
    # Check verification status
    if pharmacy.verification_status == 'pending':
        return redirect('verification_pending')
    elif pharmacy.verification_status == 'rejected':
        messages.error(request, f'Your pharmacy verification was rejected. Reason: {pharmacy.rejection_reason or "No specific reason provided."}')
        return redirect('pharmacy_verification')
    elif pharmacy.verification_status != 'verified':
        return redirect('pharmacy_verification')
    
    # Get all medicines for this pharmacy
    medicines = Medicine.objects.filter(pharmacy=pharmacy)
    
    # Get expiring medicines
    expiring_medicines = pharmacy.get_expiring_medicines()
    
    # Get prescriptions for this pharmacy
    prescriptions = Prescription.objects.filter(pharmacy=pharmacy).order_by('-created_at')
    
    # Count of pending prescriptions
    pending_count = prescriptions.filter(status='pending').count()
    
    # Get orders for this pharmacy
    orders = Order.objects.filter(pharmacy=pharmacy).order_by('-created_at')
    pending_orders_count = orders.filter(status='pending').count()
    recent_orders = orders[:5]
    
    # Calculate totals
    total_medicines = medicines.count()
    total_orders = orders.count()
    
    return render(request, 'pharmacy/dashboard.html', {
        'pharmacy': pharmacy,
        'medicines': medicines,
        'total_medicines': total_medicines,
        'expiring_medicines': expiring_medicines,
        'prescriptions': prescriptions,
        'pending_count': pending_count,
        'recent_prescriptions': prescriptions[:5],
        'orders': recent_orders,
        'pending_orders_count': pending_orders_count,
        'total_orders': total_orders,
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
def add_medicine(request):
    """Add a new medicine"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
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
        'title': 'Add Medicine'
    })

@login_required
def edit_medicine(request, medicine_id):
    """Edit an existing medicine"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    medicine = get_object_or_404(Medicine, id=medicine_id, pharmacy=pharmacy)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully!')
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    
    return render(request, 'pharmacy/medicine_form.html', {
        'form': form,
        'title': 'Edit Medicine',
        'medicine': medicine
    })

@login_required
def delete_medicine(request, medicine_id):
    """Delete a medicine"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    medicine = get_object_or_404(Medicine, id=medicine_id, pharmacy=pharmacy)
    
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully!')
        return redirect('medicine_list')
    
    return render(request, 'pharmacy/confirm_delete.html', {
        'medicine': medicine
    })

@login_required
def pharmacy_profile(request):
    """Edit pharmacy profile"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    
    if request.method == 'POST':
        form = PharmacyProfileForm(request.POST, request.FILES, instance=pharmacy)
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
    
    # Calculate statistics
    pending_count = prescriptions.filter(status='pending').count()
    approved_count = prescriptions.filter(status='approved').count()
    rejected_count = prescriptions.filter(status='rejected').count()
    completed_count = prescriptions.filter(status='completed').count()
    
    return render(request, 'pharmacy/prescriptions.html', {
        'prescriptions': prescriptions,
        'pharmacy': pharmacy,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'completed_count': completed_count,
    })

@login_required
def update_prescription_status(request, prescription_id):
    """Update prescription status"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    prescription = get_object_or_404(Prescription, id=prescription_id, pharmacy=pharmacy)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [s[0] for s in Prescription.STATUS_CHOICES]:
            prescription.status = new_status
            prescription.save()
            messages.success(request, f'Prescription status updated to {new_status}!')
        else:
            messages.error(request, 'Invalid status value!')
    
    return redirect('prescription_list')


@login_required
def order_management(request):
    """View all orders for a pharmacy"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    orders = Order.objects.filter(pharmacy=pharmacy).order_by('-created_at')
    
    # Calculate order statistics
    pending_orders = orders.filter(status='pending').count()
    approved_orders = orders.filter(status='approved').count()
    completed_orders = orders.filter(status='completed').count()
    rejected_orders = orders.filter(status='rejected').count()
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    return render(request, 'pharmacy/order_management.html', {
        'orders': orders,
        'pharmacy': pharmacy,
        'status_filter': status_filter,
        'pending_orders': pending_orders,
        'approved_orders': approved_orders,
        'completed_orders': completed_orders,
        'rejected_orders': rejected_orders,
    })


@login_required
def order_detail_pharmacy(request, order_id):
    """View order details for pharmacy"""
    try:
        pharmacy = get_object_or_404(Pharmacy, user=request.user)
    except:
        messages.error(request, 'Pharmacy profile not found.')
        return redirect('pharmacy_login')
    
    order = get_object_or_404(Order, id=order_id, pharmacy=pharmacy)
    order_items = OrderItem.objects.filter(order=order)
    
    return render(request, 'pharmacy/order_detail.html', {
        'order': order,
        'order_items': order_items,
        'pharmacy': pharmacy
    })


@login_required
def update_order_status(request, order_id):
    """Update order status"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    order = get_object_or_404(Order, id=order_id, pharmacy=pharmacy)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [s[0] for s in Order.STATUS_CHOICES]:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {new_status}!')
        else:
            messages.error(request, 'Invalid status value!')
    
    return redirect('order_management')


def pharmacy_logout(request):
    """Custom logout view for pharmacy"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
