from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import Pharmacy, Medicine
from .forms import PharmacyRegistrationForm, PharmacyUserForm, MedicineForm, PharmacyProfileForm, PharmacyVerificationForm, PrescriptionReviewForm
from customer.models import Prescription, Order, OrderItem, CartItem
from .license_validation import LicenseValidationService
# Email verification imports removed - only verification codes for registration

def pharmacy_login(request):
    """Pharmacy login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Check if user has pharmacy profile
            try:
                pharmacy = user.pharmacy
                login(request, user)
                messages.success(request, f'Welcome back, {pharmacy.name}!')
                return redirect('pharmacy_dashboard')
            except:
                messages.error(request, 'This account is not registered as a pharmacy. Please register as a pharmacy first.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'pharmacy/login.html', {'form': form})

def register(request):
    """Register a new pharmacy with mandatory document uploads"""
    if request.method == 'POST':
        user_form = PharmacyUserForm(request.POST)
        pharmacy_form = PharmacyRegistrationForm(request.POST, request.FILES)
        
        if user_form.is_valid() and pharmacy_form.is_valid():
            user = user_form.save()
            
            # Create pharmacy profile with uploaded documents
            pharmacy = pharmacy_form.save(commit=False)
            pharmacy.user = user
            
            # Get coordinates if provided
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat and lng:
                pharmacy.latitude = float(lat)
                pharmacy.longitude = float(lng)
            
            # Platform registration is completely separate from MoH
            # No MoH validation during registration - admin will verify later
            pharmacy.verification_status = 'pending'
            pharmacy.save()
            
            # Send registration confirmation email
            # Pharmacy registration completed - no email notifications needed
            
            messages.success(request, 'Registration successful! Your pharmacy has been registered and is pending admin verification.')
            
            # Log the user in automatically and redirect to dashboard
            login(request, user)
            return redirect('pharmacy_dashboard')
        else:
            # Display form errors
            if not pharmacy_form.is_valid():
                for field, errors in pharmacy_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
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
    
    # Get scheduled orders count
    scheduled_orders_count = Order.objects.filter(
        pharmacy=pharmacy,
        is_scheduled=True,
        status='scheduled'
    ).count()
    
    # Calculate totals and statistics
    total_medicines = medicines.count()
    total_orders = orders.count()
    available_medicines = medicines.filter(stock_quantity__gt=0).count()
    
    # Calculate pending deliveries (if delivery system exists)
    try:
        from delivery.models import Delivery
        pending_deliveries = Delivery.objects.filter(
            order__pharmacy=pharmacy,
            status__in=['assigned', 'picked_up', 'in_transit']
        ).count()
    except ImportError:
        pending_deliveries = 0
    
    # Calculate total receipts (if receipts exist)
    try:
        from customer.models import Receipt
        total_receipts = Receipt.objects.filter(
            order__pharmacy=pharmacy
        ).count()
    except ImportError:
        total_receipts = 0
    
    return render(request, 'pharmacy/dashboard.html', {
        'pharmacy': pharmacy,
        'medicines': medicines,
        'total_medicines': total_medicines,
        'available_medicines': available_medicines,
        'expiring_medicines': expiring_medicines,
        'prescriptions': prescriptions,
        'pending_count': pending_count,
        'recent_prescriptions': prescriptions[:5],
        'orders': recent_orders,
        'pending_orders_count': pending_orders_count,
        'scheduled_orders_count': scheduled_orders_count,
        'total_orders': total_orders,
        'pending_deliveries': pending_deliveries,
        'total_receipts': total_receipts,
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
            # Show form errors for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
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
        response_message = request.POST.get('response_message', '')
        
        if new_status in [s[0] for s in Prescription.STATUS_CHOICES]:
            prescription.status = new_status
            prescription.save()
            
            # Send email notification to customer about prescription response
            if response_message:
                # Prescription response sent - no email notifications needed
                pass
            
            messages.success(request, f'Prescription status updated to {new_status}!')
        else:
            messages.error(request, 'Invalid status value!')
    
    return redirect('prescription_list')


@login_required
def order_management(request):
    """View all orders for a pharmacy with OCR results"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    orders = Order.objects.filter(pharmacy=pharmacy).select_related('customer', 'payment').prefetch_related('orderitem_set__medicine').order_by('-created_at')
    
    # Import CartItem to access OCR validation data
    from customer.models import CartItem
    
    # Enhance orders with cart item OCR data
    for order in orders:
        for order_item in order.orderitem_set.all():
            # Find corresponding cart item (with or without OCR validation data)
            try:
                # First try to find cart item with validation data
                cart_item = CartItem.objects.filter(
                    cart__customer=order.customer,
                    medicine=order_item.medicine,
                    validation_data__isnull=False
                ).first()
                
                # If no cart item with validation data, try to find any cart item for this medicine
                if not cart_item:
                    cart_item = CartItem.objects.filter(
                        cart__customer=order.customer,
                        medicine=order_item.medicine
                    ).first()
                
                if cart_item:
                    order_item.cart_item = cart_item
                    # Check if this item requires verification
                    ocr_confidence = cart_item.get_ocr_confidence() if cart_item.validation_data else 0
                    if ocr_confidence < 100:
                        order_item.requires_verification = True
                        # Mark cart item for pharmacy review if not already marked
                        if not cart_item.pharmacy_review_required:
                            cart_item.pharmacy_review_required = True
                            cart_item.pharmacy_review_status = 'pending'
                            cart_item.save()
                    else:
                        order_item.requires_verification = False
                else:
                    order_item.cart_item = None
                    order_item.requires_verification = False
            except Exception as e:
                # If there's an error, default to no cart item
                order_item.cart_item = None
                order_item.requires_verification = False
    
    # Calculate order statistics
    pending_orders = orders.filter(status='pending').count()
    approved_orders = orders.filter(status='approved').count()
    paid_orders = orders.filter(status='paid').count()
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
        'paid_orders': paid_orders,
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
    
    # Check for pending prescription reviews that block order approval
    from customer.models import CartItem
    pending_prescription_reviews = CartItem.objects.filter(
        cart__customer=order.customer,
        medicine__pharmacy=pharmacy,
        pharmacy_review_required=True
    ).exclude(pharmacy_review_status='approved')
    
    return render(request, 'pharmacy/order_detail.html', {
        'order': order,
        'order_items': order_items,
        'pharmacy': pharmacy,
        'pending_prescription_reviews': pending_prescription_reviews
    })


@login_required
def update_order_status(request, order_id):
    """Update order status with mandatory prescription verification for OCR < 100%"""
    pharmacy = get_object_or_404(Pharmacy, user=request.user)
    order = get_object_or_404(Order, id=order_id, pharmacy=pharmacy)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        status_message = request.POST.get('status_message', '')
        
        # Check if order can be approved - require prescription verification for OCR < 100%
        if new_status == 'approved':
            from customer.models import CartItem
            
            # Check if any cart items from this order require prescription verification
            unresolved_prescription_reviews = CartItem.objects.filter(
                cart__customer=order.customer,
                medicine__pharmacy=pharmacy,
                pharmacy_review_required=True
            ).exclude(pharmacy_review_status='approved')
            
            if unresolved_prescription_reviews.exists():
                pending_count = unresolved_prescription_reviews.filter(pharmacy_review_status='pending').count()
                rejected_count = unresolved_prescription_reviews.filter(pharmacy_review_status='rejected').count()
                
                error_msg = f'Cannot approve order! '
                if pending_count > 0:
                    error_msg += f'{pending_count} prescription(s) require manual verification. '
                if rejected_count > 0:
                    error_msg += f'{rejected_count} prescription(s) were rejected. '
                error_msg += 'Please review prescriptions first in Prescription Reviews section.'
                
                messages.error(request, error_msg)
                return redirect('order_detail_pharmacy', order_id=order_id)
        
        if new_status in [s[0] for s in Order.STATUS_CHOICES]:
            old_status = order.status
            order.status = new_status
            order.save()
            
            # Send email notifications to customer
            if order.customer and order.customer.user:
                # Order status updated - no email notifications needed
                pass
            
            # Send order notification to pharmacy when order is placed
            if new_status == 'approved' and old_status != 'approved':
                # Order notification sent - no email notifications needed
                pass
            
            # If order is completed, create delivery and redirect to delivery system
            if new_status == 'completed' and old_status != 'completed':
                from delivery.models import Delivery
                from django.utils import timezone
                import uuid
                
                # Create delivery if it doesn't exist
                delivery, created = Delivery.objects.get_or_create(
                    order=order,
                    defaults={
                        'customer_address': order.customer.address or 'Address not provided',
                        'customer_phone': order.customer.phone,
                        'customer_location_lat': order.customer.latitude,
                        'customer_location_lon': order.customer.longitude,
                        'tracking_number': f"DEL{timezone.now().strftime('%Y%m%d%H%M%S')}{order.id}",
                        'status': 'pending',
                        'pharmacy_notes': f'Order #{order.id} completed and ready for delivery',
                        'estimated_delivery_time': timezone.now() + timezone.timedelta(hours=2),
                        'delivery_fee': 50.00,  # Default delivery fee
                    }
                )
                
                if created:
                    messages.success(request, f'Order #{order.id} completed! Delivery #{delivery.tracking_number} created.')
                    # Redirect to delivery management instead of order management
                    return redirect('delivery_management')
                else:
                    messages.success(request, f'Order #{order.id} status updated to {new_status}!')
            else:
                messages.success(request, f'Order #{order.id} status updated to {new_status}!')
        else:
            messages.error(request, 'Invalid status value!')
    
    return redirect('order_management')


@login_required
def pharmacy_receipts(request):
    """View pharmacy's receipts"""
    try:
        pharmacy = request.user.pharmacy
    except Pharmacy.DoesNotExist:
        messages.error(request, 'Pharmacy profile not found.')
        return redirect('pharmacy_login')
    
    from customer.models import Receipt
    receipts = Receipt.objects.filter(pharmacy=pharmacy).order_by('-generated_at')
    
    context = {
        'receipts': receipts,
        'pharmacy': pharmacy,
    }
    
    return render(request, 'pharmacy/receipts.html', context)


@login_required
def pharmacy_receipt_detail(request, receipt_id):
    """View individual receipt for pharmacy"""
    try:
        pharmacy = request.user.pharmacy
    except Pharmacy.DoesNotExist:
        messages.error(request, 'Pharmacy profile not found.')
        return redirect('pharmacy_login')
    
    from customer.models import Receipt
    receipt = get_object_or_404(Receipt, id=receipt_id, pharmacy=pharmacy)
    receipt.mark_viewed_by_pharmacy()
    
    # Track print action
    if request.GET.get('print') == '1':
        receipt.increment_print_count()
    
    context = {
        'receipt': receipt,
        'pharmacy': pharmacy,
        'payment': receipt.payment,
        'order': receipt.order,
    }
    
    return render(request, 'pharmacy/receipt_detail.html', context)


@login_required
def track_order(request, order_id):
    """Track order delivery status for pharmacy"""
    try:
        pharmacy = request.user.pharmacy
    except Pharmacy.DoesNotExist:
        messages.error(request, 'Pharmacy profile not found.')
        return redirect('pharmacy_login')
    
    # Get the order and verify it belongs to this pharmacy
    order = get_object_or_404(Order, id=order_id, pharmacy=pharmacy)
    
    # Get delivery information if it exists
    from delivery.models import Delivery, DeliveryTracking
    delivery = None
    tracking_history = []
    
    try:
        delivery = Delivery.objects.get(order=order)
        tracking_history = DeliveryTracking.objects.filter(
            delivery=delivery
        ).order_by('-timestamp')
    except Delivery.DoesNotExist:
        pass
    
    context = {
        'order': order,
        'delivery': delivery,
        'tracking_history': tracking_history,
        'pharmacy': pharmacy,
    }
    
    return render(request, 'pharmacy/track_order.html', context)


@login_required
def scheduled_orders(request):
    """View and manage scheduled orders for pharmacy"""
    try:
        pharmacy = request.user.pharmacy
    except Pharmacy.DoesNotExist:
        messages.error(request, 'Pharmacy profile not found.')
        return redirect('pharmacy_login')
    
    # Get all scheduled orders for this pharmacy
    scheduled_orders = Order.objects.filter(
        pharmacy=pharmacy,
        is_scheduled=True,
        status='scheduled'
    ).order_by('scheduled_for')
    
    context = {
        'scheduled_orders': scheduled_orders,
        'pharmacy': pharmacy,
    }
    
    return render(request, 'pharmacy/scheduled_orders.html', context)

@login_required
def approve_scheduled_order(request, order_id):
    """Approve a scheduled order"""
    try:
        pharmacy = request.user.pharmacy
    except Pharmacy.DoesNotExist:
        messages.error(request, 'Pharmacy profile not found.')
        return redirect('pharmacy_login')
    
    order = get_object_or_404(Order, id=order_id, pharmacy=pharmacy, is_scheduled=True)
    
    if request.method == 'POST':
        # Get pharmacy response message
        pharmacy_response = request.POST.get('pharmacy_response', '')
        
        # Update order status
        order.status = 'approved'
        order.pharmacy_response = pharmacy_response
        order.save()
        
        messages.success(request, f'Scheduled order #{order.id} has been approved successfully!')
        return redirect('scheduled_orders')
    
    context = {
        'order': order,
        'pharmacy': pharmacy,
    }
    
    return render(request, 'pharmacy/approve_scheduled_order.html', context)

@login_required
def reject_scheduled_order(request, order_id):
    """Reject a scheduled order"""
    try:
        pharmacy = request.user.pharmacy
    except Pharmacy.DoesNotExist:
        messages.error(request, 'Pharmacy profile not found.')
        return redirect('pharmacy_login')
    
    order = get_object_or_404(Order, id=order_id, pharmacy=pharmacy, is_scheduled=True)
    
    if request.method == 'POST':
        # Get rejection reason
        rejection_reason = request.POST.get('rejection_reason', '')
        
        # Update order status
        order.status = 'rejected'
        order.pharmacy_response = rejection_reason
        order.save()
        
        messages.success(request, f'Scheduled order #{order.id} has been rejected.')
        return redirect('scheduled_orders')
    
    context = {
        'order': order,
        'pharmacy': pharmacy,
    }
    
    return render(request, 'pharmacy/reject_scheduled_order.html', context)

def pharmacy_logout(request):
    """Custom logout view for pharmacy"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def prescription_review_list(request):
    """List prescription images that require pharmacy review"""
    try:
        pharmacy = request.user.pharmacy
    except Pharmacy.DoesNotExist:
        messages.error(request, 'Pharmacy profile not found.')
        return redirect('pharmacy_dashboard')
    
    # Get cart items that require pharmacy review for this pharmacy's medicines
    pending_reviews = CartItem.objects.filter(
        medicine__pharmacy=pharmacy,
        pharmacy_review_required=True,
        pharmacy_review_status='pending'
    ).select_related('cart__customer', 'medicine').order_by('-added_at')
    
    context = {
        'pending_reviews': pending_reviews,
        'review_count': pending_reviews.count()
    }
    
    return render(request, 'pharmacy/prescription_review_list.html', context)

@login_required
def prescription_review_detail(request, cart_item_id):
    """Review individual prescription image and validate medicine"""
    try:
        pharmacy = request.user.pharmacy
    except Pharmacy.DoesNotExist:
        messages.error(request, 'Pharmacy profile not found.')
        return redirect('pharmacy_dashboard')
    
    # Get cart item for this pharmacy's medicine
    cart_item = get_object_or_404(
        CartItem,
        id=cart_item_id,
        medicine__pharmacy=pharmacy,
        pharmacy_review_required=True
    )
    
    if request.method == 'POST':
        form = PrescriptionReviewForm(request.POST, instance=cart_item)
        if form.is_valid():
            # Get additional verification data from form
            prescription_reviewed = form.cleaned_data.get('prescription_image_reviewed')
            medicine_visible = form.cleaned_data.get('medicine_clearly_visible')
            verification_confidence = form.cleaned_data.get('verification_confidence')
            
            # Update cart item with pharmacy review
            cart_item = form.save(commit=False)
            cart_item.reviewed_by = request.user
            cart_item.reviewed_at = timezone.now()
            
            # Store enhanced verification data in validation_data
            if not cart_item.validation_data:
                cart_item.validation_data = {}
            
            cart_item.validation_data.update({
                'pharmacy_verification': {
                    'prescription_image_reviewed': prescription_reviewed,
                    'medicine_clearly_visible': medicine_visible,
                    'verification_confidence': verification_confidence,
                    'reviewed_by': request.user.username,
                    'reviewed_at': timezone.now().isoformat(),
                    'pharmacy_name': request.user.pharmacy.name
                }
            })
            
            cart_item.save()
            
            status_text = "approved" if cart_item.pharmacy_review_status == 'approved' else "rejected"
            
            # Enhanced success message with verification details
            verification_details = f"Medicine visibility: {medicine_visible.title()}, Confidence: {verification_confidence.title()}"
            messages.success(request, 
                f'Prescription review completed with enhanced verification. '
                f'Medicine {cart_item.medicine.name} has been {status_text}. '
                f'Verification details: {verification_details}')
            
            return redirect('prescription_review_list')
    else:
        form = PrescriptionReviewForm(instance=cart_item)
    
    context = {
        'cart_item': cart_item,
        'form': form,
        'ocr_confidence': cart_item.get_ocr_confidence(),
        'ocr_best_match': cart_item.get_ocr_best_match(),
        'validation_data': cart_item.validation_data
    }
    
    return render(request, 'pharmacy/prescription_review_detail.html', context)
