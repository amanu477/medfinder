"""
Admin Reporting and Issue Tracking System
Models for tracking technical issues, security concerns, and system reports
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from pharmacy.models import Pharmacy


class IncidentReport(models.Model):
    """Model for tracking system incidents and issues"""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    CATEGORY_CHOICES = [
        ('technical', 'Technical Issue'),
        ('security', 'Security Concern'),
        ('data', 'Data Integrity'),
        ('performance', 'Performance Issue'),
        ('user_report', 'User Report'),
        ('pharmacy_report', 'Pharmacy Report'),
        ('verification', 'Verification Issue'),
        ('moh_sync', 'MoH Synchronization'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    
    # Reporter Information
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reporter_email = models.EmailField(blank=True, null=True)
    reporter_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Related Objects
    related_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.SET_NULL, null=True, blank=True)
    related_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_incidents')
    
    # Technical Details
    error_message = models.TextField(blank=True, null=True)
    stack_trace = models.TextField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    url_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Resolution
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents')
    resolution_notes = models.TextField(blank=True, null=True)
    resolution_date = models.DateTimeField(blank=True, null=True)
    
    # File Attachments
    screenshot = models.ImageField(upload_to='incident_reports/screenshots/', blank=True, null=True)
    log_file = models.FileField(upload_to='incident_reports/logs/', blank=True, null=True)
    additional_file = models.FileField(upload_to='incident_reports/files/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Incident Report"
        verbose_name_plural = "Incident Reports"
    
    def __str__(self):
        return f"#{self.id} - {self.title} ({self.get_severity_display()})"
    
    def mark_resolved(self, resolution_notes=None, resolved_by=None):
        """Mark incident as resolved"""
        self.status = 'resolved'
        self.resolution_date = timezone.now()
        if resolution_notes:
            self.resolution_notes = resolution_notes
        if resolved_by:
            self.assigned_to = resolved_by
        self.save()
    
    @property
    def is_critical(self):
        """Check if incident is critical severity"""
        return self.severity == 'critical'
    
    @property
    def days_open(self):
        """Calculate days since incident was opened"""
        if self.status in ['resolved', 'closed']:
            return (self.resolution_date or self.updated_at).date() - self.created_at.date()
        return (timezone.now().date() - self.created_at.date()).days


class SecurityAlert(models.Model):
    """Model for tracking security-related alerts and threats"""
    ALERT_TYPE_CHOICES = [
        ('login_attempt', 'Failed Login Attempts'),
        ('data_breach', 'Potential Data Breach'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('malware', 'Malware Detection'),
        ('ddos', 'DDoS Attack'),
        ('injection', 'SQL/Code Injection Attempt'),
        ('xss', 'Cross-Site Scripting'),
        ('csrf', 'CSRF Attack'),
        ('file_upload', 'Malicious File Upload'),
        ('other', 'Other Security Concern'),
    ]
    
    RISK_LEVEL_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    # Alert Details
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES)
    description = models.TextField()
    
    # Source Information
    source_ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    target_url = models.CharField(max_length=500, blank=True, null=True)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Detection Details
    detection_method = models.CharField(max_length=100, blank=True, null=True)
    detection_rules = models.TextField(blank=True, null=True)
    raw_data = models.JSONField(blank=True, null=True)
    
    # Response
    is_blocked = models.BooleanField(default=False)
    response_action = models.CharField(max_length=200, blank=True, null=True)
    investigated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='investigated_alerts')
    
    # Timestamps
    detected_at = models.DateTimeField(auto_now_add=True)
    investigated_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-detected_at']
        verbose_name = "Security Alert"
        verbose_name_plural = "Security Alerts"
    
    def __str__(self):
        return f"Security Alert #{self.id} - {self.get_alert_type_display()} ({self.get_risk_level_display()})"


class SystemHealthMetric(models.Model):
    """Model for tracking system health and performance metrics"""
    METRIC_TYPE_CHOICES = [
        ('response_time', 'Response Time'),
        ('error_rate', 'Error Rate'),
        ('user_sessions', 'Active User Sessions'),
        ('database_performance', 'Database Performance'),
        ('memory_usage', 'Memory Usage'),
        ('cpu_usage', 'CPU Usage'),
        ('disk_space', 'Disk Space'),
        ('network_traffic', 'Network Traffic'),
    ]
    
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPE_CHOICES)
    value = models.FloatField()
    unit = models.CharField(max_length=20)  # e.g., 'ms', '%', 'MB', 'requests/min'
    threshold_warning = models.FloatField(blank=True, null=True)
    threshold_critical = models.FloatField(blank=True, null=True)
    
    # Additional Data
    details = models.JSONField(blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
        verbose_name = "System Health Metric"
        verbose_name_plural = "System Health Metrics"
    
    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value}{self.unit}"
    
    @property
    def status(self):
        """Determine metric status based on thresholds"""
        if self.threshold_critical and self.value >= self.threshold_critical:
            return 'critical'
        elif self.threshold_warning and self.value >= self.threshold_warning:
            return 'warning'
        return 'normal'


class AdminNotification(models.Model):
    """Model for admin notifications and alerts"""
    NOTIFICATION_TYPE_CHOICES = [
        ('incident', 'New Incident Report'),
        ('security', 'Security Alert'),
        ('system', 'System Issue'),
        ('pharmacy', 'Pharmacy Registration'),
        ('verification', 'Verification Request'),
        ('maintenance', 'Maintenance Required'),
        ('update', 'System Update'),
        ('backup', 'Backup Status'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    notification_type = models.CharField(max_length=15, choices=NOTIFICATION_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Recipients
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    
    # Related Objects
    related_incident = models.ForeignKey(IncidentReport, on_delete=models.CASCADE, blank=True, null=True)
    related_security_alert = models.ForeignKey(SecurityAlert, on_delete=models.CASCADE, blank=True, null=True)
    
    # Action URL
    action_url = models.CharField(max_length=500, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Admin Notification"
        verbose_name_plural = "Admin Notifications"
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
    
    def mark_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()