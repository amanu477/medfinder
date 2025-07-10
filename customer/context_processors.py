"""
Context processors for customer app
"""
from django.contrib.auth.models import User
from .models import AdminNotification, Cart


def notification_context(request):
    """
    Add notification context based on user type and current URL path.
    Only show MoH notifications within MoH dashboard area.
    """
    context = {
        'show_moh_notifications': False,
        'show_admin_notifications': False,
        'moh_notifications': [],
        'admin_notifications': [],
        'unread_moh_count': 0,
        'unread_admin_count': 0,
    }
    
    # Check if we're in the MoH area
    is_moh_area = request.path.startswith('/moh/')
    is_admin_area = request.path.startswith('/customer/admin/')
    
    # Only show MoH notifications within MoH dashboard
    if is_moh_area and request.session.get('moh_authenticated'):
        context['show_moh_notifications'] = True
        # Add MoH-specific notification logic here if needed
    
    # Only show admin notifications in admin area for staff users
    if is_admin_area and request.user.is_authenticated and request.user.is_staff:
        context['show_admin_notifications'] = True
        try:
            admin_notifications = AdminNotification.objects.filter(
                recipient=request.user,
                notification_type__in=['pharmacy', 'verification', 'system']
            ).order_by('-created_at')[:5]
            context['admin_notifications'] = admin_notifications
            context['unread_admin_count'] = admin_notifications.filter(is_read=False).count()
        except Exception:
            # Gracefully handle any database errors
            pass
    
    return context


def moh_context(request):
    """
    Add MoH-specific context only for MoH pages
    """
    context = {
        'is_moh_authenticated': False,
        'moh_officer': None,
    }
    
    # Only add MoH context for MoH pages - never for main website
    if request.path.startswith('/moh/'):
        context['is_moh_authenticated'] = request.session.get('moh_authenticated', False)
        context['moh_officer'] = request.session.get('moh_officer', 'Unknown')
    else:
        # Explicitly set to False for non-MoH pages
        context['is_moh_authenticated'] = False
        context['moh_officer'] = None
    
    return context


def cart_context(request):
    """
    Add cart context only for authenticated customers (not pharmacy or delivery users)
    """
    context = {
        'cart_item_count': 0,
        'cart_total': 0,
    }
    
    if request.user.is_authenticated:
        try:
            # Only provide cart context for actual customers
            # Skip if user is pharmacy or delivery person
            if hasattr(request.user, 'pharmacy') or hasattr(request.user, 'deliveryperson'):
                return context
                
            # Check if user has customer profile
            customer = request.user.customer
            cart = Cart.objects.filter(customer=customer).first()
            
            if cart:
                context['cart_item_count'] = cart.get_total_items()
                context['cart_total'] = cart.get_total_amount()
        except:
            # Handle case where user doesn't have customer profile or other errors
            pass
    
    return context