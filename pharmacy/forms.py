from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pharmacy, Medicine, MoHPharmacyRecord

class PharmacyRegistrationForm(forms.ModelForm):
    """Form for pharmacy registration"""
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    license_number = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    license_type = forms.ChoiceField(choices=Pharmacy.LICENSE_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    opening_time = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    closing_time = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Pharmacy
        fields = ['name', 'license_number', 'license_type', 'address', 'phone', 'email', 'opening_time', 'closing_time', 'latitude', 'longitude']

class PharmacyUserForm(UserCreationForm):
    """Form for creating user account for pharmacy"""
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class PharmacyProfileForm(forms.ModelForm):
    """Form for editing pharmacy profile"""
    
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Pharmacy
        fields = [
            'name', 'license_number', 'license_type', 'address', 'phone', 'email', 'opening_time', 
            'closing_time', 'is_active', 'business_license', 'pharmacist_certificate', 
            'verification_documents', 'latitude', 'longitude'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'business_license': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'pharmacist_certificate': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'verification_documents': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
        }
        
        help_texts = {
            'business_license': 'Upload your business license (PDF, JPG, PNG)',
            'pharmacist_certificate': 'Upload pharmacist certification (PDF, JPG, PNG)',
            'verification_documents': 'Upload any additional verification documents (Optional)',
        }

class MedicineForm(forms.ModelForm):
    """Form for medicine CRUD operations"""
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'price', 'stock_quantity', 'medicine_image', 'expiry_date', 'is_available', 'prescription_required']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'medicine_image': forms.FileInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prescription_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PharmacyVerificationForm(forms.ModelForm):
    """Form for pharmacy verification document upload"""
    business_license = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
        help_text="Upload your business license (PDF, JPG, PNG)"
    )
    pharmacist_certificate = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
        help_text="Upload pharmacist certification (PDF, JPG, PNG)"
    )
    verification_documents = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
        help_text="Upload any additional verification documents (Optional)"
    )
    
    class Meta:
        model = Pharmacy
        fields = ['business_license', 'pharmacist_certificate', 'verification_documents']

class MoHPharmacyForm(forms.ModelForm):
    """Form for Ministry of Health officials to register pharmacies"""
    
    class Meta:
        model = MoHPharmacyRecord
        fields = [
            'pharmacy_name', 'license_number', 'owner_name', 'pharmacist_name', 
            'pharmacist_license', 'region', 'city', 'woreda', 'kebele', 
            'address_detail', 'license_type', 'issue_date', 'expiry_date', 
            'status', 'phone_number', 'email', 'business_license_document',
            'pharmacist_certificate_document', 'pharmacy_permit_document',
            'inspection_report_document', 'moh_officer', 'last_inspection_date', 'notes'
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
            'business_license_document': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'pharmacist_certificate_document': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'pharmacy_permit_document': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'inspection_report_document': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
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