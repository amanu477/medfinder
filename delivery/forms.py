from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import DeliveryPerson, Delivery, DeliveryTracking, DeliveryZone
import re


class DeliveryPersonCreationForm(UserCreationForm):
    """Form for creating delivery person accounts"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    national_id = forms.CharField(max_length=20, required=True)
    vehicle_type = forms.ChoiceField(choices=[
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('car', 'Car'),
        ('on_foot', 'On Foot'),
    ], required=True)
    vehicle_plate = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    
    def clean_national_id(self):
        """Validate national ID format and uniqueness"""
        national_id = self.cleaned_data.get('national_id')
        if national_id:
            # Remove any spaces or special characters
            cleaned_id = re.sub(r'[^\d]', '', national_id)
            
            # Check if it contains exactly 12 digits
            if len(cleaned_id) != 12:
                raise forms.ValidationError('National ID must contain exactly 12 numbers.')
            
            # Check if it contains only digits
            if not cleaned_id.isdigit():
                raise forms.ValidationError('National ID must contain only numbers.')
            
            # Check uniqueness
            if DeliveryPerson.objects.filter(national_id=cleaned_id).exists():
                raise forms.ValidationError(f'A delivery person with National ID {cleaned_id} already exists. Please use a different National ID.')
            
            return cleaned_id
        return national_id
    
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
                raise forms.ValidationError("Phone number must be in Ethiopian format (+251XXXXXXXXX)")
            
            # Validate length and format - should be +251 + 1 digit + 8 digits (total 10 digits after +251)
            if not re.match(r'^\+251[1-9]\d{8}$', cleaned_phone):
                raise forms.ValidationError("Invalid Ethiopian phone number format. Use +251XXXXXXXXX (1 digit + 8 digits)")
            
            return cleaned_phone
        return phone
    
    def clean_email(self):
        """Validate that email is unique"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'A user with email {email} already exists. Please use a different email address.')
        return email


class DeliveryPersonForm(forms.ModelForm):
    """Form for updating delivery person details"""
    class Meta:
        model = DeliveryPerson
        fields = ['phone', 'vehicle_type', 'vehicle_plate', 'is_available']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DeliveryAssignmentForm(forms.ModelForm):
    """Form for assigning delivery to delivery person"""
    class Meta:
        model = Delivery
        fields = ['delivery_person', 'pharmacy_notes', 'estimated_delivery_time']
        widgets = {
            'delivery_person': forms.Select(attrs={'class': 'form-control'}),
            'pharmacy_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estimated_delivery_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        pharmacy = kwargs.pop('pharmacy', None)
        super().__init__(*args, **kwargs)
        if pharmacy:
            self.fields['delivery_person'].queryset = DeliveryPerson.objects.filter(
                pharmacy=pharmacy, is_active=True, is_available=True
            )
    
    def clean_estimated_delivery_time(self):
        """Validate that estimated delivery time is not in the past"""
        from django.utils import timezone
        
        estimated_time = self.cleaned_data.get('estimated_delivery_time')
        
        if estimated_time:
            now = timezone.now()
            
            # Only prevent selecting past dates - be generous with time validation
            if estimated_time.date() < now.date():
                raise forms.ValidationError(
                    'Please select a future date and time. You cannot schedule deliveries in the past.'
                )
        
        return estimated_time


class DeliveryStatusUpdateForm(forms.ModelForm):
    """Form for updating delivery status"""
    class Meta:
        model = Delivery
        fields = ['status', 'delivery_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'delivery_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict status choices for delivery personnel
        if self.instance and self.instance.status == 'assigned':
            # From assigned, can only go to picked_up or on_the_way
            self.fields['status'].choices = [
                ('assigned', 'Assigned'),
                ('picked_up', 'Picked Up'),
                ('in_transit', 'On The Way'),
            ]
        elif self.instance and self.instance.status == 'picked_up':
            # From picked_up, can only go to in_transit
            self.fields['status'].choices = [
                ('picked_up', 'Picked Up'),
                ('in_transit', 'On The Way'),
            ]
        elif self.instance and self.instance.status == 'in_transit':
            # From in_transit, can only go to arrived or delivered
            self.fields['status'].choices = [
                ('in_transit', 'On The Way'),
                ('arrived', 'Arrived'),
                ('delivered', 'Complete'),
            ]
        elif self.instance and self.instance.status == 'arrived':
            # From arrived, can only go to delivered
            self.fields['status'].choices = [
                ('arrived', 'Arrived'),
                ('delivered', 'Complete'),
            ]
        else:
            # Default choices (should not happen for delivery personnel)
            self.fields['status'].choices = [
                ('assigned', 'Assigned'),
                ('picked_up', 'Picked Up'),
                ('in_transit', 'On The Way'),
                ('arrived', 'Arrived'),
                ('delivered', 'Complete'),
            ]


class DeliveryTrackingForm(forms.ModelForm):
    """Form for adding delivery tracking points"""
    class Meta:
        model = DeliveryTracking
        fields = ['latitude', 'longitude', 'status', 'notes']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class CustomerLocationForm(forms.Form):
    """Form for customer to set delivery location"""
    address = forms.CharField(
        max_length=255,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Enter your detailed delivery address"
    )
    latitude = forms.DecimalField(
        max_digits=10, decimal_places=8,
        widget=forms.HiddenInput()
    )
    longitude = forms.DecimalField(
        max_digits=11, decimal_places=8,
        widget=forms.HiddenInput()
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Phone number for delivery contact"
    )


class DeliveryZoneForm(forms.ModelForm):
    """Form for creating delivery zones"""
    class Meta:
        model = DeliveryZone
        fields = ['name', 'delivery_fee', 'estimated_delivery_time', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estimated_delivery_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CustomerFeedbackForm(forms.ModelForm):
    """Form for customer delivery feedback"""
    class Meta:
        model = Delivery
        fields = ['customer_feedback', 'customer_rating']
        widgets = {
            'customer_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'customer_rating': forms.Select(
                choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
        }