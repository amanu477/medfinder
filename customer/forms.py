from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Prescription, Customer, Order, IncidentReport, SecurityAlert, AdminNotification
from pharmacy.models import Pharmacy

class CustomerRegistrationForm(UserCreationForm):
    """Form for customer registration"""
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

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


class CustomerProfileForm(forms.ModelForm):
    """Form for editing customer profile"""
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class OrderForm(forms.ModelForm):
    """Form for placing orders"""
    class Meta:
        model = Order
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes for your order (optional)'}),
        }


class PrescriptionForm(forms.ModelForm):
    """Form for prescription upload"""
    customer_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    customer_phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    prescription_image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    
    class Meta:
        model = Prescription
        fields = ['customer_name', 'customer_email', 'customer_phone', 'prescription_image', 'notes']


class IncidentReportForm(forms.ModelForm):
    """Form for creating incident reports"""
    
    class Meta:
        model = IncidentReport
        fields = [
            'title', 'description', 'category', 'severity', 'reporter_email', 
            'reporter_phone', 'related_pharmacy', 'error_message', 'url_path',
            'screenshot', 'log_file', 'additional_file'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of the issue'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Detailed description of the issue, steps to reproduce, expected vs actual behavior'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'reporter_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact email for follow-up'
            }),
            'reporter_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number (optional)'
            }),
            'related_pharmacy': forms.Select(attrs={'class': 'form-select'}),
            'error_message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Error message or code if any'
            }),
            'url_path': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL where the issue occurred'
            }),
            'screenshot': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'log_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.log,.txt'
            }),
            'additional_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
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
    
    category = forms.ChoiceField(
        choices=IncidentReport.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
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


class SecurityAlertForm(forms.ModelForm):
    """Form for creating security alerts"""
    
    class Meta:
        model = SecurityAlert
        fields = [
            'alert_type', 'risk_level', 'description', 'source_ip',
            'target_url', 'target_user', 'detection_method', 'response_action'
        ]
        
        widgets = {
            'alert_type': forms.Select(attrs={'class': 'form-select'}),
            'risk_level': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detailed description of the security concern'
            }),
            'source_ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'IP address of the source'
            }),
            'target_url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL that was targeted'
            }),
            'target_user': forms.Select(attrs={'class': 'form-select'}),
            'detection_method': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'How was this detected?'
            }),
            'response_action': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Action taken in response'
            }),
        }