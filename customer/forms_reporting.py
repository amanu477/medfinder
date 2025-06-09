"""
Forms for Admin Reporting and Issue Tracking System
"""
from django import forms
from django.contrib.auth.models import User
from .models_reporting import IncidentReport, SecurityAlert, AdminNotification


class IncidentReportForm(forms.ModelForm):
    """Form for creating and editing incident reports"""
    
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
        
        help_texts = {
            'severity': 'Low: Minor inconvenience, Medium: Affects functionality, High: Major impact, Critical: System down',
            'screenshot': 'Upload a screenshot if it helps explain the issue',
            'log_file': 'Upload relevant log files if available',
        }


class IncidentResolutionForm(forms.ModelForm):
    """Form for resolving incident reports"""
    
    class Meta:
        model = IncidentReport
        fields = ['status', 'resolution_notes', 'assigned_to']
        
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'resolution_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the resolution steps taken and outcome'
            }),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }


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


class AdminNotificationForm(forms.ModelForm):
    """Form for creating admin notifications"""
    
    class Meta:
        model = AdminNotification
        fields = ['notification_type', 'priority', 'title', 'message', 'recipient', 'action_url']
        
        widgets = {
            'notification_type': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Notification title'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Notification message'
            }),
            'recipient': forms.Select(attrs={'class': 'form-select'}),
            'action_url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL for action button (optional)'
            }),
        }


class BulkNotificationForm(forms.Form):
    """Form for sending notifications to multiple admins"""
    notification_type = forms.ChoiceField(
        choices=AdminNotification.NOTIFICATION_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    priority = forms.ChoiceField(
        choices=AdminNotification.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Notification title'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Notification message'
        })
    )
    
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_staff=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Select admin users to notify"
    )
    
    action_url = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'URL for action button (optional)'
        })
    )


class SystemHealthFilterForm(forms.Form):
    """Form for filtering system health metrics"""
    metric_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Metrics')] + list(IncidentReport.CATEGORY_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    date_to = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Statuses'),
            ('normal', 'Normal'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )