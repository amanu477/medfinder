from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class MoHPharmacyRecord(models.Model):
    """Ministry of Health pharmacy registry - pre-registered legitimate pharmacies"""
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
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    # Basic Information
    pharmacy_name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=50, unique=True)
    owner_name = models.CharField(max_length=100)
    pharmacist_name = models.CharField(max_length=100)
    pharmacist_license = models.CharField(max_length=50)
    
    # Location Information
    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    city = models.CharField(max_length=100)
    woreda = models.CharField(max_length=100)
    kebele = models.CharField(max_length=100)
    address_detail = models.TextField()
    
    # License Details
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPE_CHOICES, default='retail')
    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Contact Information
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    # Document Uploads
    business_license_document = models.FileField(upload_to='moh_documents/business_licenses/', blank=True, null=True, help_text="Business license document")
    pharmacist_certificate_document = models.FileField(upload_to='moh_documents/pharmacist_certificates/', blank=True, null=True, help_text="Pharmacist certificate document")
    pharmacy_permit_document = models.FileField(upload_to='moh_documents/pharmacy_permits/', blank=True, null=True, help_text="Pharmacy operating permit")
    inspection_report_document = models.FileField(upload_to='moh_documents/inspection_reports/', blank=True, null=True, help_text="Latest inspection report")
    
    # Administrative
    moh_officer = models.CharField(max_length=100, help_text="MoH officer who registered this pharmacy")
    registration_date = models.DateTimeField(auto_now_add=True)
    last_inspection_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-registration_date']
        verbose_name = "Ministry of Health Pharmacy Record"
        verbose_name_plural = "Ministry of Health Pharmacy Records"
    
    def __str__(self):
        return f"{self.pharmacy_name} - {self.license_number}"
    
    @property
    def is_license_valid(self):
        """Check if license is still valid"""
        from datetime import date
        return self.status == 'active' and self.expiry_date >= date.today()
    
    @property
    def days_until_expiry(self):
        """Days until license expires"""
        from datetime import date
        if self.expiry_date:
            return (self.expiry_date - date.today()).days
        return None
from datetime import timedelta

class Pharmacy(models.Model):
    """Model for storing pharmacy information"""
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    LICENSE_TYPE_CHOICES = [
        ('retail', 'Retail Pharmacy'),
        ('hospital', 'Hospital Pharmacy'),
        ('wholesale', 'Wholesale Pharmacy'),
        ('manufacturing', 'Manufacturing Pharmacy'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPE_CHOICES, default='retail')
    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_24_hour = models.BooleanField(default=False, help_text="Check if pharmacy operates 24/7")
    is_active = models.BooleanField(default=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    verification_documents = models.FileField(upload_to='pharmacy_documents/', null=True, blank=True)
    business_license = models.FileField(upload_to='pharmacy_documents/', null=True, blank=True)
    pharmacist_certificate = models.FileField(upload_to='pharmacy_documents/', null=True, blank=True)
    
    def is_open_now(self):
        """Check if pharmacy is currently open"""
        # 24-hour pharmacies are always open
        if self.is_24_hour:
            return True
            
        from django.utils import timezone
        # Use timezone-aware current time (Ethiopia time)
        current_time = timezone.now().time()
        
        # Handle case where pharmacy operates past midnight
        if self.opening_time <= self.closing_time:
            # Normal hours (e.g., 8:00 AM to 10:00 PM)
            return self.opening_time <= current_time < self.closing_time
        else:
            # Overnight hours (e.g., 6:00 PM to 6:00 AM)
            return current_time >= self.opening_time or current_time < self.closing_time
    
    def get_status_display(self):
        """Get human-readable status"""
        if not self.is_active:
            return "Temporarily Closed"
        elif self.verification_status != 'verified':
            return "Pending Verification"
        elif self.is_open_now():
            return "Open Now"
        else:
            return "Closed"
    
    def get_next_opening_time(self):
        """Get the next time pharmacy will be open"""
        # 24-hour pharmacies are always open
        if self.is_24_hour:
            return None
            
        from django.utils import timezone
        
        if self.is_open_now():
            return None
        
        current_time = timezone.now().time()
        
        # Handle normal hours (opening_time <= closing_time)
        if self.opening_time <= self.closing_time:
            # If today's opening time hasn't passed yet
            if current_time < self.opening_time:
                return f"Opens at {self.opening_time.strftime('%I:%M %p')}"
            else:
                # Opens tomorrow at opening time
                return f"Opens tomorrow at {self.opening_time.strftime('%I:%M %p')}"
        else:
            # Handle overnight hours (opening_time > closing_time)
            # If we're before closing time, we're still in yesterday's open period
            if current_time < self.closing_time:
                return None  # Actually still open from yesterday
            # If we're after closing time but before opening time
            elif current_time < self.opening_time:
                return f"Opens at {self.opening_time.strftime('%I:%M %p')}"
            else:
                # Opens tomorrow at opening time
                return f"Opens tomorrow at {self.opening_time.strftime('%I:%M %p')}"
    rejection_reason = models.TextField(blank=True, null=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Ministry of Health verification data
    moh_verification_data = models.JSONField(blank=True, null=True, help_text="Ministry of Health verification results")
    moh_verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Verification'),
            ('verified', 'MoH Verified'),
            ('failed', 'MoH Verification Failed'),
            ('manual_review', 'Requires Manual Review')
        ],
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_expiring_medicines(self):
        """Get medicines expiring in the next 30 days"""
        thirty_days_later = timezone.now().date() + timedelta(days=30)
        return self.medicine_set.filter(
            expiry_date__lte=thirty_days_later,
            expiry_date__gte=timezone.now().date()
        )

class Medicine(models.Model):
    """Model for storing medicine information"""
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    medicine_image = models.ImageField(upload_to='medicines/', null=True, blank=True)
    expiry_date = models.DateField()
    is_available = models.BooleanField(default=True)
    prescription_required = models.BooleanField(default=True, help_text="Check if this medicine requires a prescription")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def is_expired(self):
        """Check if medicine is expired"""
        return self.expiry_date < timezone.now().date()

    def is_expiring_soon(self):
        """Check if medicine is expiring in the next 30 days"""
        thirty_days_later = timezone.now().date() + timedelta(days=30)
        return self.expiry_date <= thirty_days_later and not self.is_expired()
