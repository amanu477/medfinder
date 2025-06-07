from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from .models import Customer, Prescription, Order, OrderItem, VerificationRequest
from pharmacy.models import Pharmacy, Medicine, MoHPharmacyRecord
from pharmacy.verification_service import MinistryOfHealthVerificationService
from pharmacy.forms import MoHPharmacyForm, MoHLoginForm
from .forms import PrescriptionForm, CustomerRegistrationForm, OrderForm

def home(request):
    """Home page view with search functionality"""
    return render(request, 'home.html')

def search_medicines(request):
    """Search medicines and return results sorted by proximity"""
    query = request.GET.get('query', '')
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lon')
    
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
    
    # If user location is provided, sort by proximity
    if user_lat and user_lon:
        try:
            from .utils import haversine_distance
            user_lat = float(user_lat)
            user_lon = float(user_lon)
            
            # Calculate distances and add to medicines
            medicine_list = []
            for medicine in medicines:
                if medicine.pharmacy.latitude and medicine.pharmacy.longitude:
                    distance = haversine_distance(
                        user_lat, user_lon,
                        float(medicine.pharmacy.latitude),
                        float(medicine.pharmacy.longitude)
                    )
                    medicine.distance = round(distance, 1)
                else:
                    medicine.distance = None  # No location data
                medicine_list.append(medicine)
            
            # Sort by distance (nearest first, None values last)
            medicines = sorted(medicine_list, key=lambda x: x.distance if x.distance is not None else float('inf'))
            
        except (ValueError, ImportError):
            # Fall back to name ordering if location processing fails
            medicines = medicines.order_by('name')
    else:
        medicines = medicines.order_by('name')
    
    return render(request, 'search_results.html', {
        'query': query,
        'medicines': medicines,
        'user_has_location': bool(user_lat and user_lon)
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

def customer_login(request):
    """Custom customer login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user has a customer profile
            try:
                customer = user.customer
                login(request, user)
                messages.success(request, f'Welcome back, {customer.name}!')
                return redirect('customer_dashboard')
            except Customer.DoesNotExist:
                messages.error(request, 'This account is not registered as a customer.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'customer/login.html')

def customer_register(request):
    """Customer registration view"""
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create the user
                user = form.save()
                user.email = form.cleaned_data['email']
                user.save()
                
                # Create the customer profile
                customer = Customer.objects.create(
                    user=user,
                    name=f"{user.first_name} {user.last_name}",
                    email=user.email,
                    phone=form.cleaned_data['phone'],
                    address=form.cleaned_data['address']
                )
                
                # Log the user in
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to our platform.')
                return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'customer/register.html', {'form': form})


@login_required
def customer_dashboard(request):
    """Customer dashboard view"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    # Get recent orders
    recent_orders = Order.objects.filter(customer=customer).order_by('-created_at')[:5]
    
    # Get recent prescriptions
    recent_prescriptions = Prescription.objects.filter(customer=customer).order_by('-created_at')[:5]
    
    # Check for order status notifications
    approved_orders = Order.objects.filter(customer=customer, status='approved').count()
    completed_orders = Order.objects.filter(customer=customer, status='completed').count()
    pending_orders = Order.objects.filter(customer=customer, status='pending').count()
    
    return render(request, 'customer/dashboard.html', {
        'customer': customer,
        'recent_orders': recent_orders,
        'recent_prescriptions': recent_prescriptions,
        'approved_orders': approved_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
    })


@login_required
def place_order(request, medicine_id):
    """Place an order for a specific medicine"""
    medicine = get_object_or_404(Medicine, id=medicine_id, is_available=True)
    
    # Check if medicine is expired
    if medicine.is_expired():
        messages.error(request, 'This medicine has expired and cannot be ordered.')
        return redirect('search_medicines')
    
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1
            messages.error(request, 'Invalid quantity entered.')
        
        if form.is_valid() and quantity > 0:
            # Check stock availability
            if quantity > medicine.stock_quantity:
                messages.error(request, f'Only {medicine.stock_quantity} units available in stock.')
                form = OrderForm()
            else:
                with transaction.atomic():
                    # Create the order
                    order = Order.objects.create(
                        customer=customer,
                        pharmacy=medicine.pharmacy,
                        notes=form.cleaned_data.get('notes', '')
                    )
                    
                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        medicine=medicine,
                        quantity=quantity,
                        price=medicine.price
                    )
                    
                    # Calculate total
                    order.calculate_total()
                    
                    messages.success(request, f'Order placed successfully! Order #{order.id}')
                    return redirect('order_detail', order_id=order.id)
        else:
            if quantity <= 0:
                messages.error(request, 'Please enter a valid quantity.')
    else:
        form = OrderForm()
    
    return render(request, 'customer/place_order.html', {
        'medicine': medicine,
        'form': form
    })


@login_required
def order_history(request):
    """View order history for customer"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    
    return render(request, 'customer/order_history.html', {
        'orders': orders,
        'customer': customer
    })


@login_required
def order_detail(request, order_id):
    """View order details"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id, customer=customer)
    order_items = OrderItem.objects.filter(order=order)
    
    return render(request, 'customer/order_detail.html', {
        'order': order,
        'order_items': order_items
    })


@login_required
def cancel_order(request, order_id):
    """Cancel an order if it's still pending"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id, customer=customer)
    
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'Order #{order.id} has been cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('order_detail', order_id=order.id)


def customer_logout(request):
    """Custom logout view for customer"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def unified_login(request):
    """Unified login view that handles all user types based on credentials"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Check if user is admin/superuser
            if user.is_superuser:
                messages.success(request, 'Welcome to admin dashboard!')
                return redirect('admin_dashboard')
            
            # Check if user has a pharmacy
            try:
                pharmacy = user.pharmacy
                messages.success(request, f'Welcome back, {pharmacy.name}!')
                return redirect('pharmacy_dashboard')
            except:
                pass
            
            # Check if user has a customer profile
            try:
                customer = user.customer
                messages.success(request, f'Welcome back, {customer.name}!')
                return redirect('customer_dashboard')
            except:
                pass
            
            # Default redirect for authenticated users without specific profiles
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'customer/unified_login.html')

# Admin Dashboard Views
def admin_dashboard(request):
    """Admin dashboard with overview of all system components"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    # Get statistics
    from django.db.models import Count, Q
    
    stats = {
        'total_pharmacies': Pharmacy.objects.count(),
        'pending_verifications': Pharmacy.objects.filter(verification_status='pending').count(),
        'verified_pharmacies': Pharmacy.objects.filter(verification_status='verified').count(),
        'rejected_pharmacies': Pharmacy.objects.filter(verification_status='rejected').count(),
        'total_customers': Customer.objects.count(),
        'total_medicines': Medicine.objects.count(),
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_prescriptions': Prescription.objects.count(),
        'pending_prescriptions': Prescription.objects.filter(status='pending').count(),
    }
    
    # Recent activities
    recent_pharmacies = Pharmacy.objects.order_by('-created_at')[:5]
    recent_prescriptions = Prescription.objects.order_by('-created_at')[:5]
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_pharmacies': recent_pharmacies,
        'recent_prescriptions': recent_prescriptions,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'admin/dashboard.html', context)

def admin_pharmacy_list(request):
    """List all pharmacies with filtering and search"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    pharmacies = Pharmacy.objects.all().order_by('-created_at')
    
    # Filter by verification status
    status_filter = request.GET.get('status')
    if status_filter:
        pharmacies = pharmacies.filter(verification_status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        pharmacies = pharmacies.filter(
            Q(name__icontains=search_query) |
            Q(license_number__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    context = {
        'pharmacies': pharmacies,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin/pharmacy_list.html', context)

def admin_verify_pharmacy(request, pharmacy_id):
    """Send verification request to Ministry of Health"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
    
    # Create verification request to MoH
    verification_request = VerificationRequest.objects.create(
        pharmacy=pharmacy,
        requested_by=request.user,
        license_number=pharmacy.license_number,
        pharmacy_name=pharmacy.name,
        owner_name=pharmacy.user.get_full_name() if pharmacy.user else 'Unknown',
        status='pending'
    )
    
    # Run automatic MoH database check
    moh_service = MinistryOfHealthVerificationService()
    moh_data = moh_service.verify_pharmacy(
        pharmacy_name=pharmacy.name,
        license_number=pharmacy.license_number,
        owner_name=pharmacy.user.get_full_name() if pharmacy.user else 'Unknown'
    )
    
    # Store verification results in the request
    verification_request.moh_response = moh_data
    
    # Update status based on automatic verification
    if moh_data['moh_record_found']:
        risk_assessment = moh_data['risk_assessment']
        if risk_assessment['recommendation'] == 'APPROVE':
            verification_request.status = 'approved'
            pharmacy.moh_verification_status = 'verified'
        elif risk_assessment['recommendation'] == 'MANUAL_REVIEW':
            verification_request.status = 'manual_review'
            pharmacy.moh_verification_status = 'manual_review'
        else:
            verification_request.status = 'rejected'
            pharmacy.moh_verification_status = 'failed'
    else:
        verification_request.status = 'rejected'
        pharmacy.moh_verification_status = 'failed'
    
    verification_request.save()
    pharmacy.moh_verification_data = moh_data
    pharmacy.save()
    
    messages.success(request, f'Verification request sent to Ministry of Health for "{pharmacy.name}". Status: {verification_request.get_status_display()}')
    return redirect('admin_pharmacy_detail', pharmacy_id=pharmacy.id)

def admin_approve_pharmacy(request, pharmacy_id):
    """Approve a pharmacy"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
    pharmacy.verification_status = 'verified'
    pharmacy.verified_at = timezone.now()
    pharmacy.save()
    
    messages.success(request, f'Pharmacy "{pharmacy.name}" has been approved successfully.')
    return redirect('admin_pharmacy_list')

def admin_reject_pharmacy(request, pharmacy_id):
    """Reject a pharmacy with reason"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason')
        if rejection_reason:
            pharmacy.verification_status = 'rejected'
            pharmacy.rejection_reason = rejection_reason
            pharmacy.save()
            messages.success(request, f'Pharmacy "{pharmacy.name}" has been rejected.')
            return redirect('admin_pharmacy_list')
        else:
            messages.error(request, 'Please provide a rejection reason.')
    
    context = {'pharmacy': pharmacy}
    return render(request, 'admin/reject_pharmacy.html', context)

def admin_customer_list(request):
    """List all customers"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    customers = Customer.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    context = {
        'customers': customers,
        'search_query': search_query,
    }
    
    return render(request, 'admin/customer_list.html', context)

def admin_medicine_list(request):
    """List all medicines"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    medicines = Medicine.objects.all().select_related('pharmacy').order_by('-created_at')
    
    # Filter by pharmacy
    pharmacy_filter = request.GET.get('pharmacy')
    if pharmacy_filter:
        medicines = medicines.filter(pharmacy_id=pharmacy_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        medicines = medicines.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    pharmacies = Pharmacy.objects.filter(verification_status='verified')
    
    context = {
        'medicines': medicines,
        'pharmacies': pharmacies,
        'pharmacy_filter': pharmacy_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin/medicine_list.html', context)

def admin_order_list(request):
    """List all orders"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    orders = Order.objects.all().select_related('customer', 'pharmacy').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/order_list.html', context)

def admin_prescription_list(request):
    """List all prescriptions"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    prescriptions = Prescription.objects.all().select_related('customer', 'pharmacy').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        prescriptions = prescriptions.filter(status=status_filter)
    
    context = {
        'prescriptions': prescriptions,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/prescription_list.html', context)

def admin_pharmacy_detail(request, pharmacy_id):
    """View detailed pharmacy information with Ministry of Health verification"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
    
    context = {
        'pharmacy': pharmacy,
        'moh_data': pharmacy.moh_verification_data or {},
    }
    
    return render(request, 'admin/pharmacy_detail.html', context)


# Ministry of Health Admin Views (Separate System)
def moh_login(request):
    """Ministry of Health login page"""
    if request.method == 'POST':
        form = MoHLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Simple authentication for MoH officials
            if username == 'moh_admin' and password == 'moh123':
                request.session['moh_authenticated'] = True
                request.session['moh_officer'] = username
                return redirect('moh_dashboard')
            else:
                messages.error(request, 'Invalid Ministry of Health credentials.')
    else:
        form = MoHLoginForm()
    
    return render(request, 'moh/login.html', {'form': form})

def moh_dashboard(request):
    """Ministry of Health dashboard"""
    if not request.session.get('moh_authenticated'):
        return redirect('moh_login')
    
    # Get statistics
    total_pharmacies = MoHPharmacyRecord.objects.count()
    active_pharmacies = MoHPharmacyRecord.objects.filter(status='active').count()
    suspended_pharmacies = MoHPharmacyRecord.objects.filter(status='suspended').count()
    from datetime import date
    expired_licenses = MoHPharmacyRecord.objects.filter(
        expiry_date__lt=date.today()
    ).count()
    
    # Get verification requests from platform admins
    pending_verifications = VerificationRequest.objects.filter(status='pending').count()
    manual_review_requests = VerificationRequest.objects.filter(status='manual_review').count()
    
    # Recent registrations and verification requests
    recent_pharmacies = MoHPharmacyRecord.objects.order_by('-registration_date')[:5]
    recent_verification_requests = VerificationRequest.objects.order_by('-created_at')[:3]
    
    context = {
        'total_pharmacies': total_pharmacies,
        'active_pharmacies': active_pharmacies,
        'suspended_pharmacies': suspended_pharmacies,
        'expired_licenses': expired_licenses,
        'pending_verifications': pending_verifications,
        'manual_review_requests': manual_review_requests,
        'recent_pharmacies': recent_pharmacies,
        'recent_verification_requests': recent_verification_requests,
        'moh_officer': request.session.get('moh_officer', 'Unknown')
    }
    
    return render(request, 'moh/dashboard.html', context)

def moh_pharmacy_list(request):
    """List all pharmacies in MoH database"""
    if not request.session.get('moh_authenticated'):
        return redirect('moh_login')
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    region_filter = request.GET.get('region', '')
    
    pharmacies = MoHPharmacyRecord.objects.all()
    
    if search_query:
        from django.db.models import Q
        pharmacies = pharmacies.filter(
            Q(pharmacy_name__icontains=search_query) |
            Q(license_number__icontains=search_query) |
            Q(owner_name__icontains=search_query)
        )
    
    if status_filter:
        pharmacies = pharmacies.filter(status=status_filter)
    
    if region_filter:
        pharmacies = pharmacies.filter(region=region_filter)
    
    pharmacies = pharmacies.order_by('-registration_date')
    
    context = {
        'pharmacies': pharmacies,
        'search': search_query,
        'status_filter': status_filter,
        'region_filter': region_filter,
        'regions': MoHPharmacyRecord.REGION_CHOICES,
        'statuses': MoHPharmacyRecord.STATUS_CHOICES
    }
    
    return render(request, 'moh/pharmacy_list.html', context)

def moh_add_pharmacy(request):
    """Add new pharmacy to MoH database"""
    if not request.session.get('moh_authenticated'):
        return redirect('moh_login')
    
    if request.method == 'POST':
        form = MoHPharmacyForm(request.POST)
        if form.is_valid():
            pharmacy = form.save(commit=False)
            pharmacy.moh_officer = request.session.get('moh_officer', 'Unknown')
            pharmacy.save()
            messages.success(request, f'Pharmacy "{pharmacy.pharmacy_name}" has been registered in the MoH database.')
            return redirect('moh_pharmacy_list')
    else:
        form = MoHPharmacyForm()
    
    return render(request, 'moh/add_pharmacy.html', {'form': form})

def moh_edit_pharmacy(request, pharmacy_id):
    """Edit pharmacy record in MoH database"""
    if not request.session.get('moh_authenticated'):
        return redirect('moh_login')
    
    pharmacy = get_object_or_404(MoHPharmacyRecord, id=pharmacy_id)
    
    if request.method == 'POST':
        form = MoHPharmacyForm(request.POST, instance=pharmacy)
        if form.is_valid():
            form.save()
            messages.success(request, f'Pharmacy "{pharmacy.pharmacy_name}" has been updated.')
            return redirect('moh_pharmacy_list')
    else:
        form = MoHPharmacyForm(instance=pharmacy)
    
    return render(request, 'moh/edit_pharmacy.html', {'form': form, 'pharmacy': pharmacy})

def moh_delete_pharmacy(request, pharmacy_id):
    """Delete pharmacy record from MoH database"""
    if not request.session.get('moh_authenticated'):
        return redirect('moh_login')
    
    pharmacy = get_object_or_404(MoHPharmacyRecord, id=pharmacy_id)
    
    if request.method == 'POST':
        pharmacy_name = pharmacy.pharmacy_name
        pharmacy.delete()
        messages.success(request, f'Pharmacy "{pharmacy_name}" has been removed from the MoH database.')
        return redirect('moh_pharmacy_list')
    
    return render(request, 'moh/delete_pharmacy.html', {'pharmacy': pharmacy})

def moh_verification_requests(request):
    """View verification requests from platform admins"""
    if not request.session.get('moh_authenticated'):
        return redirect('moh_login')
    
    # Get all verification requests with filtering
    verification_requests = VerificationRequest.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        verification_requests = verification_requests.filter(status=status_filter)
    
    context = {
        'verification_requests': verification_requests,
        'status_filter': status_filter,
        'moh_officer': request.session.get('moh_officer', 'Unknown')
    }
    
    return render(request, 'moh/verification_requests.html', context)

def moh_respond_verification(request, request_id):
    """Respond to a verification request from platform admin"""
    if not request.session.get('moh_authenticated'):
        return redirect('moh_login')
    
    verification_request = get_object_or_404(VerificationRequest, id=request_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        moh_notes = request.POST.get('moh_notes', '')
        
        if action == 'approve':
            verification_request.status = 'approved'
            verification_request.moh_notes = moh_notes
            # Update the associated pharmacy
            verification_request.pharmacy.moh_verification_status = 'verified'
            verification_request.pharmacy.save()
            messages.success(request, f'Verification approved for {verification_request.pharmacy_name}')
            
        elif action == 'reject':
            verification_request.status = 'rejected'
            verification_request.moh_notes = moh_notes
            # Update the associated pharmacy
            verification_request.pharmacy.moh_verification_status = 'failed'
            verification_request.pharmacy.save()
            messages.success(request, f'Verification rejected for {verification_request.pharmacy_name}')
            
        elif action == 'manual_review':
            verification_request.status = 'manual_review'
            verification_request.moh_notes = moh_notes
            # Update the associated pharmacy
            verification_request.pharmacy.moh_verification_status = 'manual_review'
            verification_request.pharmacy.save()
            messages.success(request, f'Verification marked for manual review: {verification_request.pharmacy_name}')
        
        verification_request.save()
        return redirect('moh_verification_requests')
    
    context = {
        'verification_request': verification_request,
        'moh_officer': request.session.get('moh_officer', 'Unknown')
    }
    
    return render(request, 'moh/respond_verification.html', context)

def moh_logout(request):
    """Logout from MoH system"""
    request.session.pop('moh_authenticated', None)
    request.session.pop('moh_officer', None)
    messages.success(request, 'You have been logged out from the Ministry of Health system.')
    return redirect('moh_login')