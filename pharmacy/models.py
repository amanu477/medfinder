from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Pharmacy(models.Model):
    """Model for storing pharmacy information"""
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    verification_documents = models.FileField(upload_to='pharmacy_documents/', null=True, blank=True)
    business_license = models.FileField(upload_to='pharmacy_documents/', null=True, blank=True)
    pharmacist_certificate = models.FileField(upload_to='pharmacy_documents/', null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    verified_at = models.DateTimeField(null=True, blank=True)
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
