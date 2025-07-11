from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from customer.models import Order, Customer
from pharmacy.models import Pharmacy
from .models import DeliveryPerson, Delivery, DeliveryTracking, DeliveryNotification, DeliveryZone
from .forms import (
    DeliveryPersonCreationForm, DeliveryPersonForm, DeliveryAssignmentForm,
    DeliveryStatusUpdateForm, DeliveryTrackingForm, CustomerLocationForm,
    CustomerFeedbackForm
)
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def delivery_dashboard(request):
    """Dashboard for delivery personnel"""
    try:
        delivery_person = request.user.deliveryperson
    except DeliveryPerson.DoesNotExist:
        messages.error(request, 'You are not registered as a delivery person.')
        return redirect('home')
    
    # Get current deliveries
    current_deliveries = Delivery.objects.filter(
        delivery_person=delivery_person,
        status__in=['assigned', 'picked_up', 'in_transit']
    ).select_related('order', 'order__customer')
    
    # Get completed deliveries (last 10)
    completed_deliveries = Delivery.objects.filter(
        delivery_person=delivery_person,
        status='delivered'
    ).select_related('order', 'order__customer').order_by('-delivery_time')[:10]
    
    # Get notifications
    notifications = DeliveryNotification.objects.filter(
        recipient_type='delivery_person',
        recipient_id=request.user.id,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'delivery_person': delivery_person,
        'current_deliveries': current_deliveries,
        'completed_deliveries': completed_deliveries,
        'notifications': notifications,
        'stats': {
            'total_deliveries': delivery_person.total_deliveries,
            'current_active': current_deliveries.count(),
            'rating': delivery_person.rating,
        }
    }
    
    return render(request, 'delivery/dashboard.html', context)


@login_required
def pharmacy_delivery_dashboard(request):
    """Dashboard for pharmacy delivery management"""
    try:
        pharmacy = request.user.pharmacy
    except Pharmacy.DoesNotExist:
        messages.error(request, 'You are not registered as a pharmacy.')
        return redirect('home')
    
    # Get pending deliveries (orders that need delivery assignment)
    pending_deliveries = Delivery.objects.filter(
        order__pharmacy=pharmacy,
        status='pending'
    ).select_related('order', 'order__customer')
    
    # Get active deliveries
    active_deliveries = Delivery.objects.filter(
        order__pharmacy=pharmacy,
        status__in=['assigned', 'picked_up', 'in_transit']
    ).select_related('order', 'order__customer', 'delivery_person')
    
    # Get delivery staff
    delivery_staff = DeliveryPerson.objects.filter(pharmacy=pharmacy, is_active=True)
    
    context = {
        'pharmacy': pharmacy,
        'pending_deliveries': pending_deliveries,
        'active_deliveries': active_deliveries,
        'delivery_staff': delivery_staff,
        'stats': {
            'pending_count': pending_deliveries.count(),
            'active_count': active_deliveries.count(),
            'staff_count': delivery_staff.count(),
            'available_staff': delivery_staff.filter(is_available=True).count(),
        }
    }
    
    return render(request, 'delivery/pharmacy_dashboard.html', context)


@login_required
def delivery_management(request):
    """Pharmacy delivery management view"""
    try:
        pharmacy = request.user.pharmacy
    except Pharmacy.DoesNotExist:
        messages.error(request, 'You are not registered as a pharmacy.')
        return redirect('home')
    
    # Get all deliveries for this pharmacy
    deliveries = Delivery.objects.filter(
        order__pharmacy=pharmacy
    ).select_related('order', 'order__customer', 'delivery_person').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)
    
    # Get delivery statistics
    pending_count = deliveries.filter(status='pending').count()
    assigned_count = deliveries.filter(status='assigned').count()
    in_transit_count = deliveries.filter(status='in_transit').count()
    delivered_count = deliveries.filter(status='delivered').count()
    
    # Get delivery staff
    delivery_staff = DeliveryPerson.objects.filter(pharmacy=pharmacy, is_active=True)
    
    context = {
        'pharmacy': pharmacy,
        'deliveries': deliveries,
        'status_filter': status_filter,
        'delivery_staff': delivery_staff,
        'stats': {
            'pending_count': pending_count,
            'assigned_count': assigned_count,
            'in_transit_count': in_transit_count,
            'delivered_count': delivered_count,
            'total_count': deliveries.count(),
        }
    }
    
    return render(request, 'delivery/delivery_management.html', context)


@login_required
def create_delivery_person(request):
    """Create new delivery person account"""
    try:
        pharmacy = request.user.pharmacy
    except Pharmacy.DoesNotExist:
        messages.error(request, 'You are not registered as a pharmacy.')
        return redirect('home')
    
    if request.method == 'POST':
        form = DeliveryPersonCreationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save()
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            # Create delivery person profile
            delivery_person = DeliveryPerson.objects.create(
                user=user,
                pharmacy=pharmacy,
                employee_id=f"DEL{timezone.now().strftime('%Y%m%d%H%M%S')}",
                phone=form.cleaned_data['phone'],
                national_id=form.cleaned_data['national_id'],
                vehicle_type=form.cleaned_data['vehicle_type'],
                vehicle_plate=form.cleaned_data.get('vehicle_plate', ''),
            )
            
            messages.success(request, f'Delivery person {user.get_full_name()} created successfully.')
            return redirect('pharmacy_delivery_dashboard')
    else:
        form = DeliveryPersonCreationForm()
    
    return render(request, 'delivery/create_delivery_person.html', {'form': form})


@login_required
def assign_delivery(request, order_id):
    """Assign delivery to delivery person"""
    try:
        pharmacy = request.user.pharmacy
        order = get_object_or_404(Order, id=order_id, pharmacy=pharmacy)
        
        # Get or create delivery record
        delivery, created = Delivery.objects.get_or_create(
            order=order,
            defaults={
                'customer_address': order.customer.address or 'Address not provided',
                'customer_phone': order.customer.phone,
                'customer_location_lat': order.customer.latitude,
                'customer_location_lon': order.customer.longitude,
            }
        )
        
        if request.method == 'POST':
            form = DeliveryAssignmentForm(request.POST, instance=delivery, pharmacy=pharmacy)
            if form.is_valid():
                delivery = form.save()
                delivery.assign_delivery_person(delivery.delivery_person)
                
                # Update order status
                order.status = 'ready_for_delivery'
                order.save()
                
                messages.success(request, f'Delivery assigned to {delivery.delivery_person.user.get_full_name()}')
                return redirect('pharmacy_delivery_dashboard')
        else:
            form = DeliveryAssignmentForm(instance=delivery, pharmacy=pharmacy)
        
        context = {
            'form': form,
            'order': order,
            'delivery': delivery,
        }
        
        return render(request, 'delivery/assign_delivery.html', context)
        
    except Pharmacy.DoesNotExist:
        messages.error(request, 'You are not registered as a pharmacy.')
        return redirect('home')


@login_required
def delivery_detail(request, delivery_id):
    """View delivery details"""
    delivery = get_object_or_404(Delivery, id=delivery_id)
    
    # Check permissions
    if hasattr(request.user, 'deliveryperson'):
        if delivery.delivery_person != request.user.deliveryperson:
            messages.error(request, 'You do not have permission to view this delivery.')
            return redirect('delivery_dashboard')
    elif hasattr(request.user, 'pharmacy'):
        if delivery.order.pharmacy != request.user.pharmacy:
            messages.error(request, 'You do not have permission to view this delivery.')
            return redirect('pharmacy_delivery_dashboard')
    elif hasattr(request.user, 'customer'):
        if delivery.order.customer != request.user.customer:
            messages.error(request, 'You do not have permission to view this delivery.')
            return redirect('customer_orders')
    else:
        messages.error(request, 'You do not have permission to view this delivery.')
        return redirect('home')
    
    # Get tracking history
    tracking_history = DeliveryTracking.objects.filter(delivery=delivery).order_by('-timestamp')
    
    context = {
        'delivery': delivery,
        'tracking_history': tracking_history,
    }
    
    return render(request, 'delivery/delivery_detail.html', context)


@login_required
def update_delivery_status(request, delivery_id):
    """Update delivery status"""
    try:
        delivery_person = request.user.deliveryperson
        delivery = get_object_or_404(Delivery, id=delivery_id, delivery_person=delivery_person)
        
        if request.method == 'POST':
            form = DeliveryStatusUpdateForm(request.POST, instance=delivery)
            if form.is_valid():
                delivery = form.save()
                
                # Update timestamps based on status
                if delivery.status == 'picked_up' and not delivery.pickup_time:
                    delivery.pickup_time = timezone.now()
                elif delivery.status == 'delivered' and not delivery.delivery_time:
                    # For delivered status, redirect to confirmation page instead of completing immediately
                    return redirect('delivery_confirm_payment', delivery_id=delivery.id)
                
                delivery.save()
                
                # Create notification for customer
                DeliveryNotification.objects.create(
                    delivery=delivery,
                    recipient_type='customer',
                    recipient_id=delivery.order.customer.user.id,
                    message=f"Delivery status updated: {delivery.get_status_display()}",
                    notification_type='status_update'
                )
                
                messages.success(request, 'Delivery status updated successfully.')
                return redirect('delivery_dashboard')
        else:
            form = DeliveryStatusUpdateForm(instance=delivery)
        
        context = {
            'form': form,
            'delivery': delivery,
        }
        
        return render(request, 'delivery/update_status.html', context)
        
    except DeliveryPerson.DoesNotExist:
        messages.error(request, 'You are not registered as a delivery person.')
        return redirect('home')


@login_required
def delivery_confirm_payment(request, delivery_id):
    """Confirm payment and complete delivery"""
    try:
        delivery_person = request.user.deliveryperson
        delivery = get_object_or_404(Delivery, id=delivery_id, delivery_person=delivery_person)
        
        # Check if delivery is ready for confirmation
        if delivery.status != 'in_transit':
            messages.error(request, 'Delivery must be in transit to confirm payment.')
            return redirect('delivery_dashboard')
        
        order = delivery.order
        payment = None
        
        # Get payment information
        try:
            payment = order.payment
        except:
            messages.error(request, 'No payment information found for this order.')
            return redirect('delivery_dashboard')
        
        # Handle payment confirmation
        if request.method == 'POST':
            confirmation_type = request.POST.get('confirmation_type')
            
            if confirmation_type == 'cash_payment':
                # Confirm cash payment received
                if payment.payment_type == 'cash_on_delivery':
                    payment.confirm_cash_payment(delivery_person.user)
                    
                    # Complete delivery
                    delivery.status = 'delivered'
                    delivery.delivery_time = timezone.now()
                    delivery_person.total_deliveries += 1
                    delivery_person.save()
                    delivery.save()
                    
                    # Create tracking entry
                    DeliveryTracking.objects.create(
                        delivery=delivery,
                        latitude=delivery_person.current_location_lat or 9.03,
                        longitude=delivery_person.current_location_lon or 38.76,
                        status='delivered',
                        notes='Cash payment confirmed and delivery completed'
                    )
                    
                    messages.success(request, 'Cash payment confirmed and delivery completed successfully.')
                    return redirect('delivery_dashboard')
                else:
                    messages.error(request, 'This order is not set for cash on delivery.')
                    
            elif confirmation_type == 'online_payment':
                # Confirm online payment (already paid)
                if payment.status == 'success':
                    # Complete delivery
                    delivery.status = 'delivered'
                    delivery.delivery_time = timezone.now()
                    delivery_person.total_deliveries += 1
                    delivery_person.save()
                    delivery.save()
                    
                    # Create tracking entry
                    DeliveryTracking.objects.create(
                        delivery=delivery,
                        latitude=delivery_person.current_location_lat or 9.03,
                        longitude=delivery_person.current_location_lon or 38.76,
                        status='delivered',
                        notes='Online payment verified and delivery completed'
                    )
                    
                    messages.success(request, 'Online payment verified and delivery completed successfully.')
                    return redirect('delivery_dashboard')
                else:
                    messages.error(request, 'Online payment has not been confirmed.')
        
        # Generate QR code data
        qr_data = None
        if payment:
            if payment.payment_type == 'cash_on_delivery':
                qr_data = {
                    'type': 'cash_payment',
                    'order_id': order.id,
                    'amount': str(payment.amount),
                    'currency': payment.currency,
                    'customer_name': order.customer.name,
                    'customer_phone': order.customer.phone,
                    'pharmacy': order.pharmacy.name,
                    'delivery_id': delivery.id,
                    'tracking_number': delivery.tracking_number,
                    'payment_status': 'cash_on_delivery'
                }
            else:
                qr_data = {
                    'type': 'online_payment',
                    'order_id': order.id,
                    'amount': str(payment.amount),
                    'currency': payment.currency,
                    'customer_name': order.customer.name,
                    'pharmacy': order.pharmacy.name,
                    'delivery_id': delivery.id,
                    'tracking_number': delivery.tracking_number,
                    'payment_status': 'paid_online',
                    'transaction_ref': payment.tx_ref
                }
        
        context = {
            'delivery': delivery,
            'order': order,
            'payment': payment,
            'qr_data': json.dumps(qr_data) if qr_data else None,
        }
        
        return render(request, 'delivery/confirm_payment.html', context)
        
    except DeliveryPerson.DoesNotExist:
        messages.error(request, 'You are not registered as a delivery person.')
        return redirect('home')


@csrf_exempt
@login_required
def update_location(request):
    """Update delivery person location via AJAX"""
    if request.method == 'POST':
        try:
            delivery_person = request.user.deliveryperson
            data = json.loads(request.body)
            
            lat = data.get('latitude')
            lon = data.get('longitude')
            
            if lat and lon:
                delivery_person.update_location(lat, lon)
                
                # Update tracking for active deliveries
                active_deliveries = Delivery.objects.filter(
                    delivery_person=delivery_person,
                    status__in=['picked_up', 'in_transit']
                )
                
                for delivery in active_deliveries:
                    DeliveryTracking.objects.create(
                        delivery=delivery,
                        latitude=lat,
                        longitude=lon,
                        status=delivery.status
                    )
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid coordinates'})
                
        except DeliveryPerson.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Not a delivery person'})
        except Exception as e:
            logger.error(f"Error updating location: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def customer_delivery_tracking(request, order_id):
    """Customer delivery tracking page"""
    try:
        customer = request.user.customer
        order = get_object_or_404(Order, id=order_id, customer=customer)
        
        try:
            delivery = Delivery.objects.get(order=order)
        except Delivery.DoesNotExist:
            messages.info(request, 'Delivery has not been assigned yet.')
            return redirect('customer_orders')
        
        # Get tracking history
        tracking_history = DeliveryTracking.objects.filter(delivery=delivery).order_by('-timestamp')
        
        context = {
            'delivery': delivery,
            'tracking_history': tracking_history,
            'order': order,
        }
        
        return render(request, 'delivery/customer_tracking.html', context)
        
    except Customer.DoesNotExist:
        messages.error(request, 'You are not registered as a customer.')
        return redirect('home')


@login_required
def delivery_feedback(request, delivery_id):
    """Customer delivery feedback"""
    try:
        customer = request.user.customer
        delivery = get_object_or_404(Delivery, id=delivery_id, order__customer=customer)
        
        if delivery.status != 'delivered':
            messages.error(request, 'You can only provide feedback for delivered orders.')
            return redirect('customer_delivery_tracking', order_id=delivery.order.id)
        
        if request.method == 'POST':
            form = CustomerFeedbackForm(request.POST, instance=delivery)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank you for your feedback!')
                return redirect('customer_delivery_tracking', order_id=delivery.order.id)
        else:
            form = CustomerFeedbackForm(instance=delivery)
        
        context = {
            'form': form,
            'delivery': delivery,
        }
        
        return render(request, 'delivery/feedback.html', context)
        
    except Customer.DoesNotExist:
        messages.error(request, 'You are not registered as a customer.')
        return redirect('home')


def get_delivery_tracking_data(request, delivery_id):
    """Get delivery tracking data as JSON"""
    delivery = get_object_or_404(Delivery, id=delivery_id)
    
    # Check permissions
    can_access = False
    if hasattr(request.user, 'deliveryperson') and delivery.delivery_person == request.user.deliveryperson:
        can_access = True
    elif hasattr(request.user, 'pharmacy') and delivery.order.pharmacy == request.user.pharmacy:
        can_access = True
    elif hasattr(request.user, 'customer') and delivery.order.customer == request.user.customer:
        can_access = True
    
    if not can_access:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    tracking_points = []
    for point in delivery.tracking_points.all():
        tracking_points.append({
            'lat': float(point.latitude),
            'lon': float(point.longitude),
            'timestamp': point.timestamp.isoformat(),
            'status': point.status
        })
    
    data = {
        'delivery_id': delivery.id,
        'status': delivery.status,
        'tracking_number': delivery.tracking_number,
        'tracking_points': tracking_points,
        'customer_location': {
            'lat': float(delivery.customer_location_lat) if delivery.customer_location_lat else None,
            'lon': float(delivery.customer_location_lon) if delivery.customer_location_lon else None,
        },
        'delivery_person': {
            'name': delivery.delivery_person.user.get_full_name() if delivery.delivery_person else None,
            'phone': delivery.delivery_person.phone if delivery.delivery_person else None,
            'vehicle_type': delivery.delivery_person.vehicle_type if delivery.delivery_person else None,
        } if delivery.delivery_person else None
    }
    
    return JsonResponse(data)

@login_required
def confirm_cash_payment(request, delivery_id):
    """Confirm cash payment received by delivery person"""
    try:
        delivery_person = request.user.deliveryperson
    except DeliveryPerson.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
    
    delivery = get_object_or_404(Delivery, id=delivery_id, delivery_person=delivery_person)
    
    if request.method == 'POST':
        # Check if delivery needs cash payment confirmation
        if delivery.needs_cash_payment_confirmation():
            if delivery.confirm_cash_payment(delivery_person):
                # Update delivery status if payment confirmed
                if delivery.status == 'in_transit':
                    delivery.status = 'delivered'
                    delivery.delivery_time = timezone.now()
                    delivery.save()
                    
                    # Update delivery person stats
                    delivery_person.total_deliveries += 1
                    delivery_person.save()
                    
                    # Update availability
                    delivery_person.update_availability_status()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Cash payment confirmed successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to confirm payment'
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'This delivery does not require cash payment confirmation'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def cash_payment_qr_scanner(request, delivery_id):
    """QR code scanner page for delivery personnel"""
    try:
        delivery_person = request.user.deliveryperson
    except DeliveryPerson.DoesNotExist:
        messages.error(request, 'You are not registered as a delivery person.')
        return redirect('home')
    
    delivery = get_object_or_404(Delivery, id=delivery_id, delivery_person=delivery_person)
    
    # Check if this delivery needs cash payment
    if not delivery.needs_cash_payment_confirmation():
        messages.error(request, 'This delivery does not require cash payment.')
        return redirect('delivery_dashboard')
    
    try:
        payment = delivery.order.payment
        if payment.qr_code_data:
            import json
            qr_data = json.loads(payment.qr_code_data)
        else:
            qr_data = None
    except:
        qr_data = None
    
    context = {
        'delivery': delivery,
        'order': delivery.order,
        'payment': payment,
        'qr_data': qr_data,
    }
    
    return render(request, 'delivery/cash_payment_scanner.html', context)