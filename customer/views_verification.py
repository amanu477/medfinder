from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db import transaction
import logging
import random
import string

from .models import Customer, EmailVerification
from .forms_verification import EmailVerificationForm, ResendVerificationForm
from .email_service import email_verification_service

logger = logging.getLogger(__name__)


@login_required
def email_verification_view(request):
    """Email verification confirmation page"""
    try:
        customer = request.user.customer
        
        # Check if already verified
        if customer.is_email_verified:
            messages.info(request, 'Your email is already verified!')
            return redirect('home')
        
        # Check if verification code exists and is valid
        if not customer.verification_code or not customer.verification_code_expires_at:
            messages.warning(request, 'No verification code found. Please request a new one.')
            return redirect('resend_verification')
        
        # Check if verification code has expired
        if timezone.now() > customer.verification_code_expires_at:
            messages.warning(request, 'Your verification code has expired. Please request a new one.')
            return redirect('resend_verification')
        
        if request.method == 'POST':
            form = EmailVerificationForm(request.POST)
            if form.is_valid():
                entered_code = form.cleaned_data['verification_code']
                
                # Check if code matches
                if customer.verification_code == entered_code:
                    # Mark as verified
                    customer.is_email_verified = True
                    customer.verification_code = None
                    customer.verification_code_expires_at = None
                    customer.save()
                    
                    messages.success(request, 'Email verified successfully! Your account is now fully activated.')
                    return redirect('dashboard')
                else:
                    form.add_error('verification_code', 'Invalid verification code. Please try again.')
            
        else:
            form = EmailVerificationForm()
        
        # Calculate time remaining
        time_remaining = customer.verification_code_expires_at - timezone.now()
        minutes_remaining = int(time_remaining.total_seconds() / 60)
        
        return render(request, 'customer/email_verification.html', {
            'form': form,
            'customer': customer,
            'minutes_remaining': minutes_remaining,
            'verification_email': request.user.email
        })
        
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')


@login_required
def resend_verification_view(request):
    """Resend verification code"""
    try:
        customer = request.user.customer
        
        # Check if already verified
        if customer.is_email_verified:
            messages.info(request, 'Your email is already verified!')
            return redirect('home')
        
        if request.method == 'POST':
            form = ResendVerificationForm(request.POST)
            form.fields['email'].initial = request.user.email
            
            if form.is_valid():
                # Generate new verification code
                verification_code = ''.join(random.choices(string.digits, k=6))
                
                # Update customer record
                customer.verification_code = verification_code
                customer.verification_code_expires_at = timezone.now() + timezone.timedelta(minutes=15)
                customer.save()
                
                # Send verification email
                try:
                    email_verification_service.send_verification_email(
                        request.user.email,
                        verification_code,
                        customer.name or request.user.username
                    )
                    messages.success(request, 'A new verification code has been sent to your email.')
                    return redirect('email_verification')
                except Exception as e:
                    logger.error(f"Error sending verification email: {str(e)}")
                    messages.error(request, 'Error sending verification email. Please try again.')
        else:
            form = ResendVerificationForm()
            form.fields['email'].initial = request.user.email
        
        return render(request, 'customer/resend_verification.html', {
            'form': form,
            'customer': customer
        })
        
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')


@csrf_exempt
def check_verification_status(request):
    """AJAX endpoint to check verification status"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        customer = request.user.customer
        return JsonResponse({
            'is_verified': customer.is_email_verified,
            'has_code': bool(customer.verification_code),
            'code_expired': (
                customer.verification_code_expires_at and
                timezone.now() > customer.verification_code_expires_at
            ) if customer.verification_code_expires_at else True
        })
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer profile not found'}, status=404)


def verification_success_view(request):
    """Email verification success page"""
    return render(request, 'customer/verification_success.html')


def verification_required_view(request):
    """Page shown when email verification is required"""
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            if customer.is_email_verified:
                return redirect('home')
        except Customer.DoesNotExist:
            pass
    
    return render(request, 'customer/verification_required.html')