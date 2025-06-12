from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import MoHOfficer, MoHPharmacyRecord
from pharmacy.models import Pharmacy


class MoHLoginForm(AuthenticationForm):
    """Custom login form for Ministry of Health officers"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your MoH username',
            'id': 'username',
            'required': True
        }),
        help_text="Your official MoH username"
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'id': 'password',
            'required': True
        }),
        help_text="Your MoH account password"
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Invalid login credentials. Please check your username and password."
                )
            else:
                # Check if user is an active MoH officer
                try:
                    moh_officer = MoHOfficer.objects.get(
                        user=self.user_cache,
                        is_active=True
                    )
                except MoHOfficer.DoesNotExist:
                    raise forms.ValidationError(
                        "Access denied. Only authorized Ministry of Health officers can access this system."
                    )
                
                if not self.user_cache.is_active:
                    raise forms.ValidationError(
                        "Your account has been deactivated. Please contact the system administrator."
                    )
        
        return self.cleaned_data


class MoHOfficerProfileForm(forms.ModelForm):
    """Form for MoH officer profile management"""
    
    class Meta:
        model = MoHOfficer
        fields = ['officer_id', 'department', 'position', 'phone', 'email']
        widgets = {
            'officer_id': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your position/title'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+251-XXX-XXX-XXX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@moh.gov.et'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not email.endswith('@moh.gov.et'):
            raise forms.ValidationError(
                "Please use your official MoH email address (@moh.gov.et)"
            )
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces and dashes
            phone = phone.replace(' ', '').replace('-', '')
            if not phone.startswith('+251') and not phone.startswith('09'):
                raise forms.ValidationError(
                    "Please enter a valid Ethiopian phone number"
                )
        return phone