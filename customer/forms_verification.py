from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Customer


class EmailVerificationForm(forms.Form):
    """Form for email verification with 6-digit code"""
    verification_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '123456',
            'style': 'font-size: 2rem; letter-spacing: 0.5rem;',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'title': 'Please enter exactly 6 digits'
        }),
        help_text="Enter the 6-digit verification code sent to your email"
    )
    
    def clean_verification_code(self):
        """Validate verification code format"""
        code = self.cleaned_data.get('verification_code')
        
        if not code:
            raise forms.ValidationError("Verification code is required.")
        
        if not code.isdigit():
            raise forms.ValidationError("Verification code must contain only numbers.")
        
        if len(code) != 6:
            raise forms.ValidationError("Verification code must be exactly 6 digits.")
        
        return code


class ResendVerificationForm(forms.Form):
    """Form for resending verification code"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'readonly': True
        }),
        help_text="We'll send a new verification code to this email"
    )
    
    def clean_email(self):
        """Validate email exists in system"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise forms.ValidationError("Email is required.")
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
            if hasattr(user, 'customer'):
                customer = user.customer
                if customer.is_email_verified:
                    raise forms.ValidationError("This email is already verified.")
            else:
                raise forms.ValidationError("No customer account found with this email.")
        except User.DoesNotExist:
            raise forms.ValidationError("No account found with this email address.")
        
        return email