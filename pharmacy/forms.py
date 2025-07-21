from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import time
import re
from decimal import Decimal, InvalidOperation
from .models import Pharmacy, Medicine, MoHPharmacyRecord
from .license_validation import LicenseValidationService

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
    is_24_hour = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Check if your pharmacy operates 24 hours a day"
    )
    
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
            'opening_time', 'closing_time', 'is_24_hour', 'business_license', 'pharmacist_certificate', 
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
            # Remove spaces, dashes, parentheses
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
            
            # Add + if not present
            if not cleaned_phone.startswith('+'):
                cleaned_phone = '+' + cleaned_phone
            
            # Ethiopian phone number validation
            if not re.match(r'^\+251[79]\d{8}$', cleaned_phone):
                raise forms.ValidationError(
                    "Phone number must be valid Ethiopian format: +251XXXXXXXXX (e.g., +251911123456)"
                )
        return phone

    def clean_license_number(self):
        """Validate license number format only - no MoH check during registration"""
        license_number = self.cleaned_data.get('license_number')
        if license_number:
            if len(license_number.strip()) < 5:
                raise forms.ValidationError("License number must be at least 5 characters long.")
            
            # Check for platform uniqueness only
            from .models import Pharmacy
            if Pharmacy.objects.filter(license_number=license_number.strip()).exists():
                raise forms.ValidationError("A pharmacy with this license number already exists on the platform.")
        
        return license_number.strip() if license_number else license_number

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
            name = name.strip()
            
            # Length validation
            if len(name) < 3:
                raise forms.ValidationError("Pharmacy name must be at least 3 characters long.")
            if len(name) > 100:
                raise forms.ValidationError("Pharmacy name cannot exceed 100 characters.")
            
            # Character validation: allow letters, numbers, spaces, dots, hyphens, apostrophes, forward slashes
            if not re.match(r'^[a-zA-Z0-9\s\.\-\'&\/]+$', name):
                raise forms.ValidationError(
                    "Pharmacy name can only contain letters, numbers, spaces, dots (.), hyphens (-), apostrophes ('), ampersand (&), and forward slash (/)."
                )
            
            # Check if name already exists
            from .models import Pharmacy
            if Pharmacy.objects.filter(name__iexact=name).exists():
                raise forms.ValidationError("A pharmacy with this name already exists.")
        return name

    def clean_address(self):
        """Validate address"""
        address = self.cleaned_data.get('address')
        if address:
            address = address.strip()
            
            # Length validation
            if len(address) < 10:
                raise forms.ValidationError("Please provide a detailed address (at least 10 characters).")
            if len(address) > 500:
                raise forms.ValidationError("Address cannot exceed 500 characters.")
            
            # Character validation: allow letters, numbers, spaces, common punctuation
            if not re.match(r'^[a-zA-Z0-9\s\.\,\-\'\/\#]+$', address):
                raise forms.ValidationError(
                    "Address can only contain letters, numbers, spaces, and common punctuation (. , - ' / #)."
                )
        return address

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')
        is_24_hour = cleaned_data.get('is_24_hour')
        
        if is_24_hour:
            # For 24-hour pharmacies, set default times if not provided
            if not opening_time:
                cleaned_data['opening_time'] = time(0, 0)  # 12:00 AM
            if not closing_time:
                cleaned_data['closing_time'] = time(23, 59)  # 11:59 PM
        else:
            # For non-24-hour pharmacies, validate times
            if opening_time and closing_time:
                if closing_time <= opening_time:
                    raise forms.ValidationError("Closing time must be after opening time, or check '24 Hour Open' if your pharmacy operates around the clock.")
        
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
            'closing_time', 'is_24_hour', 'is_active', 'business_license', 'pharmacist_certificate', 
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
            'is_24_hour': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
            'is_24_hour': 'Check if your pharmacy operates 24 hours a day',
            'is_active': 'Uncheck to temporarily close your pharmacy',
        }
    
    def clean(self):
        """Custom validation for 24-hour pharmacies"""
        cleaned_data = super().clean()
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')
        is_24_hour = cleaned_data.get('is_24_hour')
        
        if is_24_hour:
            # For 24-hour pharmacies, opening and closing times are not required
            # Set to None to clear any existing values
            cleaned_data['opening_time'] = None
            cleaned_data['closing_time'] = None
        else:
            # For non-24-hour pharmacies, both times are required
            if not opening_time:
                raise forms.ValidationError("Opening time is required for non-24-hour pharmacies.")
            if not closing_time:
                raise forms.ValidationError("Closing time is required for non-24-hour pharmacies.")
            
            # Validate that closing time is after opening time (unless overnight)
            if opening_time and closing_time:
                if closing_time <= opening_time:
                    raise forms.ValidationError("Closing time must be after opening time, or check '24/7 Pharmacy' if your pharmacy operates around the clock.")
        
        return cleaned_data

class MedicineForm(forms.ModelForm):
    """Form for medicine CRUD operations"""
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'price', 'stock_quantity', 'medicine_image', 'expiry_date', 'is_available', 'prescription_required']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Paracetamol 500mg'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of the medicine'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': '0.00'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'medicine_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prescription_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_name(self):
        """Validate medicine name"""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            
            # Length validation
            if len(name) < 2:
                raise forms.ValidationError("Medicine name must be at least 2 characters long.")
            if len(name) > 200:
                raise forms.ValidationError("Medicine name cannot exceed 200 characters.")
            
            # Character validation: allow letters, numbers, spaces, dots, hyphens, parentheses
            if not re.match(r'^[a-zA-Z0-9\s\.\-\(\)%/mg]+$', name):
                raise forms.ValidationError(
                    "Medicine name can only contain letters, numbers, spaces, dots (.), hyphens (-), parentheses (), percentage (%), slash (/), and 'mg'."
                )
        return name
    
    def clean_description(self):
        """Validate medicine description"""
        description = self.cleaned_data.get('description')
        if description:
            description = description.strip()
            
            # Length validation
            if len(description) < 5:
                raise forms.ValidationError("Description must be at least 5 characters long.")
            if len(description) > 1000:
                raise forms.ValidationError("Description cannot exceed 1000 characters.")
            
            # Character validation: allow letters, numbers, spaces, common punctuation
            if not re.match(r'^[a-zA-Z0-9\s\.\,\-\'\(\)%/]+$', description):
                raise forms.ValidationError(
                    "Description can only contain letters, numbers, spaces, and common punctuation."
                )
        return description
    
    def clean_price(self):
        """Validate medicine price"""
        price = self.cleaned_data.get('price')
        if price is not None:
            # Convert to Decimal for precise validation
            try:
                price_decimal = Decimal(str(price))
                
                # Must be positive
                if price_decimal <= 0:
                    raise forms.ValidationError("Price must be a positive number greater than 0.")
                
                # Maximum price limit
                if price_decimal > 10000:
                    raise forms.ValidationError("Price cannot exceed 10,000 ETB.")
                
                # Check decimal places (maximum 2)
                if price_decimal.as_tuple().exponent < -2:
                    raise forms.ValidationError("Price cannot have more than 2 decimal places.")
                
            except (InvalidOperation, ValueError):
                raise forms.ValidationError("Please enter a valid price.")
        return price
    
    def clean_stock_quantity(self):
        """Validate stock quantity"""
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if stock_quantity is not None:
            # Must be non-negative integer
            if stock_quantity < 0:
                raise forms.ValidationError("Stock quantity cannot be negative.")
            
            # Maximum stock limit
            if stock_quantity > 100000:
                raise forms.ValidationError("Stock quantity cannot exceed 100,000 units.")
        return stock_quantity
    
    def clean_medicine_image(self):
        """Validate medicine image"""
        image = self.cleaned_data.get('medicine_image')
        if image:
            # File size validation (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file size cannot exceed 5MB.")
            
            # File type validation
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Image must be in JPG, JPEG, PNG, GIF, or WebP format.")
        return image
    
    def clean_expiry_date(self):
        """Validate expiry date"""
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date:
            from datetime import date
            
            # Must be future date
            if expiry_date <= date.today():
                raise forms.ValidationError("Expiry date must be in the future.")
            
            # Cannot be more than 10 years in the future
            from datetime import timedelta
            max_date = date.today() + timedelta(days=3650)  # 10 years
            if expiry_date > max_date:
                raise forms.ValidationError("Expiry date cannot be more than 10 years in the future.")
        return expiry_date

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