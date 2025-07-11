from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re
from decimal import Decimal, InvalidOperation
from .models import Prescription, Customer, Order, IncidentReport, AdminNotification
from pharmacy.models import Pharmacy

class CustomerRegistrationForm(UserCreationForm):
    """Form for customer registration"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text="Valid email address for account verification"
    )
    first_name = forms.CharField(
        max_length=30, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Your first name (2-30 characters)"
    )
    last_name = forms.CharField(
        max_length=30, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Your last name (2-30 characters)"
    )
    phone = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Valid phone number (10-15 digits)"
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Your complete address (at least 10 characters)"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].help_text = "3-30 characters, letters, numbers, and underscore only"
        self.fields['password1'].help_text = "At least 8 characters with uppercase, lowercase, and numbers"
        self.fields['password2'].help_text = "Confirm your password"

    def clean_username(self):
        """Validate username"""
        username = self.cleaned_data.get('username')
        if username:
            import re
            if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
                raise forms.ValidationError("Username must be 3-30 characters, letters, numbers, and underscore only.")
            
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        """Validate email"""
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_first_name(self):
        """Validate first name"""
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            first_name = first_name.strip()
            
            # Length validation
            if len(first_name) < 2:
                raise forms.ValidationError("First name must be at least 2 characters long.")
            if len(first_name) > 30:
                raise forms.ValidationError("First name cannot exceed 30 characters.")
            
            # Character validation: allow letters, spaces, dots, hyphens, apostrophes
            if not re.match(r'^[a-zA-Z\s\.\-\']+$', first_name):
                raise forms.ValidationError(
                    "First name can only contain letters, spaces, dots (.), hyphens (-), and apostrophes (')."
                )
        return first_name

    def clean_last_name(self):
        """Validate last name"""
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            last_name = last_name.strip()
            
            # Length validation
            if len(last_name) < 2:
                raise forms.ValidationError("Last name must be at least 2 characters long.")
            if len(last_name) > 30:
                raise forms.ValidationError("Last name cannot exceed 30 characters.")
            
            # Character validation: allow letters, spaces, dots, hyphens, apostrophes
            if not re.match(r'^[a-zA-Z\s\.\-\']+$', last_name):
                raise forms.ValidationError(
                    "Last name can only contain letters, spaces, dots (.), hyphens (-), and apostrophes (')."
                )
        return last_name

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


class CustomerProfileForm(forms.ModelForm):
    """Form for editing customer profile"""
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+251911123456'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Complete address'}),
        }
    
    def clean_name(self):
        """Validate customer name"""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            
            # Length validation
            if len(name) < 2:
                raise forms.ValidationError("Name must be at least 2 characters long.")
            if len(name) > 100:
                raise forms.ValidationError("Name cannot exceed 100 characters.")
            
            # Character validation: allow letters, spaces, dots, hyphens, apostrophes
            if not re.match(r'^[a-zA-Z\s\.\-\']+$', name):
                raise forms.ValidationError(
                    "Name can only contain letters, spaces, dots (.), hyphens (-), and apostrophes (')."
                )
        return name
    
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


class OrderForm(forms.ModelForm):
    """Form for placing orders"""
    prescription_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'prescription-upload'
        }),
        help_text="Upload prescription image if required (JPG, PNG, GIF - max 5MB)"
    )
    
    class Meta:
        model = Order
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes for your order (optional)'}),
        }
    
    def clean_notes(self):
        """Validate order notes"""
        notes = self.cleaned_data.get('notes')
        if notes:
            notes = notes.strip()
            
            # Length validation
            if len(notes) > 1000:
                raise forms.ValidationError("Notes cannot exceed 1000 characters.")
            
            # Character validation: allow letters, numbers, spaces, common punctuation
            if not re.match(r'^[a-zA-Z0-9\s\.\,\-\'\!\?\(\)\/\#]+$', notes):
                raise forms.ValidationError(
                    "Notes can only contain letters, numbers, spaces, and common punctuation."
                )
        return notes
    
    def clean_prescription_image(self):
        """Validate prescription image"""
        image = self.cleaned_data.get('prescription_image')
        if image:
            # File size validation (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Prescription image file size cannot exceed 5MB.")
            
            # File type validation
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Prescription image must be in JPG, JPEG, PNG, GIF, or WebP format.")
        return image
    
    def clean_prescription_image(self):
        """Validate prescription image"""
        image = self.cleaned_data.get('prescription_image')
        if image:
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large. Maximum size is 5MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise forms.ValidationError("Only JPG, PNG, and GIF images are allowed.")
        
        return image
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        # Note: We can't access the medicine instance here since it's passed via URL parameter
        # The view will handle prescription requirement validation
        return cleaned_data


class PrescriptionForm(forms.ModelForm):
    """Form for prescription upload"""
    customer_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
        help_text="Enter your full name as it appears on your prescription"
    )
    customer_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
        help_text="We'll use this to contact you about your prescription"
    )
    customer_phone = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+251912345678'}),
        help_text="Include country code (e.g., +251 for Ethiopia)"
    )
    prescription_image = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        help_text="Upload a clear photo or scan of your prescription (JPG, PNG, max 5MB)"
    )
    notes = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional notes for the pharmacy...'}),
        help_text="Optional: Add any special instructions or notes"
    )
    
    class Meta:
        model = Prescription
        fields = ['customer_name', 'customer_email', 'customer_phone', 'prescription_image', 'notes']
    
    def clean_customer_name(self):
        """Validate customer name"""
        name = self.cleaned_data.get('customer_name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError("Name must be at least 2 characters long.")
            if len(name) > 100:
                raise forms.ValidationError("Name cannot exceed 100 characters.")
        return name
    
    def clean_customer_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('customer_phone')
        if phone:
            import re
            # Remove spaces and common characters
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not re.match(r'^[+]?[\d]{10,15}$', cleaned_phone):
                raise forms.ValidationError("Please enter a valid phone number (10-15 digits with optional country code).")
        return phone
    
    def clean_prescription_image(self):
        """Validate prescription image"""
        image = self.cleaned_data.get('prescription_image')
        if image:
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large. Maximum size is 5MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise forms.ValidationError("Only JPG, PNG, and GIF images are allowed.")
        
        return image


class IncidentReportForm(forms.ModelForm):
    """Form for creating incident reports"""
    
    class Meta:
        model = IncidentReport
        fields = ['title', 'description', 'severity']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of the issue'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Detailed description of the issue'
            }),
            'severity': forms.Select(attrs={'class': 'form-select'}),
        }


class QuickIncidentForm(forms.Form):
    """Quick form for reporting urgent incidents"""
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'What is the issue?'
        })
    )
    
    severity = forms.ChoiceField(
        choices=IncidentReport.SEVERITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Brief description of the issue'
        })
    )
    
    contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email for follow-up'
        })
    )


