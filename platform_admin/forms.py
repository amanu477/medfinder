from django import forms
from django.contrib.auth import authenticate
import re

class PlatformAdminLoginForm(forms.Form):
    """Custom login form for platform admin"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
    
    def clean_username(self):
        """Validate username"""
        username = self.cleaned_data.get('username')
        if username:
            username = username.strip()
            
            # Length validation
            if len(username) < 3:
                raise forms.ValidationError("Username must be at least 3 characters long.")
            if len(username) > 150:
                raise forms.ValidationError("Username cannot exceed 150 characters.")
            
            # Character validation: allow letters, numbers, underscore, hyphen
            if not re.match(r'^[a-zA-Z0-9_\-]+$', username):
                raise forms.ValidationError(
                    "Username can only contain letters, numbers, underscore (_), and hyphen (-)."
                )
        return username
    
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
                    "Please enter a correct username and password."
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")
            elif not self.user_cache.is_superuser:
                raise forms.ValidationError(
                    "You must be a superuser to access the platform admin."
                )
        
        return self.cleaned_data
    
    def get_user(self):
        return self.user_cache