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


class MoHPharmacyRegistrationForm(forms.Form):
    """Comprehensive form for MoH pharmacy registration with document uploads"""
    
    REGION_CHOICES = [
        ('', 'Select Region'),
        ('addis_ababa', 'Addis Ababa'),
        ('oromia', 'Oromia'),
        ('amhara', 'Amhara'),
        ('tigray', 'Tigray'),
        ('snnp', 'Southern Nations, Nationalities, and Peoples'),
        ('afar', 'Afar'),
        ('somali', 'Somali'),
        ('benishangul', 'Benishangul-Gumuz'),
        ('gambela', 'Gambela'),
        ('harari', 'Harari'),
        ('dire_dawa', 'Dire Dawa'),
    ]
    
    WOREDA_CHOICES = [
        ('', 'Select Woreda'),
        ('arada', 'Arada'),
        ('addis_ketema', 'Addis Ketema'),
        ('akaki_kality', 'Akaki Kality'),
        ('bole', 'Bole'),
        ('gullele', 'Gullele'),
        ('kirkos', 'Kirkos'),
        ('kolfe_keranio', 'Kolfe Keranio'),
        ('lideta', 'Lideta'),
        ('nifas_silk', 'Nifas Silk-Lafto'),
        ('yeka', 'Yeka'),
        ('lemi_kura', 'Lemi Kura'),
        ('sebeta', 'Sebeta'),
        ('sululta', 'Sululta'),
        ('sendafa', 'Sendafa'),
        ('holeta', 'Holeta'),
    ]
    
    KEBELE_CHOICES = [
        ('', 'Select Kebele'),
        ('kebele_01', 'Kebele 01'),
        ('kebele_02', 'Kebele 02'),
        ('kebele_03', 'Kebele 03'),
        ('kebele_04', 'Kebele 04'),
        ('kebele_05', 'Kebele 05'),
        ('kebele_06', 'Kebele 06'),
        ('kebele_07', 'Kebele 07'),
        ('kebele_08', 'Kebele 08'),
        ('kebele_09', 'Kebele 09'),
        ('kebele_10', 'Kebele 10'),
        ('kebele_11', 'Kebele 11'),
        ('kebele_12', 'Kebele 12'),
        ('kebele_13', 'Kebele 13'),
        ('kebele_14', 'Kebele 14'),
        ('kebele_15', 'Kebele 15'),
    ]
    
    LICENSE_TYPE_CHOICES = [
        ('', 'Select License Type'),
        ('retail', 'Retail Pharmacy'),
        ('hospital', 'Hospital Pharmacy'),
        ('wholesale', 'Wholesale Pharmacy'),
        ('manufacturing', 'Manufacturing Pharmacy'),
    ]
    
    # Basic Information
    pharmacy_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter pharmacy name'
        }),
        help_text="Official registered name of the pharmacy"
    )
    
    license_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ETH-PH-XXXX-XXXX'
        }),
        help_text="Unique pharmacy license identifier"
    )
    
    license_type = forms.ChoiceField(
        choices=LICENSE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Type of pharmacy license"
    )
    
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+251-9XX-XXX-XXX'
        }),
        help_text="Contact phone number"
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'pharmacy@example.com'
        }),
        help_text="Email address (optional)"
    )
    
    # Owner & Staff Information
    owner_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full name of pharmacy owner'
        }),
        help_text="Full name of the pharmacy owner"
    )
    
    pharmacist_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name of chief pharmacist'
        }),
        help_text="Name of the licensed pharmacist in charge"
    )
    
    pharmacist_license = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ETH-PHARM-XXXX'
        }),
        help_text="Licensed pharmacist's professional license number"
    )
    
    # Location Information
    region = forms.ChoiceField(
        choices=REGION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select the region where pharmacy is located"
    )
    
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City name'
        }),
        help_text="City where pharmacy is located"
    )
    
    woreda = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Woreda name'
        }),
        help_text="Woreda (district) where pharmacy is located"
    )
    
    kebele = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kebele name'
        }),
        help_text="Kebele (neighborhood) where pharmacy is located"
    )
    
    address_detail = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Complete address including street name, building number, and landmarks'
        }),
        help_text="Detailed address description"
    )
    
    # License Validity Information
    issue_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text="Date when license was issued"
    )
    
    expiry_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text="Date when license expires"
    )
    
    STATUS_CHOICES = [
        ('', 'Select Status'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('pending_renewal', 'Pending Renewal'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Current status of the pharmacy license"
    )
    
    # Required Document Uploads
    business_license = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,.pdf,.doc,.docx'
        }),
        help_text="Upload business license document (PDF, DOC, or image)"
    )
    
    pharmacist_certificate = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,.pdf,.doc,.docx'
        }),
        help_text="Upload pharmacist professional certificate (PDF, DOC, or image)"
    )
    
    pharmacy_permit = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,.pdf,.doc,.docx'
        }),
        help_text="Upload pharmacy operation permit (PDF, DOC, or image)"
    )
    
    inspection_report = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,.pdf,.doc,.docx'
        }),
        help_text="Upload latest inspection report (PDF, DOC, or image)"
    )
    
    # Additional Information
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any additional notes or comments'
        }),
        help_text="Additional notes or comments (optional)"
    )
    
    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if license_number:
            # Check if license number already exists
            if Pharmacy.objects.filter(license_number=license_number).exists():
                raise forms.ValidationError(
                    "A pharmacy with this license number already exists."
                )
        return license_number
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove spaces and dashes
            phone = phone.replace(' ', '').replace('-', '')
            if not phone.startswith('+251') and not phone.startswith('09'):
                raise forms.ValidationError(
                    "Please enter a valid Ethiopian phone number (+251XXXXXXXXX or 09XXXXXXXX)"
                )
        return phone
    
    def clean_business_license(self):
        file = self.cleaned_data.get('business_license')
        if file:
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "File size must be less than 5MB"
                )
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(
                    "Only PDF, DOC, DOCX, JPG, JPEG, and PNG files are allowed"
                )
        return file
    
    def clean_pharmacist_certificate(self):
        file = self.cleaned_data.get('pharmacist_certificate')
        if file:
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "File size must be less than 5MB"
                )
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(
                    "Only PDF, DOC, DOCX, JPG, JPEG, and PNG files are allowed"
                )
        return file
    
    def clean_pharmacy_permit(self):
        file = self.cleaned_data.get('pharmacy_permit')
        if file:
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "File size must be less than 5MB"
                )
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(
                    "Only PDF, DOC, DOCX, JPG, JPEG, and PNG files are allowed"
                )
        return file