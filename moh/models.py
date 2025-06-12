from django.db import models
from django.contrib.auth.models import User
from pharmacy.models import Pharmacy


class MoHPharmacyRecord(models.Model):
    """Ministry of Health official pharmacy records"""
    pharmacy = models.OneToOneField(Pharmacy, on_delete=models.CASCADE, related_name='moh_record')
    license_status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
        ('pending', 'Pending Review')
    ], default='pending')
    verification_date = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    inspection_date = models.DateField(null=True, blank=True)
    inspection_notes = models.TextField(blank=True)
    compliance_score = models.IntegerField(default=0, help_text="Score out of 100")
    
    # Document verification
    business_license_verified = models.BooleanField(default=False)
    pharmacist_certificate_verified = models.BooleanField(default=False)
    pharmacy_permit_verified = models.BooleanField(default=False)
    
    # Additional documents storage
    business_license_document = models.FileField(upload_to='moh_documents/business_licenses/', null=True, blank=True)
    pharmacist_certificate_document = models.FileField(upload_to='moh_documents/pharmacist_certificates/', null=True, blank=True)
    pharmacy_permit_document = models.FileField(upload_to='moh_documents/pharmacy_permits/', null=True, blank=True)
    inspection_report = models.FileField(upload_to='moh_documents/inspection_reports/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "MoH Pharmacy Record"
        verbose_name_plural = "MoH Pharmacy Records"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"MoH Record - {self.pharmacy.name}"


class VerificationRequest(models.Model):
    """Pharmacy verification requests to MoH"""
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='moh_verification_requests')
    request_type = models.CharField(max_length=30, choices=[
        ('initial', 'Initial License'),
        ('renewal', 'License Renewal'),
        ('modification', 'License Modification'),
        ('reinstatement', 'License Reinstatement')
    ])
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('requires_inspection', 'Requires Inspection')
    ], default='pending')
    
    submitted_date = models.DateTimeField(auto_now_add=True)
    reviewed_date = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moh_verification_reviews')
    
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Verification Request"
        verbose_name_plural = "Verification Requests"
        ordering = ['-submitted_date']
    
    def __str__(self):
        return f"{self.pharmacy.name} - {self.request_type} ({self.status})"


class MoHOfficer(models.Model):
    """Ministry of Health Officers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    officer_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, choices=[
        ('licensing', 'Pharmacy Licensing'),
        ('inspection', 'Pharmacy Inspection'),
        ('compliance', 'Regulatory Compliance'),
        ('administration', 'Administration')
    ])
    position = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "MoH Officer"
        verbose_name_plural = "MoH Officers"
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.officer_id})"


class ComplianceAlert(models.Model):
    """System alerts for compliance issues"""
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=30, choices=[
        ('license_expiry', 'License Expiring'),
        ('missing_documents', 'Missing Documents'),
        ('inspection_due', 'Inspection Due'),
        ('compliance_violation', 'Compliance Violation')
    ])
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ])
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Compliance Alert"
        verbose_name_plural = "Compliance Alerts"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.pharmacy.name} - {self.alert_type} ({self.severity})"