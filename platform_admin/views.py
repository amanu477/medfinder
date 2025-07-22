from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging

logger = logging.getLogger(__name__)

# Import models from other apps
from pharmacy.models import Pharmacy, Medicine
from customer.models import Customer, Order, OrderItem, Prescription, IncidentReport, AdminNotification
from moh.models import MoHPharmacyRegistry
from pharmacy.verification_service import MinistryOfHealthVerificationService
from .forms import PlatformAdminLoginForm

def admin_login(request):
    """Platform admin login view"""
    if request.method == 'POST':
        form = PlatformAdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, Platform Admin {user.username}!')
            return redirect('platform_admin:admin_dashboard')
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = PlatformAdminLoginForm()
    
    return render(request, 'admin/login.html', {'form': form})

@login_required
def admin_dashboard(request):
    """Admin dashboard with overview of all system components"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('platform_admin:admin_login')
    
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
    
    # Run automatic MoH database check
    moh_service = MinistryOfHealthVerificationService()
    moh_data = moh_service.verify_pharmacy(
        pharmacy_name=pharmacy.name,
        license_number=pharmacy.license_number,
        owner_name=pharmacy.user.get_full_name() if pharmacy.user else 'Unknown'
    )
    
    if moh_data['moh_record_found'] and moh_data['risk_assessment']['recommendation'] == 'APPROVE':
        pharmacy.verification_status = 'verified'
        pharmacy.save()
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
        'resolved_reports': IncidentReport.objects.filter(status='resolved').count(),
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

def admin_resolve_incident(request, incident_id):
    """Mark incident as resolved"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    incident = get_object_or_404(IncidentReport, id=incident_id)
    incident.status = 'resolved'
    incident.resolved_at = timezone.now()
    incident.resolved_by = request.user
    incident.save()
    
    messages.success(request, f'Incident "{incident.title}" has been marked as resolved.')
    return redirect('platform_admin:admin_incident_reports')

@require_http_methods(["POST"])
@csrf_exempt
@login_required
def admin_verify_moh(request):
    """API endpoint for admin to verify pharmacy license with MoH records"""
    if not request.user.is_superuser:
        return JsonResponse({
            'valid': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        data = json.loads(request.body)
        pharmacy_id = data.get('pharmacy_id')
        license_number = data.get('license_number', '').strip()
        pharmacy_name = data.get('pharmacy_name', '').strip()
        
        if not pharmacy_id or not license_number:
            return JsonResponse({
                'valid': False,
                'message': 'Pharmacy ID and license number are required.'
            })
        
        # Get the pharmacy instance
        try:
            pharmacy = Pharmacy.objects.get(id=pharmacy_id)
        except Pharmacy.DoesNotExist:
            return JsonResponse({
                'valid': False,
                'message': 'Pharmacy not found.'
            })
        
        # Check for license match in independent MoH registry
        try:
            moh_record = MoHPharmacyRegistry.objects.filter(
                license_number=pharmacy.license_number
            ).first()
            
            if moh_record:
                # License found in MoH registry - approve automatically
                pharmacy.verification_status = 'verified'
                pharmacy.verified_at = timezone.now()
                pharmacy.save()
                
                response_data = {
                    'valid': True,
                    'message': 'License found in MoH registry - Pharmacy approved automatically',
                    'status': 'verified',
                    'status_updated': True,
                    'data': {
                        'pharmacy_name': moh_record.pharmacy_name,
                        'owner_name': moh_record.owner_name,
                        'pharmacist_name': moh_record.pharmacist_name,
                        'license_type': moh_record.get_license_type_display(),
                        'region': moh_record.get_region_display(),
                        'city': moh_record.city,
                        'license_status': moh_record.get_license_status_display(),
                        'issue_date': moh_record.issue_date.strftime('%Y-%m-%d') if moh_record.issue_date else 'N/A',
                        'expiry_date': moh_record.expiry_date.strftime('%Y-%m-%d') if moh_record.expiry_date else 'N/A'
                    }
                }
            else:
                # License not found in MoH registry - reject automatically
                pharmacy.verification_status = 'rejected'
                pharmacy.save()
                
                response_data = {
                    'valid': False,
                    'message': 'License number not found in MoH registry - Pharmacy rejected automatically',
                    'status': 'rejected',
                    'status_updated': True
                }
            
        except Exception as e:
            logger.error(f"Error during MoH verification: {e}")
            response_data = {
                'valid': False,
                'message': 'Error accessing MoH registry. Please try again later.',
                'status': 'error',
                'status_updated': False
            }
        
        # Create admin notification about the verification - FIXED
        AdminNotification.objects.create(
            user=request.user,  # ✅ Changed from 'recipient' to 'user'
            title=f'MoH Verification: {pharmacy.name}',
            message=f'MoH verification {"successful" if response_data["valid"] else "failed"} for {pharmacy.name} (License: {license_number})',
            notification_type='verification',
            is_read=False
        )
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'valid': False,
            'message': 'Invalid request format.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in admin_verify_moh: {e}")
        return JsonResponse({
            'valid': False,
            'message': 'Unable to verify with MoH: HTTP 500: Internal Server Error'
        }, status=500)