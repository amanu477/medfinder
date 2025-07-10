from django.db import models
from django.contrib.auth.models import User
from pharmacy.models import Pharmacy

class Customer(models.Model):
    """Model for storing customer information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Cart(models.Model):
    """Model for storing customer shopping cart"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.customer.name}"

    def get_total_items(self):
        """Get total number of items in the cart"""
        return sum(item.quantity for item in self.cartitem_set.all())

    def get_total_amount(self):
        """Get total amount for all items in the cart"""
        return sum(item.get_total_price() for item in self.cartitem_set.all())

    def clear(self):
        """Clear all items from the cart"""
        self.cartitem_set.all().delete()

class CartItem(models.Model):
    """Model for storing individual items in a cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    medicine = models.ForeignKey('pharmacy.Medicine', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    prescription_image = models.ImageField(upload_to='cart_prescriptions/', blank=True, null=True)
    ocr_validation_data = models.JSONField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'medicine']

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"

    def get_total_price(self):
        """Get total price for this item"""
        return self.quantity * self.medicine.price

class Order(models.Model):
    """Model for storing medicine orders"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
        ('completed', 'Completed'),
        ('ready_for_delivery', 'Ready for Delivery'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    prescription_image = models.ImageField(upload_to='order_prescriptions/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"

    def get_total_items(self):
        """Get total number of items in the order"""
        return sum(item.quantity for item in self.orderitem_set.all())

    def calculate_total(self):
        """Calculate total amount for the order"""
        total = sum(item.get_total_price() for item in self.orderitem_set.all())
        self.total_amount = total
        self.save()
        return total

class OrderItem(models.Model):
    """Model for storing individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    medicine = models.ForeignKey('pharmacy.Medicine', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"

    def get_total_price(self):
        """Get total price for this item"""
        return self.quantity * self.price


class Payment(models.Model):
    """Model for tracking Chapa payments"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    tx_ref = models.CharField(max_length=100, unique=True)  # Chapa transaction reference
    chapa_tx_ref = models.CharField(max_length=100, blank=True, null=True)  # Chapa's transaction reference
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ETB')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Customer information for payment
    customer_email = models.EmailField()
    customer_first_name = models.CharField(max_length=50)
    customer_last_name = models.CharField(max_length=50)
    customer_phone = models.CharField(max_length=20)
    
    # Chapa response data
    chapa_response = models.JSONField(blank=True, null=True)
    checkout_url = models.URLField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.tx_ref} - {self.amount} {self.currency} ({self.status})"

class Prescription(models.Model):
    """Model for storing prescription information"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True, blank=True)
    prescription_image = models.ImageField(upload_to='prescriptions/')
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription #{self.id} - {self.customer_name}"

class VerificationRequest(models.Model):
    """Model for tracking verification requests sent to MoH"""
    STATUS_CHOICES = (
        ('pending', 'Pending MoH Response'),
        ('approved', 'MoH Confirmed'),
        ('rejected', 'MoH Denied'),
        ('manual_review', 'Requires Manual Review'),
    )
    
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='customer_verification_requests')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_verification_requests')
    license_number = models.CharField(max_length=50)
    pharmacy_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    moh_response = models.JSONField(blank=True, null=True)
    moh_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Verification Request: {self.pharmacy_name} ({self.license_number})"


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
    
    def __str__(self):
        return f"#{self.id} - {self.title} ({self.get_severity_display()})"


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
    
    def __str__(self):
        return f"Security Alert #{self.id} - {self.get_alert_type_display()} ({self.get_risk_level_display()})"


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
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"


class Receipt(models.Model):
    """Model for storing payment receipts"""
    
    # Core receipt information
    receipt_number = models.CharField(max_length=20, unique=True)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='receipt')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='receipts')
    
    # Customer and pharmacy information
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='receipts')
    pharmacy = models.ForeignKey('pharmacy.Pharmacy', on_delete=models.CASCADE, related_name='receipts')
    
    # Receipt content (stored as JSON for flexibility)
    receipt_data = models.JSONField(help_text="Complete receipt data including all items and totals")
    
    # Receipt metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    is_printed = models.BooleanField(default=False)
    print_count = models.PositiveIntegerField(default=0)
    last_viewed_by_customer = models.DateTimeField(blank=True, null=True)
    last_viewed_by_pharmacy = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['customer', '-generated_at']),
            models.Index(fields=['pharmacy', '-generated_at']),
            models.Index(fields=['receipt_number']),
        ]
    
    def __str__(self):
        return f"Receipt #{self.receipt_number} - Order #{self.order.id}"
    
    def generate_receipt_number(self):
        """Generate unique receipt number"""
        import uuid
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"RCP-{timestamp}-{unique_id}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)
    
    def mark_viewed_by_customer(self):
        """Mark receipt as viewed by customer"""
        from django.utils import timezone
        self.last_viewed_by_customer = timezone.now()
        self.save(update_fields=['last_viewed_by_customer'])
    
    def mark_viewed_by_pharmacy(self):
        """Mark receipt as viewed by pharmacy"""
        from django.utils import timezone
        self.last_viewed_by_pharmacy = timezone.now()
        self.save(update_fields=['last_viewed_by_pharmacy'])
    
    def increment_print_count(self):
        """Increment print count"""
        self.print_count += 1
        self.is_printed = True
        self.save(update_fields=['print_count', 'is_printed'])
    
    def get_receipt_data(self):
        """Get formatted receipt data"""
        return {
            'receipt_number': self.receipt_number,
            'order_id': self.order.id,
            'customer_name': self.customer.name,
            'customer_email': self.customer.email,
            'pharmacy_name': self.pharmacy.name,
            'pharmacy_address': self.pharmacy.address,
            'payment_data': {
                'tx_ref': self.payment.tx_ref,
                'amount': str(self.payment.amount),
                'currency': self.payment.currency,
                'status': self.payment.get_status_display(),
                'paid_at': self.payment.paid_at.isoformat() if self.payment.paid_at else None,
                'chapa_tx_ref': self.payment.chapa_tx_ref,
            },
            'order_data': self.receipt_data,
            'generated_at': self.generated_at.isoformat(),
            'print_count': self.print_count,
        }