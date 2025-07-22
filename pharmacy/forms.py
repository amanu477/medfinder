from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Pharmacy, Medicine
from customer.models import CartItem
import re

class PharmacyUserForm(UserCreationForm):
    """Form for creating pharmacy user account"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email

class PharmacyVerificationForm(forms.ModelForm):
    """Form for pharmacy verification updates"""
    
    class Meta:
        model = Pharmacy
        fields = ['verification_status']
        widgets = {
            'verification_status': forms.Select(attrs={'class': 'form-select'}),
        }

class PharmacyRegistrationForm(forms.ModelForm):
    """Form for pharmacy registration with required location coordinates"""
    
    class Meta:
        model = Pharmacy
        fields = ['name', 'license_number', 'license_type', 'address', 'latitude', 'longitude',
                 'phone', 'email', 'opening_time', 'closing_time', 'is_24_hour', 
                 'verification_documents', 'business_license', 'pharmacist_certificate']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': 'any', 
                'placeholder': 'e.g., 9.0260',
                'required': True,
                'id': 'pharmacy-latitude'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': 'any', 
                'placeholder': 'e.g., 38.7578',
                'required': True,
                'id': 'pharmacy-longitude'
            }),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+251912345678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_24_hour': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'verification_documents': forms.FileInput(attrs={'class': 'form-control'}),
            'business_license': forms.FileInput(attrs={'class': 'form-control'}),
            'pharmacist_certificate': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        """Validate pharmacy name"""
        name = self.cleaned_data.get('name')
        if name:
            # Allow letters, numbers, spaces, dots, hyphens, apostrophes, ampersands, and forward slashes
            if not re.match(r"^[a-zA-Z0-9\s.\-'&/]+$", name):
                raise ValidationError("Name can only contain letters, numbers, spaces, dots, hyphens, apostrophes, ampersands, and forward slashes.")
            if len(name.strip()) < 2:
                raise ValidationError("Name must be at least 2 characters long.")
        return name

    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any spaces or special characters
            cleaned_phone = re.sub(r'[^\d+]', '', phone)
            
            # Check if it starts with +251 or convert local number
            if cleaned_phone.startswith('0'):
                cleaned_phone = '+251' + cleaned_phone[1:]
            elif cleaned_phone.startswith('9') and len(cleaned_phone) == 9:
                cleaned_phone = '+251' + cleaned_phone
            elif not cleaned_phone.startswith('+251'):
                raise ValidationError("Phone number must be in Ethiopian format (+251XXXXXXXXX)")
            
            # Validate length and format
            if not re.match(r'^\+251[1-9]\d{8}$', cleaned_phone):
                raise ValidationError("Invalid Ethiopian phone number format. Use +251XXXXXXXXX")
            
            return cleaned_phone
        return phone

    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if email:
            from django.contrib.auth.models import User
            if User.objects.filter(email=email).exists():
                raise ValidationError("This email address is already registered.")
        return email

    def clean_license_number(self):
        """Validate license number"""
        license_number = self.cleaned_data.get('license_number')
        if license_number:
            # Check if license number already exists
            if Pharmacy.objects.filter(license_number=license_number).exists():
                raise ValidationError("This license number is already registered.")
            
            # Basic format validation
            if len(license_number.strip()) < 5:
                raise ValidationError("License number must be at least 5 characters long.")
        return license_number

    def clean_latitude(self):
        """Validate latitude coordinate"""
        latitude = self.cleaned_data.get('latitude')
        if latitude is None:
            raise ValidationError("Latitude coordinate is required for distance calculations and map display.")
        if not (-90 <= latitude <= 90):
            raise ValidationError("Latitude must be between -90 and 90 degrees.")
        # Check if it's a valid Ethiopian coordinate (approximate bounds)
        if not (3 <= latitude <= 15):
            raise ValidationError("Please enter a valid Ethiopian latitude coordinate (between 3 and 15 degrees).")
        return latitude

    def clean_longitude(self):
        """Validate longitude coordinate"""
        longitude = self.cleaned_data.get('longitude')
        if longitude is None:
            raise ValidationError("Longitude coordinate is required for distance calculations and map display.")
        if not (-180 <= longitude <= 180):
            raise ValidationError("Longitude must be between -180 and 180 degrees.")
        # Check if it's a valid Ethiopian coordinate (approximate bounds)
        if not (33 <= longitude <= 48):
            raise ValidationError("Please enter a valid Ethiopian longitude coordinate (between 33 and 48 degrees).")
        return longitude


class MedicineForm(forms.ModelForm):
    """Form for adding/editing medicines"""
    
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'price', 'stock_quantity', 'expiry_date', 'is_available', 'prescription_required']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prescription_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_expiry_date(self):
        """Validate expiry date"""
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date:
            from django.utils import timezone
            if expiry_date <= timezone.now().date():
                raise ValidationError("Expiry date must be in the future.")
        return expiry_date

    def clean_price(self):
        """Validate price"""
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise ValidationError("Price must be greater than zero.")
        return price

    def clean_stock_quantity(self):
        """Validate stock quantity"""
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if stock_quantity is not None and stock_quantity < 0:
            raise ValidationError("Stock quantity cannot be negative.")
        return stock_quantity


class PrescriptionResponseForm(forms.Form):
    """Form for responding to prescription orders"""
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('requires_clarification', 'Requires Clarification'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    pharmacist_notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text="Optional notes for the customer"
    )
    
    def clean_pharmacist_notes(self):
        """Validate pharmacist notes"""
        notes = self.cleaned_data.get('pharmacist_notes')
        status = self.cleaned_data.get('status')
        
        if status in ['rejected', 'requires_clarification'] and not notes:
            raise ValidationError("Please provide notes when rejecting or requesting clarification.")
        
        return notes


class CartUpdateForm(forms.ModelForm):
    """Form for updating cart items (pharmacy side)"""
    
    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def clean_quantity(self):
        """Validate quantity against stock"""
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise ValidationError("Quantity must be at least 1.")
        
        # Check stock availability
        if hasattr(self.instance, 'medicine') and self.instance.medicine:
            if quantity > self.instance.medicine.stock_quantity:
                raise ValidationError(f"Only {self.instance.medicine.stock_quantity} units available in stock.")
        
        return quantity


class PharmacyProfileForm(forms.ModelForm):
    """Form for updating pharmacy profile"""
    
    class Meta:
        model = Pharmacy
        fields = ['name', 'address', 'latitude', 'longitude', 'phone', 'email', 
                 'opening_time', 'closing_time', 'is_24_hour']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_24_hour': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PrescriptionReviewForm(forms.Form):
    """Form for reviewing prescription requests"""
    ACTION_CHOICES = [
        ('approve', 'Approve Prescription'),
        ('reject', 'Reject Prescription'),
        ('request_info', 'Request More Information'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text="Optional notes for the customer"
    )