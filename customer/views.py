from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from .models import Customer, Prescription, Order, OrderItem, IncidentReport, AdminNotification, Payment
from .chapa_service import ChapaService
from pharmacy.models import Pharmacy, Medicine
from moh.models import MoHOfficer
from .forms import PrescriptionForm, CustomerRegistrationForm, OrderForm, QuickIncidentForm

def home(request):
    """Home page view with search functionality"""
    # Ensure no MoH notifications appear on main homepage
    context = {
        'suppress_moh_notifications': True,
    }
    return render(request, 'home.html', context)

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
            import logging
            logger = logging.getLogger(__name__)
            
            user_lat = float(user_lat)
            user_lon = float(user_lon)
            
            medicines_with_distance = []
            for medicine in medicines:
                pharmacy = medicine.pharmacy
                if pharmacy.latitude and pharmacy.longitude:
                    distance = haversine_distance(
                        user_lat, user_lon,
                        float(pharmacy.latitude), float(pharmacy.longitude)
                    )
                    # Attach distance to medicine object for template display
                    medicine.distance = round(distance, 1)
                    medicines_with_distance.append((medicine, distance))
                    logger.info(f"Medicine: {medicine.name}, Pharmacy: {pharmacy.name}, Distance: {distance:.2f} km")
                else:
                    medicine.distance = None
                    medicines_with_distance.append((medicine, float('inf')))
            
            # Sort by distance (closest first)
            medicines_with_distance.sort(key=lambda x: x[1])
            medicines = [medicine for medicine, distance in medicines_with_distance]
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating distances: {e}")
            # Continue without distance sorting
            pass
    
    context = {
        'query': query,
        'medicines': medicines,
        'user_location': {'lat': user_lat, 'lon': user_lon} if user_lat and user_lon else None,
        'user_has_location': bool(user_lat and user_lon),
    }
    
    return render(request, 'search_results.html', context)

def upload_prescription(request):
    """View for customers to upload prescriptions"""
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.status = 'pending'
            prescription.save()
            
            # Set session variable to show success message
            request.session['prescription_uploaded'] = True
            request.session['prescription_id'] = prescription.id
            
            return redirect('prescription_success')
    else:
        form = PrescriptionForm()
    
    return render(request, 'prescription_upload.html', {'form': form})

def prescription_success(request):
    """Success page after prescription submission"""
    # Check if user just uploaded a prescription
    if not request.session.get('prescription_uploaded'):
        return redirect('upload_prescription')
    
    prescription_id = request.session.get('prescription_id')
    
    # Clear session variables
    if 'prescription_uploaded' in request.session:
        del request.session['prescription_uploaded']
    if 'prescription_id' in request.session:
        del request.session['prescription_id']
    
    context = {
        'prescription_id': prescription_id,
    }
    
    return render(request, 'prescription_success.html', context)

def customer_login(request):
    """Universal login view for all user types"""
    from django.contrib.auth.forms import AuthenticationForm
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Check user type and redirect accordingly
            # 1. Check if user is superuser/admin
            if user.is_superuser or user.is_staff:
                messages.success(request, f'Welcome back, Admin {user.username}!')
                return redirect('/platform-admin/')
            
            # 2. Check if user has customer profile
            try:
                customer = user.customer
                messages.success(request, f'Welcome back, {customer.name}!')
                return redirect('customer_dashboard')
            except:
                pass
            
            # 3. Check if user has pharmacy profile
            try:
                from pharmacy.models import Pharmacy
                pharmacy = Pharmacy.objects.get(user=user)
                messages.success(request, f'Welcome back, {pharmacy.name}!')
                return redirect('pharmacy_dashboard')
            except:
                pass
            
            # 4. Check if user has MoH officer profile
            try:
                moh_officer = MoHOfficer.objects.get(user=user, is_active=True)
                messages.success(request, f'Welcome back, {moh_officer.user.get_full_name()}!')
                return redirect('moh_dashboard')
            except:
                pass
            
            # If no profile found
            messages.error(request, 'Account type not recognized. Please contact support.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'customer/login.html', {'form': form})

def customer_register(request):
    """Customer registration view"""
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    customer = Customer.objects.create(
                        user=user,
                        name=f"{user.first_name} {user.last_name}",
                        email=user.email,
                        phone=form.cleaned_data['phone'],
                        address=form.cleaned_data['address']
                    )
                    
                    login(request, user)
                    messages.success(request, f'Welcome to Ethiopian Pharmacy Platform, {customer.name}!')
                    return redirect('customer_dashboard')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'customer/register.html', {'form': form})

@login_required
def customer_dashboard(request):
    """Customer dashboard view"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found. Please contact support.')
        return redirect('home')
    
    # Get customer's recent orders and prescriptions
    recent_orders = Order.objects.filter(customer=customer).order_by('-created_at')[:5]
    recent_prescriptions = Prescription.objects.filter(
        customer_email=customer.email
    ).order_by('-created_at')[:3]
    
    # Count pending orders
    pending_orders = Order.objects.filter(customer=customer, status='pending').count()
    completed_orders = Order.objects.filter(customer=customer, status='completed').count()
    cancelled_orders = Order.objects.filter(customer=customer, status='cancelled').count()
    
    context = {
        'customer': customer,
        'recent_orders': recent_orders,
        'recent_prescriptions': recent_prescriptions,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
    }
    
    return render(request, 'customer/dashboard.html', context)

@login_required
def place_order(request, medicine_id):
    """Place an order for a specific medicine"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            quantity = int(request.POST.get('quantity', 1))
            
            if quantity > medicine.stock_quantity:
                messages.error(request, f'Only {medicine.stock_quantity} units available in stock.')
                return render(request, 'customer/place_order.html', {
                    'medicine': medicine,
                    'form': form
                })
            
            # Check prescription requirement
            prescription_image = form.cleaned_data.get('prescription_image')
            if medicine.prescription_required and not prescription_image:
                messages.error(request, 'This medicine requires a prescription. Please upload a prescription image.')
                return render(request, 'customer/place_order.html', {
                    'medicine': medicine,
                    'form': form
                })
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                pharmacy=medicine.pharmacy,
                total_amount=medicine.price * quantity,
                status='pending',
                notes=form.cleaned_data.get('notes', ''),
                prescription_image=prescription_image
            )
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                medicine=medicine,
                quantity=quantity,
                price=medicine.price
            )
            
            # Update medicine stock
            medicine.stock_quantity -= quantity
            medicine.save()
            
            messages.success(request, f'Order placed successfully! Order ID: {order.id}')
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm()
    
    context = {
        'medicine': medicine,
        'form': form,
    }
    
    return render(request, 'customer/place_order.html', context)

@login_required
def order_history(request):
    """View order history for customer"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    
    context = {
        'orders': orders,
        'customer': customer,
    }
    
    return render(request, 'customer/order_history.html', context)

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
    
    context = {
        'order': order,
        'order_items': order_items,
        'customer': customer,
    }
    
    return render(request, 'customer/order_detail.html', context)

@login_required
def cancel_order(request, order_id):
    """Cancel an order if it's still pending"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id, customer=customer)
    
    if order.status != 'pending':
        messages.error(request, 'Only pending orders can be cancelled.')
        return redirect('order_detail', order_id=order.id)
    
    # Restore medicine stock
    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        item.medicine.stock_quantity += item.quantity
        item.medicine.save()
    
    # Update order status
    order.status = 'cancelled'
    order.save()
    
    messages.success(request, f'Order {order.id} has been cancelled successfully.')
    return redirect('order_history')

def customer_logout(request):
    """Custom logout view for customer"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def unified_login(request):
    """Unified login view that handles all user types based on credentials"""
    next_url = request.GET.get('next')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Redirect based on user type
            if user.is_superuser:
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('padmin:admin_dashboard')
            elif hasattr(user, 'customer'):
                messages.success(request, f'Welcome back, {user.customer.name}!')
                return redirect('customer_dashboard')
            elif hasattr(user, 'pharmacy'):
                messages.success(request, f'Welcome back, {user.pharmacy.name}!')
                return redirect('pharmacy_dashboard')
            else:
                messages.success(request, f'Welcome back, {user.username}!')
            
            # Handle next parameter
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    # Pass the next parameter to the template
    context = {'next': next_url} if next_url else {}
    return render(request, 'customer/unified_login.html', context)

def quick_report_incident(request):
    """Quick incident reporting form for urgent issues"""
    if request.method == 'POST':
        form = QuickIncidentForm(request.POST)
        if form.is_valid():
            # Create incident report
            incident = IncidentReport.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                category=form.cleaned_data['category'],
                severity=form.cleaned_data['severity'],
                status='open',
                reporter_email=form.cleaned_data.get('contact_email'),
                reported_by=request.user if request.user.is_authenticated else None,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                url_path=request.META.get('HTTP_REFERER', '')
            )
            
            # Create urgent notifications for critical incidents
            if incident.severity == 'critical':
                admin_users = User.objects.filter(is_staff=True)
                for admin in admin_users:
                    AdminNotification.objects.create(
                        notification_type='incident',
                        priority='urgent',
                        title='URGENT: Critical System Issue Reported',
                        message=f'A critical incident has been reported: {incident.title}. Immediate attention required.',
                        recipient=admin,
                        related_incident=incident,
                        action_url=f'/platform-admin/incidents/{incident.id}/'
                    )
            
            messages.success(request, f'Incident report #{incident.id} has been submitted. Our team will investigate shortly.')
            return render(request, 'admin/quick_report_success.html', {'incident': incident})
    else:
        form = QuickIncidentForm()
    
    return render(request, 'admin/quick_report.html', {'form': form})


@login_required
def initiate_payment(request, order_id):
    """Initiate payment for approved order"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id, customer=customer)
    
    # Check if order is approved and payment can be initiated
    if order.status != 'approved':
        messages.error(request, 'Payment can only be initiated for approved orders.')
        return redirect('order_detail', order_id=order.id)
    
    # Check if payment already exists
    if hasattr(order, 'payment'):
        if order.payment.status == 'success':
            messages.info(request, 'This order has already been paid.')
            return redirect('order_detail', order_id=order.id)
        elif order.payment.status == 'pending':
            if order.payment.checkout_url:
                messages.info(request, 'Payment is already in progress. Please complete the existing payment.')
                return redirect(order.payment.checkout_url)
            else:
                # If no checkout URL, reinitialize payment
                messages.info(request, 'Reinitializing payment...')
                order.payment.delete()
    
    # Initialize Chapa payment
    chapa_service = ChapaService()
    
    customer_data = {
        'email': customer.email,
        'first_name': customer.user.first_name if customer.user.first_name else customer.name.split()[0],
        'last_name': customer.user.last_name if customer.user.last_name else customer.name.split()[-1],
        'phone': customer.phone
    }
    
    try:
        result = chapa_service.initialize_payment(order, customer_data)
        
        if result['success']:
            # Check if we're in test mode and redirect appropriately
            checkout_url = result['checkout_url']
            if checkout_url.startswith('https://checkout.chapa.co/test/'):
                # In test mode, simulate successful payment and redirect to success page
                messages.success(request, 'Payment processed successfully (TEST MODE).')
                payment = Payment.objects.get(tx_ref=result['tx_ref'])
                payment.status = 'success'
                payment.paid_at = timezone.now()
                payment.save()
                
                # Update order status to paid
                order.status = 'paid'
                order.save()
                
                return redirect('payment_success', payment_id=payment.id)
            else:
                # Production mode - redirect to actual Chapa checkout
                messages.success(request, 'Payment initialized successfully. You will be redirected to the payment page.')
                return redirect(checkout_url)
        else:
            messages.error(request, f'Payment initialization failed: {result["error"]}')
            return redirect('order_detail', order_id=order.id)
            
    except Exception as e:
        messages.error(request, f'Payment system error: {str(e)}')
        return redirect('order_detail', order_id=order.id)


def payment_callback(request):
    """Handle Chapa payment callback"""
    if request.method == 'GET':
        status = request.GET.get('status')
        tx_ref = request.GET.get('tx_ref')
        trx_ref = request.GET.get('trx_ref')
        
        if not tx_ref:
            messages.error(request, 'Invalid payment callback.')
            return redirect('home')
        
        try:
            payment = Payment.objects.get(tx_ref=tx_ref)
            chapa_service = ChapaService()
            
            # Verify payment with Chapa
            verification_result = chapa_service.verify_payment(tx_ref)
            
            if verification_result['success']:
                verified_data = verification_result['data']
                
                if verified_data.get('status') == 'success' and status == 'success':
                    # Payment successful
                    payment.status = 'success'
                    payment.chapa_tx_ref = trx_ref
                    payment.paid_at = timezone.now()
                    payment.chapa_response = verified_data
                    payment.save()
                    
                    # Update order status to paid
                    payment.order.status = 'paid'
                    payment.order.save()
                    
                    # Create receipt
                    from .models import Receipt
                    receipt, created = Receipt.objects.get_or_create(
                        payment=payment,
                        defaults={
                            'order': payment.order,
                            'customer': payment.order.customer,
                            'pharmacy': payment.order.pharmacy,
                            'receipt_data': {
                                'order_items': [
                                    {
                                        'medicine_name': item.medicine.name,
                                        'quantity': item.quantity,
                                        'price': str(item.price),
                                        'total': str(item.get_total_price())
                                    }
                                    for item in payment.order.items.all()
                                ],
                                'total_amount': str(payment.order.total_amount),
                                'order_date': payment.order.created_at.isoformat(),
                                'payment_method': 'Chapa Payment Gateway',
                            }
                        }
                    )
                    
                    messages.success(request, f'Payment successful! Order #{payment.order.id} has been paid.')
                    return redirect('payment_success', payment_id=payment.id)
                else:
                    # Payment failed
                    payment.status = 'failed'
                    payment.chapa_response = verified_data
                    payment.save()
                    
                    messages.error(request, 'Payment failed. Please try again.')
                    return redirect('order_detail', order_id=payment.order.id)
            else:
                messages.error(request, 'Payment verification failed. Please contact support.')
                return redirect('order_detail', order_id=payment.order.id)
                
        except Payment.DoesNotExist:
            messages.error(request, 'Payment record not found.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Payment processing error: {str(e)}')
            return redirect('home')
    
    return redirect('home')


@login_required
def payment_success(request, payment_id):
    """Payment success page"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    payment = get_object_or_404(Payment, id=payment_id, order__customer=customer)
    
    context = {
        'payment': payment,
        'order': payment.order,
        'customer': customer,
    }
    
    return render(request, 'customer/payment_success.html', context)


def payment_webhook(request):
    """Handle Chapa webhook notifications"""
    if request.method == 'POST':
        try:
            import json
            webhook_data = json.loads(request.body)
            
            chapa_service = ChapaService()
            result = chapa_service.handle_webhook(webhook_data)
            
            if result['success']:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': result['error']}, status=400)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)