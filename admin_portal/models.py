from django.db import models
from django.contrib.auth.models import User
from pharmacy.models import Pharmacy
from customer.models import Customer, Order, Prescription


class AdminProfile(models.Model):
    """Admin user profiles"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admin_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, choices=[
        ('system', 'System Administration'),
        ('operations', 'Operations Management'),
        ('support', 'Customer Support'),
        ('finance', 'Finance & Billing'),
        ('security', 'Security & Compliance')
    ])
    access_level = models.CharField(max_length=20, choices=[
        ('read_only', 'Read Only'),
        ('editor', 'Editor'),
        ('admin', 'Administrator'),
        ('super_admin', 'Super Administrator')
    ], default='editor')
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.admin_id})"


class SystemNotification(models.Model):
    """System-wide notifications from admin"""
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=[
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('maintenance', 'Maintenance'),
        ('update', 'System Update'),
        ('alert', 'Alert')
    ])
    target_audience = models.CharField(max_length=20, choices=[
        ('all', 'All Users'),
        ('customers', 'Customers Only'),
        ('pharmacies', 'Pharmacies Only'),
        ('moh', 'MoH Officers Only')
    ])
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "System Notification"
        verbose_name_plural = "System Notifications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.target_audience})"


class PlatformAnalytics(models.Model):
    """Platform usage analytics"""
    date = models.DateField(unique=True)
    
    # User metrics
    new_customers = models.IntegerField(default=0)
    new_pharmacies = models.IntegerField(default=0)
    active_customers = models.IntegerField(default=0)
    active_pharmacies = models.IntegerField(default=0)
    
    # Activity metrics
    medicine_searches = models.IntegerField(default=0)
    prescriptions_uploaded = models.IntegerField(default=0)
    orders_placed = models.IntegerField(default=0)
    pharmacy_registrations = models.IntegerField(default=0)
    
    # Financial metrics
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Platform Analytics"
        verbose_name_plural = "Platform Analytics"
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.date}"


class SystemSettings(models.Model):
    """Global system settings"""
    setting_name = models.CharField(max_length=100, unique=True)
    setting_value = models.TextField()
    setting_type = models.CharField(max_length=20, choices=[
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('float', 'Float')
    ])
    description = models.TextField()
    is_editable = models.BooleanField(default=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return f"{self.setting_name}: {self.setting_value}"


class AdminAuditLog(models.Model):
    """Audit log for admin actions"""
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    target_model = models.CharField(max_length=50)
    target_id = models.CharField(max_length=50)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Admin Audit Log"
        verbose_name_plural = "Admin Audit Logs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.action} on {self.target_model}"


class PlatformReport(models.Model):
    """Generated platform reports"""
    report_name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=[
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('custom', 'Custom Report')
    ])
    date_range_start = models.DateField()
    date_range_end = models.DateField()
    report_data = models.JSONField()
    file_path = models.FileField(upload_to='admin_reports/', null=True, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Platform Report"
        verbose_name_plural = "Platform Reports"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.report_name} ({self.report_type})"


class MaintenanceMode(models.Model):
    """System maintenance mode control"""
    is_active = models.BooleanField(default=False)
    title = models.CharField(max_length=200, default="System Maintenance")
    message = models.TextField(default="The system is currently under maintenance. Please try again later.")
    estimated_duration = models.CharField(max_length=100, blank=True)
    affected_services = models.JSONField(default=list)
    bypass_ips = models.JSONField(default=list, help_text="IP addresses that can bypass maintenance mode")
    
    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Maintenance Mode"
        verbose_name_plural = "Maintenance Mode"
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"Maintenance Mode ({status})"