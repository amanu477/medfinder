from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import MoHPharmacyRecord, VerificationRequest, MoHOfficer, ComplianceAlert
from .forms import MoHLoginForm, MoHPharmacyRegistrationForm
from pharmacy.models import Pharmacy, MoHPharmacyRecord as PharmacyMoHRecord
from customer.models import Customer


def moh_login(request):
    """MoH officer login with improved form handling"""
    if request.method == 'POST':
        form = MoHLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome, {user.get_full_name()}! You have successfully logged into the MoH system.')
            return redirect('moh_dashboard')
        else:
            # Form errors will be displayed in the template
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = MoHLoginForm()
    
    return render(request, 'moh/login.html', {'form': form})


@login_required
def moh_dashboard(request):
    """MoH dashboard with statistics"""
    # Check MoH officer status
    try:
        moh_officer = MoHOfficer.objects.get(user=request.user, is_active=True)
    except MoHOfficer.DoesNotExist:
        return redirect('moh_login')
    
    # Dashboard statistics
    total_pharmacies = PharmacyMoHRecord.objects.count()
    pending_verifications = VerificationRequest.objects.filter(status='pending').count()
    active_pharmacies = PharmacyMoHRecord.objects.filter(status='active').count()
    critical_alerts = ComplianceAlert.objects.filter(severity='critical', is_resolved=False).count()
    
    # Recent verification requests
    recent_requests = VerificationRequest.objects.filter(
        status__in=['pending', 'under_review']
    ).order_by('-submitted_date')[:5]
    
    # Recent compliance alerts
    recent_alerts = ComplianceAlert.objects.filter(
        is_resolved=False
    ).order_by('-created_at')[:5]
    
    # All pharmacy registrations (show all instead of just recent 5)
    recent_pharmacies = PharmacyMoHRecord.objects.order_by('-registration_date')
    
    # Additional statistics for dashboard
    expired_licenses = PharmacyMoHRecord.objects.filter(status='expired').count()
    pending_renewals = PharmacyMoHRecord.objects.filter(status='suspended').count()
    
    context = {
        'moh_officer': moh_officer,
        'total_pharmacies': total_pharmacies,
        'pending_verifications': pending_verifications,
        'active_pharmacies': active_pharmacies,
        'critical_alerts': critical_alerts,
        'recent_requests': recent_requests,
        'recent_alerts': recent_alerts,
        'recent_pharmacies': recent_pharmacies,
        'expired_licenses': expired_licenses,
        'pending_renewals': pending_renewals,
    }
    
    return render(request, 'moh/dashboard.html', context)


@login_required
def moh_pharmacy_list(request):
    """List all pharmacies with MoH records"""
    try:
        moh_officer = MoHOfficer.objects.get(user=request.user, is_active=True)
    except MoHOfficer.DoesNotExist:
        return redirect('moh_login')
    
    # Filter and search
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Get pharmacy records from the pharmacy app's MoHPharmacyRecord model
    pharmacies = PharmacyMoHRecord.objects.all().order_by('-registration_date')
    
    if search_query:
        pharmacies = pharmacies.filter(
            Q(pharmacy_name__icontains=search_query) |
            Q(license_number__icontains=search_query) |
            Q(owner_name__icontains=search_query) |
            Q(address_detail__icontains=search_query)
        )
    
    if status_filter:
        pharmacies = pharmacies.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(pharmacies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'moh_officer': moh_officer,
        'page_obj': page_obj,
        'pharmacies': page_obj,  # For template compatibility
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': PharmacyMoHRecord.STATUS_CHOICES,
    }
    
    return render(request, 'moh/pharmacy_list.html', context)


@login_required
def moh_verification_requests(request):
    """View verification requests"""
    try:
        moh_officer = MoHOfficer.objects.get(user=request.user, is_active=True)
    except MoHOfficer.DoesNotExist:
        return redirect('moh_login')
    
    # Filter requests
    status_filter = request.GET.get('status', 'pending')
    requests = VerificationRequest.objects.filter(status=status_filter).order_by('-submitted_date')
    
    # Pagination
    paginator = Paginator(requests, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'moh_officer': moh_officer,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_choices': VerificationRequest._meta.get_field('status').choices,
    }
    
    return render(request, 'moh/verification_requests.html', context)


@login_required
def moh_respond_verification(request, request_id):
    """Respond to verification request"""
    try:
        moh_officer = MoHOfficer.objects.get(user=request.user, is_active=True)
    except MoHOfficer.DoesNotExist:
        return redirect('moh_login')
    
    verification_request = get_object_or_404(VerificationRequest, id=request_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            verification_request.status = 'approved'
            verification_request.reviewed_by = request.user
            verification_request.reviewed_date = timezone.now()
            verification_request.notes = notes
            verification_request.save()
            
            # Update or create MoH record
            moh_record, created = MoHPharmacyRecord.objects.get_or_create(
                pharmacy=verification_request.pharmacy,
                defaults={
                    'license_status': 'active',
                    'verified_by': request.user,
                    'verification_date': timezone.now(),
                }
            )
            if not created:
                moh_record.license_status = 'active'
                moh_record.verified_by = request.user
                moh_record.verification_date = timezone.now()
                moh_record.save()
            
            messages.success(request, 'Verification request approved successfully.')
            
        elif action == 'reject':
            verification_request.status = 'rejected'
            verification_request.reviewed_by = request.user
            verification_request.reviewed_date = timezone.now()
            verification_request.rejection_reason = notes
            verification_request.save()
            
            messages.success(request, 'Verification request rejected.')
            
        elif action == 'require_inspection':
            verification_request.status = 'requires_inspection'
            verification_request.reviewed_by = request.user
            verification_request.reviewed_date = timezone.now()
            verification_request.notes = notes
            verification_request.save()
            
            messages.success(request, 'Inspection required for this pharmacy.')
        
        return redirect('moh_verification_requests')
    
    context = {
        'moh_officer': moh_officer,
        'verification_request': verification_request,
    }
    
    return render(request, 'moh/respond_verification.html', context)


@login_required
def moh_add_pharmacy(request):
    """Add new pharmacy to MoH records with comprehensive form and document uploads"""
    try:
        moh_officer = MoHOfficer.objects.get(user=request.user, is_active=True)
    except MoHOfficer.DoesNotExist:
        return redirect('moh_login')
    
    if request.method == 'POST':
        form = MoHPharmacyRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create a temporary user account for MoH-registered pharmacy
                # Use license number as username to ensure uniqueness
                temp_username = f"moh_pharmacy_{form.cleaned_data['license_number']}"
                from django.contrib.auth.models import User
                import secrets
                import string
                
                # Generate random password
                alphabet = string.ascii_letters + string.digits
                temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
                
                temp_user = User.objects.create_user(
                    username=temp_username,
                    email=form.cleaned_data.get('email', ''),
                    password=temp_password,
                    first_name=form.cleaned_data['pharmacy_name'][:30],  # Truncate if needed
                    is_active=False  # Inactive until pharmacy claims account
                )
                
                # Create pharmacy record with user
                pharmacy = Pharmacy.objects.create(
                    user=temp_user,
                    name=form.cleaned_data['pharmacy_name'],
                    license_number=form.cleaned_data['license_number'],
                    license_type=form.cleaned_data.get('license_type', 'retail'),
                    phone=form.cleaned_data['phone_number'],
                    email=form.cleaned_data.get('email', ''),
                    address=form.cleaned_data['address_detail'],
                    opening_time=form.cleaned_data['opening_time'],
                    closing_time=form.cleaned_data['closing_time'],
                    verification_status='verified',
                    moh_verification_status='verified',
                    is_active=True
                )
                
                # Create comprehensive MoH record with document uploads
                moh_record = MoHPharmacyRecord.objects.create(
                    pharmacy=pharmacy,
                    license_status='active',
                    verified_by=request.user,
                    verification_date=timezone.now(),
                    inspection_date=timezone.now().date(),
                    compliance_score=100,  # Newly registered pharmacies start with full score
                    business_license_verified=True,
                    pharmacist_certificate_verified=True,
                    pharmacy_permit_verified=True,
                    # Store uploaded documents
                    business_license_document=form.cleaned_data['business_license'],
                    pharmacist_certificate_document=form.cleaned_data['pharmacist_certificate'],
                    pharmacy_permit_document=form.cleaned_data['pharmacy_permit'],
                    inspection_report=form.cleaned_data.get('inspection_report'),
                )
                
                messages.success(
                    request, 
                    f'Pharmacy "{form.cleaned_data["pharmacy_name"]}" has been successfully registered '
                    f'with license number {form.cleaned_data["license_number"]}. '
                    f'All required documents have been uploaded and verified.'
                )
                return redirect('moh_pharmacy_list')
                
            except Exception as e:
                messages.error(request, f'Error creating pharmacy record: {str(e)}')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = MoHPharmacyRegistrationForm()
    
    context = {
        'moh_officer': moh_officer,
        'form': form,
    }
    
    return render(request, 'moh/add_pharmacy.html', context)


@login_required
def moh_edit_pharmacy(request, pharmacy_id):
    """Edit pharmacy MoH record"""
    try:
        moh_officer = MoHOfficer.objects.get(user=request.user, is_active=True)
    except MoHOfficer.DoesNotExist:
        return redirect('moh_login')
    
    pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
    moh_record, created = MoHPharmacyRecord.objects.get_or_create(
        pharmacy=pharmacy,
        defaults={'license_status': 'pending'}
    )
    
    if request.method == 'POST':
        # Update MoH record
        moh_record.license_status = request.POST.get('license_status')
        moh_record.compliance_score = int(request.POST.get('compliance_score', 0))
        moh_record.inspection_notes = request.POST.get('inspection_notes', '')
        moh_record.business_license_verified = bool(request.POST.get('business_license_verified'))
        moh_record.pharmacist_certificate_verified = bool(request.POST.get('pharmacist_certificate_verified'))
        moh_record.pharmacy_permit_verified = bool(request.POST.get('pharmacy_permit_verified'))
        moh_record.updated_at = timezone.now()
        moh_record.save()
        
        messages.success(request, 'MoH record updated successfully.')
        return redirect('moh_pharmacy_list')
    
    context = {
        'moh_officer': moh_officer,
        'pharmacy': pharmacy,
        'moh_record': moh_record,
        'status_choices': MoHPharmacyRecord._meta.get_field('license_status').choices,
    }
    
    return render(request, 'moh/edit_pharmacy.html', context)


@login_required
def moh_delete_pharmacy(request, pharmacy_id):
    """Suspend/deactivate pharmacy"""
    try:
        moh_officer = MoHOfficer.objects.get(user=request.user, is_active=True)
    except MoHOfficer.DoesNotExist:
        return redirect('moh_login')
    
    pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
    
    if request.method == 'POST':
        # Instead of deleting, suspend the license
        moh_record, created = MoHPharmacyRecord.objects.get_or_create(
            pharmacy=pharmacy,
            defaults={'license_status': 'suspended'}
        )
        if not created:
            moh_record.license_status = 'suspended'
            moh_record.save()
        
        pharmacy.is_active = False
        pharmacy.save()
        
        messages.success(request, f'Pharmacy "{pharmacy.name}" license suspended.')
        return redirect('moh_pharmacy_list')
    
    context = {
        'moh_officer': moh_officer,
        'pharmacy': pharmacy,
    }
    
    return render(request, 'moh/confirm_suspend.html', context)


@login_required
def moh_logout(request):
    """MoH officer logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('moh_login')