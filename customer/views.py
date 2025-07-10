from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from .models import Customer, Prescription, Order, OrderItem, Cart, CartItem, IncidentReport, AdminNotification, Payment
from .chapa_service import ChapaService
from .ocr_service import PrescriptionOCRService
from pharmacy.models import Pharmacy, Medicine
from moh.models import MoHOfficer
from .forms import PrescriptionForm, CustomerRegistrationForm, OrderForm, QuickIncidentForm
import tempfile
import os
import base64
import logging

def home(request):
    """Home page view with search functionality"""
    # Ensure no MoH notifications appear on main homepage
    context = {
        'suppress_moh_notifications': True,
    }
    return render(request, 'home.html', context)

def login_selector(request):
    """Login selector page showing all login options"""
    return render(request, 'login_selector.html')

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
    # Get user location if available
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lon')
    
    # Get all active pharmacies
    pharmacies = Pharmacy.objects.filter(is_active=True, verification_status='verified')
    
    # If user location is provided, sort pharmacies by proximity
    if user_lat and user_lon:
        try:
            from .utils import haversine_distance
            user_lat = float(user_lat)
            user_lon = float(user_lon)
            
            pharmacies_with_distance = []
            for pharmacy in pharmacies:
                if pharmacy.latitude and pharmacy.longitude:
                    distance = haversine_distance(
                        user_lat, user_lon,
                        float(pharmacy.latitude), float(pharmacy.longitude)
                    )
                    pharmacy.distance = round(distance, 1)
                    pharmacies_with_distance.append((pharmacy, distance))
                else:
                    pharmacy.distance = None
                    pharmacies_with_distance.append((pharmacy, float('inf')))
            
            # Sort by distance (closest first)
            pharmacies_with_distance.sort(key=lambda x: x[1])
            pharmacies = [pharmacy for pharmacy, distance in pharmacies_with_distance]
            
        except (ValueError, TypeError) as e:
            logging.error(f"Error calculating pharmacy distances: {e}")
            pass
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            prescription = form.save(commit=False)
            
            # Get selected pharmacy
            pharmacy_id = request.POST.get('pharmacy_id')
            if pharmacy_id:
                try:
                    pharmacy = Pharmacy.objects.get(id=pharmacy_id, is_active=True)
                    prescription.pharmacy = pharmacy
                except Pharmacy.DoesNotExist:
                    messages.error(request, 'Selected pharmacy not found.')
                    return render(request, 'prescription_upload.html', {
                        'form': form, 
                        'pharmacies': pharmacies,
                        'user_location': {'lat': user_lat, 'lon': user_lon} if user_lat and user_lon else None
                    })
            
            prescription.status = 'pending'
            prescription.save()
            
            # Set session variable to show success message
            request.session['prescription_uploaded'] = True
            request.session['prescription_id'] = prescription.id
            
            messages.success(request, 'Prescription uploaded successfully!')
            return redirect('prescription_success')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PrescriptionForm()
        # Pre-fill customer information if user is logged in
        if request.user.is_authenticated:
            try:
                customer = request.user.customer
                form.fields['customer_name'].initial = customer.name
                form.fields['customer_email'].initial = customer.email
                form.fields['customer_phone'].initial = customer.phone
            except:
                pass
    
    context = {
        'form': form,
        'pharmacies': pharmacies,
        'user_location': {'lat': user_lat, 'lon': user_lon} if user_lat and user_lon else None,
        'user_has_location': bool(user_lat and user_lon),
    }
    
    return render(request, 'prescription_upload.html', context)

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
            
            # 4. Check if user has delivery person profile
            try:
                from delivery.models import DeliveryPerson
                delivery_person = DeliveryPerson.objects.get(user=user, is_active=True)
                messages.success(request, f'Welcome back, {delivery_person.user.get_full_name()}!')
                return redirect('delivery_dashboard')
            except:
                pass
            
            # 5. Check if user has MoH officer profile
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
            
            # OCR Validation for prescription images
            ocr_validation_passed = True
            ocr_result = None
            
            if prescription_image:
                try:
                    # Save the uploaded image temporarily for OCR processing
                    import tempfile
                    import os
                    
                    # Create temporary file for OCR processing
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                        for chunk in prescription_image.chunks():
                            temp_file.write(chunk)
                        temp_image_path = temp_file.name
                    
                    # Initialize OCR service
                    ocr_service = PrescriptionOCRService()
                    
                    # Validate medicine name against prescription
                    ocr_result = ocr_service.validate_medicine_name(
                        medicine.name, 
                        temp_image_path, 
                        threshold=60  # Lower threshold for flexibility
                    )
                    
                    # Clean up temporary file
                    os.unlink(temp_image_path)
                    
                    # Check validation result
                    if not ocr_result['is_valid']:
                        ocr_validation_passed = False
                        
                        if ocr_result.get('confidence', 0) > 0:
                            messages.warning(request, 
                                f'OCR Warning: The medicine "{medicine.name}" was not clearly found in the prescription. '
                                f'Best match: "{ocr_result.get("best_match", "None")}" with {ocr_result.get("confidence", 0)}% confidence. '
                                f'Please verify the prescription matches the selected medicine.'
                            )
                        else:
                            messages.warning(request, 
                                f'OCR Warning: Could not verify "{medicine.name}" in the uploaded prescription. '
                                f'Please ensure the prescription image is clear and contains the correct medicine name.'
                            )
                        
                        # Still allow order but with warning
                        ocr_validation_passed = True
                    else:
                        messages.success(request, 
                            f'✓ OCR Verification: Medicine "{medicine.name}" confirmed in prescription '
                            f'(Match: "{ocr_result.get("best_match")}" with {ocr_result.get("confidence")}% confidence)'
                        )
                
                except Exception as e:
                    messages.warning(request, 
                        f'OCR processing encountered an issue: {str(e)}. Order will proceed without OCR validation.'
                    )
                    ocr_validation_passed = True
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                pharmacy=medicine.pharmacy,
                total_amount=medicine.price * quantity,
                status='pending',  # Wait for pharmacy approval
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
            
            messages.success(request, f'Order placed successfully! Waiting for pharmacy approval.')
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
                return redirect('/platform-admin/')
            elif hasattr(user, 'customer'):
                messages.success(request, f'Welcome back, {user.customer.name}!')
                return redirect('customer_dashboard')
            else:
                # Try to get pharmacy
                try:
                    from pharmacy.models import Pharmacy
                    pharmacy = Pharmacy.objects.get(user=user)
                    messages.success(request, f'Welcome back, {pharmacy.name}!')
                    return redirect('pharmacy_dashboard')
                except Pharmacy.DoesNotExist:
                    pass
                
                # Try to get MoH officer
                try:
                    moh_officer = MoHOfficer.objects.get(user=user, is_active=True)
                    messages.success(request, f'Welcome back, {moh_officer.user.get_full_name()}!')
                    return redirect('moh_dashboard')
                except MoHOfficer.DoesNotExist:
                    pass
                
                # Default fallback
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Handle next parameter
                if next_url:
                    return redirect(next_url)
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    # Pass the next parameter to the template
    context = {'next': next_url} if next_url else {}
    return render(request, 'customer/login.html', context)

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
                                for item in payment.order.orderitem_set.all()
                            ],
                            'total_amount': str(payment.order.total_amount),
                            'order_date': payment.order.created_at.isoformat(),
                            'payment_method': 'Chapa Payment Gateway',
                        }
                    }
                )
                
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
                                    for item in payment.order.orderitem_set.all()
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
    
    # Get or create receipt
    from .models import Receipt
    try:
        receipt = Receipt.objects.get(payment=payment)
        receipt.mark_viewed_by_customer()
    except Receipt.DoesNotExist:
        receipt = None
    
    context = {
        'payment': payment,
        'order': payment.order,
        'customer': customer,
        'receipt': receipt,
    }
    
    return render(request, 'customer/payment_success.html', context)


@login_required
def receipt_list(request):
    """View customer's receipts"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    from .models import Receipt
    receipts = Receipt.objects.filter(customer=customer).order_by('-generated_at')
    
    context = {
        'receipts': receipts,
        'customer': customer,
    }
    
    return render(request, 'customer/receipt_list.html', context)


@login_required
def receipt_detail(request, receipt_id):
    """View individual receipt"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    from .models import Receipt
    receipt = get_object_or_404(Receipt, id=receipt_id, customer=customer)
    receipt.mark_viewed_by_customer()
    
    # Track print action
    if request.GET.get('print') == '1':
        receipt.increment_print_count()
    
    context = {
        'receipt': receipt,
        'customer': customer,
        'payment': receipt.payment,
        'order': receipt.order,
    }
    
    return render(request, 'customer/receipt_detail.html', context)


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

@login_required
def prescription_validation_view(request, medicine_id):
    """
    Upload prescription and validate medicine name with OCR
    This comes after medicine search but before order placement
    """
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    if request.method == 'POST':
        prescription_image = request.FILES.get('prescription_image')
        quantity = int(request.POST.get('quantity', 1))
        
        if not prescription_image:
            messages.error(request, 'Please upload a prescription image.')
            return render(request, 'customer/prescription_validation.html', {
                'medicine': medicine,
                'step': 1  # Step 1: Upload prescription
            })
        
        # Process OCR validation
        try:
            # Save uploaded image temporarily for OCR processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                for chunk in prescription_image.chunks():
                    temp_file.write(chunk)
                temp_image_path = temp_file.name
            
            # Initialize OCR service
            ocr_service = PrescriptionOCRService()
            
            # Validate medicine name against prescription
            ocr_result = ocr_service.validate_medicine_name(
                medicine.name, 
                temp_image_path, 
                threshold=60
            )
            
            # Clean up temporary file
            os.unlink(temp_image_path)
            
            # Store results in session for order placement
            request.session['prescription_validation'] = {
                'medicine_id': medicine_id,
                'quantity': quantity,
                'ocr_result': ocr_result,
                'prescription_uploaded': True
            }
            
            # Store the actual prescription image in session (base64 encoded)
            prescription_image.seek(0)  # Reset file pointer
            prescription_data = base64.b64encode(prescription_image.read()).decode('utf-8')
            request.session['prescription_image_data'] = prescription_data
            request.session['prescription_image_name'] = prescription_image.name
            
            context = {
                'medicine': medicine,
                'quantity': quantity,
                'ocr_result': ocr_result,
                'step': 2  # Step 2: Show OCR results
            }
            
            return render(request, 'customer/prescription_validation.html', context)
            
        except Exception as e:
            logger.error(f"OCR validation error: {str(e)}")
            messages.error(request, f'Error processing prescription: {str(e)}')
            return render(request, 'customer/prescription_validation.html', {
                'medicine': medicine,
                'step': 1
            })
    
    # GET request - show prescription upload form
    return render(request, 'customer/prescription_validation.html', {
        'medicine': medicine,
        'step': 1
    })

@login_required
def confirm_order_with_prescription(request, medicine_id):
    """
    Confirm order after prescription validation
    """
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    # Check if prescription validation was completed
    validation_data = request.session.get('prescription_validation')
    if not validation_data or validation_data.get('medicine_id') != medicine_id:
        messages.error(request, 'Please complete prescription validation first.')
        return redirect('prescription_validation', medicine_id=medicine_id)
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    quantity = validation_data.get('quantity', 1)
    ocr_result = validation_data.get('ocr_result')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirm_order':
            # User confirmed they want to proceed with the order
            return create_order_with_prescription(request, medicine, quantity, ocr_result)
        elif action == 'retry_prescription':
            # User wants to upload a different prescription
            # Clear session data
            if 'prescription_validation' in request.session:
                del request.session['prescription_validation']
            if 'prescription_image_data' in request.session:
                del request.session['prescription_image_data']
            if 'prescription_image_name' in request.session:
                del request.session['prescription_image_name']
            
            return redirect('prescription_validation', medicine_id=medicine_id)
    
    # Show order confirmation with OCR results
    context = {
        'medicine': medicine,
        'quantity': quantity,
        'ocr_result': ocr_result,
        'total_price': medicine.price * quantity,
        'step': 3  # Step 3: Order confirmation
    }
    
    return render(request, 'customer/prescription_validation.html', context)

def create_order_with_prescription(request, medicine, quantity, ocr_result):
    """
    Create order with prescription and OCR validation data
    """
    try:
        customer = request.user.customer
        
        # Check stock availability
        if quantity > medicine.stock_quantity:
            messages.error(request, f'Only {medicine.stock_quantity} units available in stock.')
            return redirect('prescription_validation', medicine_id=medicine.id)
        
        # Create order
        with transaction.atomic():
            order = Order.objects.create(
                customer=customer,
                pharmacy=medicine.pharmacy,
                total_amount=medicine.price * quantity,
                status='pending',  # Wait for pharmacy approval
                notes=f'OCR Validation - Confidence: {ocr_result.get("confidence", 0):.1f}%'
            )
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                medicine=medicine,
                quantity=quantity,
                price=medicine.price
            )
            
            # Save prescription image if available
            prescription_image_data = request.session.get('prescription_image_data')
            prescription_image_name = request.session.get('prescription_image_name')
            
            if prescription_image_data and prescription_image_name:
                from django.core.files.base import ContentFile
                
                # Decode base64 image data
                image_data = base64.b64decode(prescription_image_data)
                image_file = ContentFile(image_data, name=prescription_image_name)
                
                # Save to order
                order.prescription_image = image_file
                order.save()
            
            # Update stock
            medicine.stock_quantity -= quantity
            medicine.save()
            
            # Clear session data
            if 'prescription_validation' in request.session:
                del request.session['prescription_validation']
            if 'prescription_image_data' in request.session:
                del request.session['prescription_image_data']
            if 'prescription_image_name' in request.session:
                del request.session['prescription_image_name']
            
            messages.success(request, f'Order #{order.id} placed successfully! Waiting for pharmacy approval.')
            return redirect('order_detail', order_id=order.id)
            
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        messages.error(request, f'Error creating order: {str(e)}')
        return redirect('prescription_validation', medicine_id=medicine.id)

@login_required
def add_to_cart(request, medicine_id):
    """Add medicine to cart with or without prescription"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        prescription_uploaded = request.POST.get('prescription_uploaded')
        skip_prescription = request.POST.get('skip_prescription')
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(customer=customer)
        
        # Check if coming from prescription validation flow
        if prescription_uploaded == 'true':
            # Use data from session (already validated)
            validation_data = request.session.get('prescription_validation')
            prescription_image_data = request.session.get('prescription_image_data')
            prescription_image_name = request.session.get('prescription_image_name')
            
            if validation_data and prescription_image_data:
                ocr_result = validation_data.get('ocr_result')
                
                # Recreate prescription image file
                from django.core.files.base import ContentFile
                image_data = base64.b64decode(prescription_image_data)
                prescription_image = ContentFile(image_data, name=prescription_image_name)
                
                # Check if medicine already in cart
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    medicine=medicine,
                    defaults={
                        'quantity': quantity,
                        'prescription_image': prescription_image,
                        'ocr_validation_data': ocr_result
                    }
                )
                
                if not created:
                    # Update existing cart item
                    cart_item.quantity += quantity
                    cart_item.prescription_image = prescription_image
                    cart_item.ocr_validation_data = ocr_result
                    cart_item.save()
                    messages.success(request, f'Updated {medicine.name} quantity in cart.')
                else:
                    messages.success(request, f'Added {medicine.name} to cart.')
                
                return redirect('cart_view')
            else:
                messages.error(request, 'Please complete prescription validation first.')
                return redirect('prescription_validation', medicine_id=medicine_id)
        
        elif skip_prescription == 'true':
            # Add to cart without prescription (for bulk OCR later)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                medicine=medicine,
                defaults={
                    'quantity': quantity,
                    'prescription_image': None,
                    'ocr_validation_data': None
                }
            )
            
            if not created:
                # Update existing cart item
                cart_item.quantity += quantity
                cart_item.save()
                messages.success(request, f'Updated {medicine.name} quantity in cart.')
            else:
                messages.success(request, f'Added {medicine.name} to cart. You can upload prescriptions later.')
            
            return redirect('cart_view')
        
        else:
            # Direct add to cart (need to process prescription)
            prescription_image = request.FILES.get('prescription_image')
            
            if not prescription_image:
                messages.error(request, 'Please upload a prescription image.')
                return redirect('prescription_validation', medicine_id=medicine_id)
            
            # Process OCR validation first
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                    for chunk in prescription_image.chunks():
                        temp_file.write(chunk)
                    temp_image_path = temp_file.name
                
                ocr_service = PrescriptionOCRService()
                ocr_result = ocr_service.validate_medicine_name(
                    medicine.name, 
                    temp_image_path, 
                    threshold=60
                )
                
                os.unlink(temp_image_path)
                
                # Check if medicine already in cart
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    medicine=medicine,
                    defaults={
                        'quantity': quantity,
                        'prescription_image': prescription_image,
                        'ocr_validation_data': ocr_result
                    }
                )
                
                if not created:
                    # Update existing cart item
                    cart_item.quantity += quantity
                    cart_item.prescription_image = prescription_image
                    cart_item.ocr_validation_data = ocr_result
                    cart_item.save()
                    messages.success(request, f'Updated {medicine.name} quantity in cart.')
                else:
                    messages.success(request, f'Added {medicine.name} to cart.')
                
                return redirect('cart_view')
                
            except Exception as e:
                logger.error(f"Error adding to cart: {str(e)}")
                messages.error(request, f'Error adding to cart: {str(e)}')
                return redirect('prescription_validation', medicine_id=medicine_id)
    
    return redirect('prescription_validation', medicine_id=medicine_id)

@login_required
def cart_view(request):
    """View shopping cart"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    cart, created = Cart.objects.get_or_create(customer=customer)
    cart_items = cart.cartitem_set.all().select_related('medicine', 'medicine__pharmacy')
    
    # Group cart items by pharmacy
    pharmacy_groups = {}
    for item in cart_items:
        pharmacy = item.medicine.pharmacy
        if pharmacy not in pharmacy_groups:
            pharmacy_groups[pharmacy] = []
        pharmacy_groups[pharmacy].append(item)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'pharmacy_groups': pharmacy_groups,
        'total_items': cart.get_total_items(),
        'total_amount': cart.get_total_amount(),
    }
    
    return render(request, 'customer/cart.html', context)

@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    try:
        customer = request.user.customer
        cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=customer)
        
        if request.method == 'POST':
            new_quantity = int(request.POST.get('quantity', 1))
            
            if new_quantity > 0:
                if new_quantity <= cart_item.medicine.stock_quantity:
                    cart_item.quantity = new_quantity
                    cart_item.save()
                    messages.success(request, f'Updated {cart_item.medicine.name} quantity.')
                else:
                    messages.error(request, f'Only {cart_item.medicine.stock_quantity} units available.')
            else:
                messages.error(request, 'Quantity must be greater than 0.')
        
        return redirect('cart_view')
        
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Error updating cart: {str(e)}')
        return redirect('cart_view')

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        customer = request.user.customer
        cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=customer)
        
        medicine_name = cart_item.medicine.name
        cart_item.delete()
        
        messages.success(request, f'Removed {medicine_name} from cart.')
        return redirect('cart_view')
        
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Error removing from cart: {str(e)}')
        return redirect('cart_view')

@login_required
def clear_cart(request):
    """Clear all items from cart"""
    try:
        customer = request.user.customer
        cart = get_object_or_404(Cart, customer=customer)
        
        cart.clear()
        messages.success(request, 'Cart cleared successfully.')
        return redirect('cart_view')
        
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Error clearing cart: {str(e)}')
        return redirect('cart_view')

@login_required
def checkout_cart(request):
    """Convert cart items to orders"""
    logger = logging.getLogger(__name__)
    
    try:
        customer = request.user.customer
        cart = get_object_or_404(Cart, customer=customer)
        cart_items = cart.cartitem_set.all().select_related('medicine', 'medicine__pharmacy')
        
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('cart_view')
        
        # Group cart items by pharmacy to create separate orders
        pharmacy_groups = {}
        for item in cart_items:
            pharmacy = item.medicine.pharmacy
            if pharmacy not in pharmacy_groups:
                pharmacy_groups[pharmacy] = []
            pharmacy_groups[pharmacy].append(item)
        
        created_orders = []
        
        with transaction.atomic():
            for pharmacy, items in pharmacy_groups.items():
                # Calculate total for this pharmacy
                total_amount = sum(item.get_total_price() for item in items)
                
                # Check if any cart item has prescription image
                prescription_image = None
                for item in items:
                    if item.prescription_image:
                        prescription_image = item.prescription_image
                        break
                
                # Create order with prescription image
                order = Order.objects.create(
                    customer=customer,
                    pharmacy=pharmacy,
                    total_amount=total_amount,
                    status='pending',  # Wait for pharmacy approval
                    prescription_image=prescription_image,
                    notes=f'Order created from cart - {len(items)} items{"" if not prescription_image else " (with prescription)"}'
                )
                
                # Create order items
                for cart_item in items:
                    # Check stock availability
                    if cart_item.quantity > cart_item.medicine.stock_quantity:
                        raise Exception(f'Only {cart_item.medicine.stock_quantity} units of {cart_item.medicine.name} available.')
                    
                    OrderItem.objects.create(
                        order=order,
                        medicine=cart_item.medicine,
                        quantity=cart_item.quantity,
                        price=cart_item.medicine.price
                    )
                    
                    # Update stock
                    cart_item.medicine.stock_quantity -= cart_item.quantity
                    cart_item.medicine.save()
                
                created_orders.append(order)
            
            # Clear cart after successful order creation
            cart.clear()
        
        if len(created_orders) == 1:
            messages.success(request, f'Order #{created_orders[0].id} created successfully! Waiting for pharmacy approval.')
            return redirect('order_detail', order_id=created_orders[0].id)
        else:
            messages.success(request, f'Created {len(created_orders)} orders successfully! Waiting for pharmacy approval.')
            return redirect('order_history')
            
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f"Error during checkout: {str(e)}")
        messages.error(request, f'Error during checkout: {str(e)}')
        return redirect('cart_view')

@login_required
def bulk_ocr_verification(request):
    """Bulk OCR verification for all cart items"""
    logger = logging.getLogger(__name__)
    
    try:
        customer = request.user.customer
        cart = get_object_or_404(Cart, customer=customer)
        cart_items = cart.cartitem_set.all().select_related('medicine')
        
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('cart_view')
        
        if request.method == 'POST':
            prescription_image = request.FILES.get('prescription_image')
            
            if not prescription_image:
                messages.error(request, 'Please upload a prescription image.')
                return redirect('bulk_ocr_verification')
            
            # Save prescription image temporarily with proper error handling
            try:
                # Get the file extension from the uploaded file
                file_extension = os.path.splitext(prescription_image.name)[1] or '.jpg'
                
                # Create temporary file with proper extension
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
                temp_image_path = temp_file.name
                
                # Write the uploaded file to temporary location
                for chunk in prescription_image.chunks():
                    temp_file.write(chunk)
                temp_file.close()  # Close the file handle
                
                # Verify the file was created and is readable
                if not os.path.exists(temp_image_path):
                    raise FileNotFoundError(f"Failed to create temporary file: {temp_image_path}")
                
                # Check file size
                file_size = os.path.getsize(temp_image_path)
                if file_size == 0:
                    raise ValueError("Uploaded file is empty")
                
                logger.info(f"Temporary file created successfully: {temp_image_path} (size: {file_size} bytes)")
                
            except Exception as e:
                logger.error(f"Error creating temporary file: {str(e)}")
                messages.error(request, 'Error uploading prescription image. Please try again.')
                return redirect('bulk_ocr_verification')
            
            try:
                ocr_service = PrescriptionOCRService()
                validated_items = []
                failed_items = []
                
                # Process each cart item ONE BY ONE
                total_items = cart_items.count()
                validated_count = 0
                failed_count = 0
                
                logger.info(f"Starting individual medicine validation for {total_items} medicines")
                
                for i, cart_item in enumerate(cart_items, 1):
                    medicine_name = cart_item.medicine.name
                    logger.info(f"Step {i}/{total_items}: Validating '{medicine_name}' in prescription")
                    
                    try:
                        # Validate THIS medicine in the prescription
                        ocr_result = ocr_service.validate_medicine_name(
                            medicine_name, 
                            temp_image_path, 
                            threshold=60
                        )
                        
                        # Log the result for this specific medicine
                        logger.info(f"Medicine '{medicine_name}' validation result: {ocr_result}")
                        
                        # Update cart item with OCR result
                        cart_item.prescription_image = prescription_image
                        cart_item.ocr_validation_data = ocr_result
                        cart_item.save()
                        
                        # Store the prescription image path for later use in order creation
                        if not hasattr(cart_item, '_prescription_file_path'):
                            cart_item._prescription_file_path = temp_image_path
                        
                        if ocr_result.get('is_valid', False):
                            validated_items.append({
                                'name': medicine_name,
                                'confidence': ocr_result.get('confidence', 0),
                                'best_match': ocr_result.get('best_match', 'N/A')
                            })
                            validated_count += 1
                            logger.info(f"✓ Medicine '{medicine_name}' VALIDATED with {ocr_result.get('confidence', 0):.1f}% confidence")
                        else:
                            failed_items.append({
                                'name': medicine_name,
                                'confidence': ocr_result.get('confidence', 0),
                                'best_match': ocr_result.get('best_match', 'N/A')
                            })
                            failed_count += 1
                            logger.info(f"✗ Medicine '{medicine_name}' FAILED validation with {ocr_result.get('confidence', 0):.1f}% confidence")
                    
                    except Exception as e:
                        logger.error(f"Error validating medicine '{medicine_name}': {str(e)}")
                        failed_items.append({
                            'name': medicine_name,
                            'error': str(e),
                            'confidence': 0
                        })
                        failed_count += 1
                        logger.error(f"✗ Medicine '{medicine_name}' ERROR: {str(e)}")
                
                # Clean up temporary file
                try:
                    if os.path.exists(temp_image_path):
                        os.unlink(temp_image_path)
                        logger.info(f"Cleaned up temporary file: {temp_image_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {temp_image_path}: {str(e)}")
                
                # Calculate overall validation percentage
                validation_percentage = (validated_count / total_items) * 100 if total_items > 0 else 0
                
                # Show detailed step-by-step results
                logger.info(f"Final validation results: {validated_count} validated, {failed_count} failed out of {total_items}")
                
                if validated_items:
                    validated_details = []
                    for item in validated_items:
                        validated_details.append(f"{item['name']} ({item['confidence']:.1f}%)")
                    
                    messages.success(
                        request, 
                        f'✓ Successfully validated {validated_count}/{total_items} medicines ({validation_percentage:.1f}%): {", ".join(validated_details)}'
                    )
                
                if failed_items:
                    failed_details = []
                    for item in failed_items:
                        if 'error' in item:
                            failed_details.append(f"{item['name']} (Error)")
                        else:
                            confidence = item.get('confidence', 0)
                            best_match = item.get('best_match', 'N/A')
                            failed_details.append(f"{item['name']} ({confidence:.1f}% - closest: {best_match})")
                    
                    messages.warning(
                        request, 
                        f'⚠ Failed validation for {failed_count}/{total_items} medicines: {", ".join(failed_details)}. '
                        f'Overall validation: {validation_percentage:.1f}%. '
                        f'{"Pharmacy must manually verify prescription for these medicines." if validation_percentage < 100 else ""}'
                    )
                
                # Add pharmacy notification for manual verification if needed
                if validation_percentage < 100:
                    # Group items by pharmacy for notification
                    pharmacy_groups = {}
                    for item in cart_items:
                        pharmacy = item.medicine.pharmacy
                        if pharmacy not in pharmacy_groups:
                            pharmacy_groups[pharmacy] = []
                        pharmacy_groups[pharmacy].append(item)
                    
                    for pharmacy, items in pharmacy_groups.items():
                        pharmacy_failed = [item for item in items if item.medicine.name in [f['name'] for f in failed_items]]
                        if pharmacy_failed:
                            failed_med_names = [item.medicine.name for item in pharmacy_failed]
                            messages.info(
                                request,
                                f'📋 {pharmacy.name}: Manual prescription verification required for: {", ".join(failed_med_names)}. '
                                f'Validation rate: {((len(items) - len(pharmacy_failed)) / len(items)) * 100:.1f}%'
                            )
                
                return redirect('cart_view')
                
            except Exception as e:
                # Clean up temporary file on error
                try:
                    if 'temp_image_path' in locals() and os.path.exists(temp_image_path):
                        os.unlink(temp_image_path)
                        logger.info(f"Cleaned up temporary file after error: {temp_image_path}")
                except:
                    pass
                
                logger.error(f"Error during bulk OCR: {str(e)}")
                messages.error(request, f'Error during bulk OCR verification: {str(e)}')
                return redirect('bulk_ocr_verification')
        
        # Get items without prescription validation
        items_without_prescription = cart_items.filter(prescription_image__isnull=True)
        items_with_prescription = cart_items.filter(prescription_image__isnull=False)
        
        context = {
            'cart_items': cart_items,
            'items_without_prescription': items_without_prescription,
            'items_with_prescription': items_with_prescription,
            'total_items': cart_items.count(),
        }
        
        return render(request, 'customer/bulk_ocr_verification.html', context)
        
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f"Error in bulk OCR verification: {str(e)}")
        messages.error(request, f'Error: {str(e)}')
        return redirect('cart_view')

@login_required
def payment_choice(request, order_id):
    """Show payment method selection page"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id, customer=customer)
    
    # Check if order is eligible for payment
    if order.status != 'approved':
        messages.error(request, 'This order is not approved for payment yet. Please wait for pharmacy approval.')
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'customer/payment_choice.html', {
        'order': order
    })

@login_required
def cash_payment_choice(request, order_id):
    """Handle cash payment selection"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id, customer=customer)
    
    if request.method == 'POST':
        payment_type = request.POST.get('payment_type')
        
        if payment_type == 'cash_on_delivery':
            # Create cash payment record
            try:
                with transaction.atomic():
                    # Generate transaction reference
                    import uuid
                    tx_ref = f"CASH_{uuid.uuid4().hex[:8].upper()}"
                    
                    # Create payment record
                    payment = Payment.objects.create(
                        order=order,
                        tx_ref=tx_ref,
                        amount=order.total_amount,
                        currency='ETB',
                        payment_type='cash_on_delivery',
                        status='cash_pending',
                        customer_email=customer.email,
                        customer_first_name=customer.name.split()[0] if customer.name else '',
                        customer_last_name=' '.join(customer.name.split()[1:]) if len(customer.name.split()) > 1 else '',
                        customer_phone=customer.phone,
                    )
                    
                    # Generate QR code data
                    payment.generate_qr_code_data()
                    
                    # Update order status
                    order.status = 'approved'  # Approved for processing
                    order.save()
                    
                    messages.success(request, 'Cash payment option selected successfully. You will pay when the delivery person arrives.')
                    return render(request, 'customer/cash_payment_confirmation.html', {
                        'order': order,
                        'payment': payment
                    })
                    
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error creating cash payment: {str(e)}")
                messages.error(request, 'Error setting up cash payment. Please try again.')
                return redirect('payment_choice', order_id=order.id)
    
    # If not POST or invalid payment type, redirect back
    return redirect('payment_choice', order_id=order.id)