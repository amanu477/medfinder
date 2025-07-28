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
    """Form for pharmacy registration with automatic location capture"""
    
    # Add hidden fields for coordinates
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    
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



    def clean(self):
        """Custom clean method for 24-hour pharmacy validation"""
        cleaned_data = super().clean()
        is_24_hour = cleaned_data.get('is_24_hour', False)
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')
        
        if is_24_hour:
            # For 24-hour pharmacies, clear the time fields
            cleaned_data['opening_time'] = None
            cleaned_data['closing_time'] = None
        else:
            # For non-24-hour pharmacies, require both times
            if not opening_time:
                self.add_error('opening_time', 'Opening time is required for non-24-hour pharmacies.')
            if not closing_time:
                self.add_error('closing_time', 'Closing time is required for non-24-hour pharmacies.')
        
        return cleaned_data

class PharmacyProfileForm(forms.ModelForm):
    """Form for editing pharmacy profile"""
    
    class Meta:
        model = Pharmacy
        fields = ['name', 'license_number', 'license_type', 'address', 'phone', 'email', 
                 'opening_time', 'closing_time', 'is_24_hour', 'verification_documents', 
                 'business_license', 'pharmacist_certificate']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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

    def clean(self):
        """Custom clean method for 24-hour pharmacy validation"""
        cleaned_data = super().clean()
        is_24_hour = cleaned_data.get('is_24_hour', False)
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')
        
        if is_24_hour:
            # For 24-hour pharmacies, clear the time fields
            cleaned_data['opening_time'] = None
            cleaned_data['closing_time'] = None
        else:
            # For non-24-hour pharmacies, require both times
            if not opening_time:
                self.add_error('opening_time', 'Opening time is required for non-24-hour pharmacies.')
            if not closing_time:
                self.add_error('closing_time', 'Closing time is required for non-24-hour pharmacies.')
        
        return cleaned_data

class MedicineForm(forms.ModelForm):
    """Form for adding/editing medicines"""
    
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'price', 'stock_quantity', 'expiry_date', 'is_available', 'prescription_required', 'medicine_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prescription_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'medicine_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        """Validate medicine name"""
        name = self.cleaned_data.get('name')
        if name:
            # Allow letters, numbers, spaces, dots, hyphens, apostrophes, parentheses, and forward slashes
            if not re.match(r"^[a-zA-Z0-9\s.\-'()/]+$", name):
                raise ValidationError("Medicine name can only contain letters, numbers, spaces, dots, hyphens, apostrophes, parentheses, and forward slashes.")
            if len(name.strip()) < 2:
                raise ValidationError("Medicine name must be at least 2 characters long.")
        return name

    def clean_price(self):
        """Validate medicine price"""
        price = self.cleaned_data.get('price')
        if price is not None:
            if price <= 0:
                raise ValidationError("Price must be greater than 0.")
            # Remove price limit - pharmacy can set any price they want
            # Check for maximum 2 decimal places
            if len(str(price).split('.')[-1]) > 2:
                raise ValidationError("Price can have maximum 2 decimal places.")
        return price
    
    def clean_stock_quantity(self):
        """Validate stock quantity"""
        quantity = self.cleaned_data.get('stock_quantity')
        if quantity is not None and quantity < 0:
            raise ValidationError("Stock quantity cannot be negative.")
        return quantity
    
    def clean_expiry_date(self):
        """Validate expiry date to prevent adding expired medicines"""
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date:
            from django.utils import timezone
            today = timezone.now().date()
            
            # Check if medicine is already expired
            if expiry_date < today:
                raise ValidationError("Cannot add expired medicine. Please check the expiry date.")
            
            # Warn if medicine expires very soon (within 7 days)
            from datetime import timedelta
            warning_date = today + timedelta(days=7)
            if expiry_date <= warning_date:
                raise ValidationError("This medicine expires very soon (within 7 days). Please verify the expiry date.")
        
        return expiry_date

class PrescriptionReviewForm(forms.ModelForm):
    """Form for pharmacy to review prescription images and validate medicines"""
    
    # Additional fields for enhanced verification
    prescription_image_reviewed = forms.BooleanField(
        required=True,
        label="I have carefully examined the prescription image",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    medicine_clearly_visible = forms.ChoiceField(
        required=True,
        label="Is the requested medicine clearly visible in the prescription?",
        choices=[
            ('', 'Please select...'),
            ('yes', 'Yes - Medicine name is clearly visible'),
            ('no', 'No - Medicine name is not visible/unclear'),
            ('partial', 'Partially visible - Some uncertainty')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    verification_confidence = forms.ChoiceField(
        required=True,
        label="How confident are you in your verification?",
        choices=[
            ('', 'Please select...'),
            ('high', 'High confidence - 100% certain'),
            ('medium', 'Medium confidence - 75-99% certain'),
            ('low', 'Low confidence - Below 75% certain')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = CartItem
        fields = ['pharmacy_review_status', 'pharmacy_review_notes']
        widgets = {
            'pharmacy_review_status': forms.Select(attrs={'class': 'form-select'}),
            'pharmacy_review_notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Provide detailed notes about your prescription verification including specific findings...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limit status choices to pharmacy review options
        self.fields['pharmacy_review_status'].choices = [
            ('', 'Select your decision...'),
            ('approved', 'APPROVED - Medicine matches prescription'),
            ('rejected', 'REJECTED - Medicine does not match prescription')
        ]
        
        # Make critical fields required for proper verification
        self.fields['pharmacy_review_notes'].required = False  # Optional - decision is sufficient
        self.fields['pharmacy_review_status'].required = True

    def clean(self):
        """Enhanced validation for proper prescription verification"""
        cleaned_data = super().clean()
        status = cleaned_data.get('pharmacy_review_status')
        notes = cleaned_data.get('pharmacy_review_notes')
        prescription_reviewed = cleaned_data.get('prescription_image_reviewed')
        medicine_visible = cleaned_data.get('medicine_clearly_visible')
        confidence = cleaned_data.get('verification_confidence')
        
        # Ensure prescription image has been reviewed
        if not prescription_reviewed:
            self.add_error('prescription_image_reviewed', 
                          'You must confirm that you have examined the prescription image.')
        
        # Validate medicine visibility assessment
        if not medicine_visible:
            self.add_error('medicine_clearly_visible', 
                          'You must assess whether the medicine is visible in the prescription.')
        
        # Validate verification confidence
        if not confidence:
            self.add_error('verification_confidence', 
                          'You must indicate your confidence level in the verification.')
        
        # Validate decision and notes
        if not status:
            self.add_error('pharmacy_review_status', 
                          'You must make a decision to approve or reject.')
        
        # Notes are now optional since final decision is sufficient
        # Only validate notes if they are provided
        if notes and len(notes.strip()) < 10:
            self.add_error('pharmacy_review_notes', 
                          'If providing notes, please write at least 10 characters.')
        
        # Logic validation: ensure consistency between assessments and decision
        if status == 'approved':
            if medicine_visible == 'no':
                self.add_error('pharmacy_review_status', 
                              'Cannot approve if medicine is not visible in prescription.')
            if confidence == 'low':
                self.add_error('pharmacy_review_status', 
                              'Cannot approve with low confidence. Consider rejection or request clearer prescription.')
        
        if status == 'rejected':
            if medicine_visible == 'yes' and confidence == 'high':
                self.add_error('pharmacy_review_status', 
                              'Inconsistent: Cannot reject if medicine is clearly visible with high confidence.')
        
        # Additional safety check for approval - but notes are optional
        if status == 'approved' and (medicine_visible != 'yes' or confidence != 'high'):
            # Warning but not blocking - final decision is sufficient
            pass
        
        return cleaned_data