from django import forms
from .models import MoHPharmacyRecord

class MoHPharmacyForm(forms.ModelForm):
    """Form for Ministry of Health officials to register pharmacies"""
    
    class Meta:
        model = MoHPharmacyRecord
        fields = [
            'pharmacy_name', 'license_number', 'owner_name', 'pharmacist_name', 
            'pharmacist_license', 'region', 'city', 'woreda', 'kebele', 
            'address_detail', 'license_type', 'issue_date', 'expiry_date', 
            'status', 'phone_number', 'email', 'moh_officer', 
            'last_inspection_date', 'notes'
        ]
        
        widgets = {
            'pharmacy_name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., PH001234'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control'}),
            'pharmacist_name': forms.TextInput(attrs={'class': 'form-control'}),
            'pharmacist_license': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., PC123456'}),
            'region': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'woreda': forms.TextInput(attrs={'class': 'form-control'}),
            'kebele': forms.TextInput(attrs={'class': 'form-control'}),
            'address_detail': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'license_type': forms.Select(attrs={'class': 'form-select'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+251911123456'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'moh_officer': forms.TextInput(attrs={'class': 'form-control'}),
            'last_inspection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Additional notes about the pharmacy'}),
        }

class MoHLoginForm(forms.Form):
    """Simple login form for MoH officials"""
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MoH Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )