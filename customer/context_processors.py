"""
Context processors for customer app
"""
from django.contrib.auth.models import User
from .models import AdminNotification


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
    
    # Only add MoH context for MoH pages
    if request.path.startswith('/moh/'):
        context['is_moh_authenticated'] = request.session.get('moh_authenticated', False)
        context['moh_officer'] = request.session.get('moh_officer', 'Unknown')
    
    return context