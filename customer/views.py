from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from .models import Customer, Prescription, Order, OrderItem
from pharmacy.models import Pharmacy, Medicine
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


# Removed location-based API endpoints as requested