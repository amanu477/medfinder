from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pharmacy, Medicine, MoHPharmacyRecord

class PharmacyRegistrationForm(forms.ModelForm):
    """Form for pharmacy registration with mandatory document uploads"""
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    license_number = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    license_type = forms.ChoiceField(choices=Pharmacy.LICENSE_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    opening_time = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    closing_time = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    
    # Mandatory document uploads
    business_license = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control', 
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        help_text="Business license document is required (PDF, JPG, PNG)"
    )
    pharmacist_certificate = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control', 
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        help_text="Pharmacist certificate is required (PDF, JPG, PNG)"
    )
    verification_documents = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control', 
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        help_text="Additional verification documents (Optional)"
    )
    
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Pharmacy
        fields = [
            'name', 'license_number', 'license_type', 'address', 'phone', 'email', 
            'opening_time', 'closing_time', 'business_license', 'pharmacist_certificate', 
            'verification_documents', 'latitude', 'longitude'
        ]
    
    def clean_business_license(self):
        """Validate business license file"""
        file = self.cleaned_data.get('business_license')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError("Business license file size cannot exceed 10MB.")
            
            valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Business license must be PDF, JPG, JPEG, or PNG format.")
        return file
    
    def clean_pharmacist_certificate(self):
        """Validate pharmacist certificate file"""
        file = self.cleaned_data.get('pharmacist_certificate')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError("Pharmacist certificate file size cannot exceed 10MB.")
            
            valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Pharmacist certificate must be PDF, JPG, JPEG, or PNG format.")
        return file

    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone')
        if phone:
            import re
            # Remove spaces, dashes, parentheses
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not re.match(r'^[+]?[\d]{10,15}$', cleaned_phone):
                raise forms.ValidationError("Please enter a valid phone number (10-15 digits).")
        return phone

    def clean_license_number(self):
        """Validate license number"""
        license_number = self.cleaned_data.get('license_number')
        if license_number:
            if len(license_number.strip()) < 5:
                raise forms.ValidationError("License number must be at least 5 characters long.")
            
            # Check if license number already exists
            from .models import Pharmacy
            if Pharmacy.objects.filter(license_number=license_number).exists():
                raise forms.ValidationError("A pharmacy with this license number already exists.")
        return license_number

    def clean_email(self):
        """Validate email"""
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            from .models import Pharmacy
            if Pharmacy.objects.filter(email=email).exists():
                raise forms.ValidationError("A pharmacy with this email address already exists.")
        return email

    def clean_name(self):
        """Validate pharmacy name"""
        name = self.cleaned_data.get('name')
        if name:
            if len(name.strip()) < 3:
                raise forms.ValidationError("Pharmacy name must be at least 3 characters long.")
            
            # Check if name already exists
            from .models import Pharmacy
            if Pharmacy.objects.filter(name__iexact=name.strip()).exists():
                raise forms.ValidationError("A pharmacy with this name already exists.")
        return name.strip()

    def clean_address(self):
        """Validate address"""
        address = self.cleaned_data.get('address')
        if address and len(address.strip()) < 10:
            raise forms.ValidationError("Please provide a detailed address (at least 10 characters).")
        return address.strip() if address else address

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')
        
        if opening_time and closing_time:
            if closing_time <= opening_time:
                raise forms.ValidationError("Closing time must be after opening time.")
        
        return cleaned_data

class PharmacyUserForm(UserCreationForm):
    """Form for creating user account for pharmacy"""
    username = forms.CharField(
        max_length=30, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="3-30 characters, letters, numbers, and underscore only"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text="Valid email address for account verification"
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="At least 8 characters with uppercase, lowercase, and numbers"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Confirm your password"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        """Validate username"""
        username = self.cleaned_data.get('username')
        if username:
            import re
            if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
                raise forms.ValidationError("Username must be 3-30 characters, letters, numbers, and underscore only.")
            
            # Check if username already exists
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        """Validate email"""
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            from django.contrib.auth.models import User
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password1(self):
        """Validate password strength"""
        password1 = self.cleaned_data.get('password1')
        if password1:
            import re
            if len(password1) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
            
            if not re.search(r'[a-z]', password1):
                raise forms.ValidationError("Password must contain at least one lowercase letter.")
            
            if not re.search(r'[A-Z]', password1):
                raise forms.ValidationError("Password must contain at least one uppercase letter.")
            
            if not re.search(r'\d', password1):
                raise forms.ValidationError("Password must contain at least one number.")
                
        return password1

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