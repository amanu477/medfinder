from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import User

from .models import AdminProfile, SystemNotification, PlatformAnalytics, SystemSettings, AdminAuditLog, PlatformReport, MaintenanceMode
from pharmacy.models import Pharmacy, Medicine
from customer.models import Customer, Order, Prescription


def admin_login(request):
    """Admin portal login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user is admin
            try:
                admin_profile = AdminProfile.objects.get(user=user, is_active=True)
                login(request, user)
                return redirect('admin_dashboard')
            except AdminProfile.DoesNotExist:
                messages.error(request, 'Access denied. Admin credentials required.')
        else:
            messages.error(request, 'Invalid credentials.')
    
    return render(request, 'admin_portal/login.html')


@login_required
def admin_dashboard(request):
    """Admin dashboard with system overview"""
    try:
        admin_profile = AdminProfile.objects.get(user=request.user, is_active=True)
    except AdminProfile.DoesNotExist:
        return redirect('admin_login')
    
    # System statistics
    total_users = User.objects.count()
    total_customers = Customer.objects.count()
    total_pharmacies = Pharmacy.objects.count()
    total_medicines = Medicine.objects.count()
    total_orders = Order.objects.count()
    total_prescriptions = Prescription.objects.count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_customers = Customer.objects.filter(created_at__gte=thirty_days_ago).count()
    new_pharmacies = Pharmacy.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_orders = Order.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Active notifications
    active_notifications = SystemNotification.objects.filter(
        is_active=True,
        start_date__lte=timezone.now()
    ).count()
    
    # Maintenance mode status
    maintenance_mode = MaintenanceMode.objects.first()
    
    context = {
        'admin_profile': admin_profile,
        'total_users': total_users,
        'total_customers': total_customers,
        'total_pharmacies': total_pharmacies,
        'total_medicines': total_medicines,
        'total_orders': total_orders,
        'total_prescriptions': total_prescriptions,
        'new_customers': new_customers,
        'new_pharmacies': new_pharmacies,
        'recent_orders': recent_orders,
        'active_notifications': active_notifications,
        'maintenance_mode': maintenance_mode,
    }
    
    return render(request, 'admin_portal/dashboard.html', context)


@login_required
def admin_users(request):
    """Manage users"""
    try:
        admin_profile = AdminProfile.objects.get(user=request.user, is_active=True)
    except AdminProfile.DoesNotExist:
        return redirect('admin_login')
    
    # Filter and search
    search_query = request.GET.get('search', '')
    user_type = request.GET.get('type', '')
    
    users = User.objects.all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    if user_type == 'customers':
        users = users.filter(customer__isnull=False)
    elif user_type == 'pharmacies':
        users = users.filter(pharmacy__isnull=False)
    elif user_type == 'admins':
        users = users.filter(adminprofile__isnull=False)
    
    # Pagination
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'admin_profile': admin_profile,
        'page_obj': page_obj,
        'search_query': search_query,
        'user_type': user_type,
    }
    
    return render(request, 'admin_portal/users.html', context)


@login_required
def admin_pharmacies(request):
    """Manage pharmacies"""
    try:
        admin_profile = AdminProfile.objects.get(user=request.user, is_active=True)
    except AdminProfile.DoesNotExist:
        return redirect('admin_login')
    
    # Filter and search
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    pharmacies = Pharmacy.objects.all()
    
    if search_query:
        pharmacies = pharmacies.filter(
            Q(name__icontains=search_query) |
            Q(license_number__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    if status_filter == 'active':
        pharmacies = pharmacies.filter(is_active=True)
    elif status_filter == 'inactive':
        pharmacies = pharmacies.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(pharmacies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'admin_profile': admin_profile,
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin_portal/pharmacies.html', context)


@login_required
def admin_notifications(request):
    """Manage system notifications"""
    try:
        admin_profile = AdminProfile.objects.get(user=request.user, is_active=True)
    except AdminProfile.DoesNotExist:
        return redirect('admin_login')
    
    if request.method == 'POST':
        # Create new notification
        title = request.POST.get('title')
        message = request.POST.get('message')
        notification_type = request.POST.get('notification_type')
        target_audience = request.POST.get('target_audience')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date') or None
        
        SystemNotification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            target_audience=target_audience,
            start_date=start_date,
            end_date=end_date,
            created_by=request.user,
            is_active=True
        )
        
        messages.success(request, 'Notification created successfully.')
        return redirect('admin_notifications')
    
    # Get existing notifications
    notifications = SystemNotification.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(notifications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'admin_profile': admin_profile,
        'page_obj': page_obj,
        'notification_types': SystemNotification._meta.get_field('notification_type').choices,
        'target_audiences': SystemNotification._meta.get_field('target_audience').choices,
    }
    
    return render(request, 'admin_portal/notifications.html', context)


@login_required
def admin_analytics(request):
    """Platform analytics and reports"""
    try:
        admin_profile = AdminProfile.objects.get(user=request.user, is_active=True)
    except AdminProfile.DoesNotExist:
        return redirect('admin_login')
    
    # Date range filter
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Get analytics data
    analytics = PlatformAnalytics.objects.filter(
        date__range=[start_date, end_date]
    ).order_by('date')
    
    # Calculate totals
    total_new_customers = sum(a.new_customers for a in analytics)
    total_new_pharmacies = sum(a.new_pharmacies for a in analytics)
    total_searches = sum(a.medicine_searches for a in analytics)
    total_prescriptions = sum(a.prescriptions_uploaded for a in analytics)
    total_orders = sum(a.orders_placed for a in analytics)
    
    context = {
        'admin_profile': admin_profile,
        'analytics': analytics,
        'start_date': start_date,
        'end_date': end_date,
        'total_new_customers': total_new_customers,
        'total_new_pharmacies': total_new_pharmacies,
        'total_searches': total_searches,
        'total_prescriptions': total_prescriptions,
        'total_orders': total_orders,
    }
    
    return render(request, 'admin_portal/analytics.html', context)


@login_required
def admin_settings(request):
    """System settings management"""
    try:
        admin_profile = AdminProfile.objects.get(user=request.user, is_active=True)
    except AdminProfile.DoesNotExist:
        return redirect('admin_login')
    
    if request.method == 'POST':
        setting_name = request.POST.get('setting_name')
        setting_value = request.POST.get('setting_value')
        
        if setting_name and setting_value:
            setting, created = SystemSettings.objects.get_or_create(
                setting_name=setting_name,
                defaults={
                    'setting_value': setting_value,
                    'setting_type': 'string',
                    'description': 'Admin configured setting',
                    'updated_by': request.user
                }
            )
            if not created:
                setting.setting_value = setting_value
                setting.updated_by = request.user
                setting.save()
            
            messages.success(request, f'Setting "{setting_name}" updated successfully.')
            return redirect('admin_settings')
    
    # Get all settings
    settings = SystemSettings.objects.all().order_by('setting_name')
    
    context = {
        'admin_profile': admin_profile,
        'settings': settings,
    }
    
    return render(request, 'admin_portal/settings.html', context)


@login_required
def admin_maintenance(request):
    """Maintenance mode control"""
    try:
        admin_profile = AdminProfile.objects.get(user=request.user, is_active=True)
    except AdminProfile.DoesNotExist:
        return redirect('admin_login')
    
    maintenance_mode, created = MaintenanceMode.objects.get_or_create(
        defaults={'created_by': request.user}
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'enable':
            maintenance_mode.is_active = True
            maintenance_mode.title = request.POST.get('title', 'System Maintenance')
            maintenance_mode.message = request.POST.get('message', 'The system is under maintenance.')
            maintenance_mode.estimated_duration = request.POST.get('estimated_duration', '')
            maintenance_mode.save()
            
            messages.success(request, 'Maintenance mode enabled.')
            
        elif action == 'disable':
            maintenance_mode.is_active = False
            maintenance_mode.save()
            
            messages.success(request, 'Maintenance mode disabled.')
    
    context = {
        'admin_profile': admin_profile,
        'maintenance_mode': maintenance_mode,
    }
    
    return render(request, 'admin_portal/maintenance.html', context)


@login_required
def admin_logout(request):
    """Admin logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_login')