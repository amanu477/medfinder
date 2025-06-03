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
    
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        quantity = int(request.POST.get('quantity', 1))
        
        if form.is_valid() and quantity > 0:
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


# Removed location-based API endpoints as requested