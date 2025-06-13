from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from .forms import PlatformAdminLoginForm

# Import models from other apps
from pharmacy.models import Pharmacy, Medicine
from customer.models import Customer, Order, OrderItem, Prescription, IncidentReport, SecurityAlert, AdminNotification, VerificationRequest
from moh.models import MoHPharmacyRecord
from pharmacy.verification_service import MinistryOfHealthVerificationService


def admin_login(request):
    """Platform admin login page"""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('padmin:admin_dashboard')
    
    if request.method == 'POST':
        form = PlatformAdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'padmin:admin_dashboard')
            return redirect(next_url)
    else:
        form = PlatformAdminLoginForm()
    
    return render(request, 'platform_admin/login.html', {'form': form})

def admin_logout(request):
    """Platform admin logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('padmin:admin_login')

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
    
    if moh_data['is_verified']:
        pharmacy.verification_status = 'verified'
        pharmacy.moh_verification_data = moh_data
        pharmacy.save()
        verification_request.status = 'approved'
        verification_request.response_notes = 'Automatically verified through MoH database'
        verification_request.save()
        messages.success(request, f'Pharmacy {pharmacy.name} has been automatically verified!')
    else:
        messages.info(request, f'Verification request sent to Ministry of Health for {pharmacy.name}')
    
    return redirect('platform_admin:admin_pharmacy_list')


def admin_approve_pharmacy(request, pharmacy_id):
    """Approve pharmacy manually"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
    pharmacy.verification_status = 'verified'
    pharmacy.save()
    
    messages.success(request, f'Pharmacy {pharmacy.name} has been approved.')
    return redirect('platform_admin:admin_pharmacy_list')


def admin_reject_pharmacy(request, pharmacy_id):
    """Reject pharmacy"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
    pharmacy.verification_status = 'rejected'
    pharmacy.save()
    
    messages.success(request, f'Pharmacy {pharmacy.name} has been rejected.')
    return redirect('platform_admin:admin_pharmacy_list')


def admin_customer_list(request):
    """List all customers with search functionality"""
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
    
    # Pagination
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    customers = paginator.get_page(page_number)
    
    context = {
        'customers': customers,
        'search_query': search_query,
    }
    
    return render(request, 'admin/customer_list.html', context)


def admin_medicine_list(request):
    """List all medicines with search functionality"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    medicines = Medicine.objects.select_related('pharmacy').all().order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        medicines = medicines.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(pharmacy__name__icontains=search_query)
        )
    
    # Filter by pharmacy
    pharmacy_filter = request.GET.get('pharmacy')
    if pharmacy_filter:
        medicines = medicines.filter(pharmacy_id=pharmacy_filter)
    
    pharmacies = Pharmacy.objects.filter(verification_status='verified').order_by('name')
    
    # Pagination
    paginator = Paginator(medicines, 50)
    page_number = request.GET.get('page')
    medicines = paginator.get_page(page_number)
    
    context = {
        'medicines': medicines,
        'pharmacies': pharmacies,
        'search_query': search_query,
        'pharmacy_filter': pharmacy_filter,
    }
    
    return render(request, 'admin/medicine_list.html', context)


def admin_order_list(request):
    """List all orders with filtering"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    orders = Order.objects.select_related('customer').all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            Q(customer__name__icontains=search_query) |
            Q(customer__email__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(orders, 25)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin/order_list.html', context)


def admin_prescription_list(request):
    """List all prescriptions with filtering"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    prescriptions = Prescription.objects.select_related('pharmacy').all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        prescriptions = prescriptions.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        prescriptions = prescriptions.filter(
            Q(customer_name__icontains=search_query) |
            Q(customer_email__icontains=search_query) |
            Q(pharmacy__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(prescriptions, 25)
    page_number = request.GET.get('page')
    prescriptions = paginator.get_page(page_number)
    
    context = {
        'prescriptions': prescriptions,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin/prescription_list.html', context)


# Admin Reporting System Views
def admin_incident_reports(request):
    """View and manage incident reports"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    reports = IncidentReport.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    # Filter by severity
    severity_filter = request.GET.get('severity')
    if severity_filter:
        reports = reports.filter(severity=severity_filter)
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        reports = reports.filter(category=category_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        reports = reports.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(reporter_email__icontains=search_query)
        )
    
    # Statistics for dashboard
    stats = {
        'total_reports': IncidentReport.objects.count(),
        'open_reports': IncidentReport.objects.filter(status='open').count(),
        'in_progress_reports': IncidentReport.objects.filter(status='in_progress').count(),
        'critical_reports': IncidentReport.objects.filter(severity='critical').count(),
        'high_reports': IncidentReport.objects.filter(severity='high').count(),
    }
    
    # Pagination
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    reports = paginator.get_page(page_number)
    
    context = {
        'reports': reports,
        'stats': stats,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
        'category_filter': category_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin/incident_reports.html', context)


def admin_create_incident(request):
    """Create new incident report"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    from customer.forms_reporting import IncidentReportForm
    
    if request.method == 'POST':
        form = IncidentReportForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.created_by = request.user
            incident.save()
            
            # Create admin notification
            AdminNotification.objects.create(
                user=request.user,
                title=f'New Incident Report: {incident.title}',
                message=f'Incident report #{incident.id} has been created.',
                notification_type='incident',
                is_read=False
            )
            
            messages.success(request, 'Incident report created successfully.')
            return redirect('platform_admin:admin_incident_reports')
    else:
        form = IncidentReportForm()
    
    context = {'form': form}
    return render(request, 'admin/create_incident.html', context)


def admin_incident_detail(request, incident_id):
    """View and update incident report details"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    incident = get_object_or_404(IncidentReport, id=incident_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        resolution_notes = request.POST.get('resolution_notes')
        
        if status:
            incident.status = status
        if priority:
            incident.priority = priority
        if resolution_notes:
            incident.resolution_notes = resolution_notes
        
        incident.resolved_by = request.user
        incident.resolved_at = timezone.now() if status == 'resolved' else None
        incident.save()
        
        messages.success(request, 'Incident report updated successfully.')
        return redirect('platform_admin:admin_incident_detail', incident_id=incident.id)
    
    context = {'incident': incident}
    return render(request, 'admin/incident_detail.html', context)


def admin_security_alerts(request):
    """View and manage security alerts"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    alerts = SecurityAlert.objects.all().order_by('-created_at')
    
    # Filter by alert type
    type_filter = request.GET.get('type')
    if type_filter:
        alerts = alerts.filter(alert_type=type_filter)
    
    # Filter by risk level
    risk_filter = request.GET.get('risk')
    if risk_filter:
        alerts = alerts.filter(risk_level=risk_filter)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        alerts = alerts.filter(status=status_filter)
    
    # Statistics
    stats = {
        'total_alerts': SecurityAlert.objects.count(),
        'active_alerts': SecurityAlert.objects.filter(status='active').count(),
        'critical_alerts': SecurityAlert.objects.filter(risk_level='critical').count(),
        'high_alerts': SecurityAlert.objects.filter(risk_level='high').count(),
    }
    
    context = {
        'alerts': alerts,
        'stats': stats,
        'type_filter': type_filter,
        'risk_filter': risk_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/security_alerts.html', context)


def admin_create_security_alert(request):
    """Create new security alert"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    from customer.forms_reporting import SecurityAlertForm
    
    if request.method == 'POST':
        form = SecurityAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.created_by = request.user
            alert.save()
            
            # Create admin notification for high/critical alerts
            if alert.risk_level in ['high', 'critical']:
                AdminNotification.objects.create(
                    user=request.user,
                    title=f'Security Alert: {alert.get_alert_type_display()}',
                    message=f'New {alert.get_risk_level_display()} security alert created.',
                    notification_type='security',
                    is_read=False
                )
            
            messages.success(request, 'Security alert created successfully.')
            return redirect('platform_admin:admin_security_alerts')
    else:
        form = SecurityAlertForm()
    
    context = {'form': form}
    return render(request, 'admin/create_security_alert.html', context)


def admin_notifications(request):
    """View and manage admin notifications"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    notifications = AdminNotification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark as read if requested
    mark_read_id = request.GET.get('mark_read')
    if mark_read_id:
        try:
            notification = AdminNotification.objects.get(id=mark_read_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success'})
        except AdminNotification.DoesNotExist:
            return JsonResponse({'status': 'error'})
    
    # Pagination
    paginator = Paginator(notifications, 25)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    context = {'notifications': notifications}
    return render(request, 'admin/notifications.html', context)


def admin_system_health(request):
    """System health monitoring dashboard"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    from django.db import connection
    import psutil
    import os
    
    # Database health
    db_stats = {
        'total_queries': len(connection.queries),
        'pharmacies_count': Pharmacy.objects.count(),
        'customers_count': Customer.objects.count(),
        'orders_count': Order.objects.count(),
        'prescriptions_count': Prescription.objects.count(),
    }
    
    # System health (basic stats)
    system_stats = {
        'cpu_percent': psutil.cpu_percent() if 'psutil' in globals() else 'N/A',
        'memory_percent': psutil.virtual_memory().percent if 'psutil' in globals() else 'N/A',
        'disk_usage': psutil.disk_usage('/').percent if 'psutil' in globals() else 'N/A',
    }
    
    # Recent incidents and alerts
    recent_incidents = IncidentReport.objects.filter(status__in=['open', 'in_progress']).order_by('-created_at')[:5]
    recent_alerts = SecurityAlert.objects.filter(status='active').order_by('-created_at')[:5]
    
    context = {
        'db_stats': db_stats,
        'system_stats': system_stats,
        'recent_incidents': recent_incidents,
        'recent_alerts': recent_alerts,
    }
    
    return render(request, 'admin/system_health.html', context)


def quick_report_incident(request):
    """Quick incident reporting for emergency issues"""
    from customer.forms_reporting import QuickIncidentForm
    
    if request.method == 'POST':
        form = QuickIncidentForm(request.POST)
        if form.is_valid():
            # Create incident report
            incident = IncidentReport.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                category=form.cleaned_data['category'],
                severity=form.cleaned_data['severity'],
                reporter_email=form.cleaned_data['contact_email'] or 'anonymous@system.local',
                status='open',
                created_by=request.user if request.user.is_authenticated else None
            )
            
            # Create notification for admins
            if request.user.is_authenticated:
                AdminNotification.objects.create(
                    user=request.user,
                    title=f'Quick Report: {incident.title}',
                    message=f'Incident #{incident.id} reported via quick form.',
                    notification_type='incident',
                    is_read=False
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Report submitted successfully',
                    'incident_id': incident.id
                })
            
            messages.success(request, 'Incident report submitted successfully.')
            return redirect('home')
    else:
        form = QuickIncidentForm()
    
    context = {'form': form}
    return render(request, 'admin/quick_report.html', context)