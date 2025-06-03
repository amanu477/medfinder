from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Prescription, Customer, Order

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