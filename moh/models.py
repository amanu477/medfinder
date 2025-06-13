from django.db import models
from django.contrib.auth.models import User


class MoHPharmacyRegistry(models.Model):
    """Ministry of Health independent pharmacy registry - separate from platform registrations"""
    
    REGION_CHOICES = [
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
    
    LICENSE_TYPE_CHOICES = [
        ('retail', 'Retail Pharmacy'),
        ('hospital', 'Hospital Pharmacy'),
        ('wholesale', 'Wholesale Pharmacy'),
        ('manufacturing', 'Manufacturing Pharmacy'),
    ]
    
    LICENSE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
        ('pending', 'Pending Review'),
        ('expired', 'Expired')
    ]
    
    # Basic Information - Independent of platform pharmacy records
    pharmacy_name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=50, unique=True)
    owner_name = models.CharField(max_length=100)
    pharmacist_name = models.CharField(max_length=100)
    pharmacist_license = models.CharField(max_length=50)
    
    # Location Information
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='addis_ababa')
    city = models.CharField(max_length=100, default='Addis Ababa')
    woreda = models.CharField(max_length=100, default='Not Specified')
    kebele = models.CharField(max_length=100, default='Not Specified')
    address_detail = models.TextField(default='Address not specified')
    
    # License Details
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPE_CHOICES, default='retail')
    license_status = models.CharField(max_length=20, choices=LICENSE_STATUS_CHOICES, default='pending')
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Contact Information
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    # MoH Administrative
    moh_officer = models.CharField(max_length=100, help_text="MoH officer who registered this pharmacy")
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
    
    @property
    def is_license_valid(self):
        """Check if license is still valid"""
        from datetime import date
        return self.license_status == 'active' and self.expiry_date >= date.today()
    
    @property
    def days_until_expiry(self):
        """Days until license expires"""
        from datetime import date
        if self.expiry_date:
            return (self.expiry_date - date.today()).days
        return None
    
    def get_license_type_display(self):
        """Get display name for license type"""
        return dict(self.LICENSE_TYPE_CHOICES).get(self.license_type, self.license_type)
    
    def get_region_display(self):
        """Get display name for region"""
        return dict(self.REGION_CHOICES).get(self.region, self.region)
    
    def get_license_status_display(self):
        """Get display name for license status"""
        return dict(self.LICENSE_STATUS_CHOICES).get(self.license_status, self.license_status)

    def __str__(self):
        return f"MoH Record - {self.pharmacy_name} ({self.license_number})"


class VerificationRequest(models.Model):
    """Pharmacy verification requests to MoH"""
    pharmacy_license = models.CharField(max_length=50, help_text="License number of the requesting pharmacy")
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