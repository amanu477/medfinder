from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Customer(models.Model):
    """Customer model for storing customer information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)  # Email verification status

    def __str__(self):
        return f"{self.name} - {self.email}"

class EmailVerification(models.Model):
    """Model for storing email verification codes"""
    email = models.EmailField()
    verification_code = models.CharField(max_length=6)
    user_type = models.CharField(max_length=20, choices=[
        ('customer', 'Customer'),
        ('pharmacy', 'Pharmacy')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Verification for {self.email} - {self.verification_code}"
    
    def is_expired(self):
        """Check if verification code has expired (15 minutes)"""
        return timezone.now() > self.created_at + timedelta(minutes=15)
    
    def is_valid(self):
        """Check if verification code is valid"""
        return not self.used and not self.is_expired()

# Keep existing models
class Prescription(models.Model):
    """Model for storing prescription information"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    prescription_image = models.ImageField(upload_to='prescriptions/')
    pharmacy = models.ForeignKey('pharmacy.Pharmacy', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription by {self.customer_name}"

class Order(models.Model):
    """Model for storing order information"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('completed', 'Completed'),
        ('on_the_way', 'On The Way'),
        ('arrived', 'Arrived'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey('pharmacy.Pharmacy', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    prescription_image = models.ImageField(upload_to='order_prescriptions/', blank=True, null=True)
    
    # Scheduling fields
    is_scheduled = models.BooleanField(default=False)
    scheduled_for = models.DateTimeField(null=True, blank=True, help_text="When this order should be processed")
    scheduled_message = models.TextField(blank=True, null=True, help_text="Customer message for scheduled order")
    pharmacy_response = models.TextField(blank=True, null=True, help_text="Pharmacy response to scheduled order")
    
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
    
    def can_be_scheduled(self):
        """Check if this order can be scheduled (pharmacy is closed)"""
        return not self.pharmacy.is_open_now()
    
    def get_next_opening_time(self):
        """Get the next opening time for the pharmacy"""
        return self.pharmacy.get_next_opening_time()
    
    def schedule_for_opening(self, message=""):
        """Schedule this order for when the pharmacy opens"""
        if self.can_be_scheduled():
            self.is_scheduled = True
            self.status = 'scheduled'
            self.scheduled_for = self.get_next_opening_time()
            self.scheduled_message = message
            self.save()
            return True
        return False

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
    """Model for tracking payments (online and cash-on-delivery)"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('cash_pending', 'Cash Payment Pending'),
        ('cash_paid', 'Cash Payment Received'),
    )
    
    PAYMENT_TYPE_CHOICES = (
        ('online', 'Online Payment'),
        ('cash_on_delivery', 'Cash on Delivery'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    tx_ref = models.CharField(max_length=100, unique=True)
    chapa_tx_ref = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ETB')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='online')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Customer information for payment
    customer_email = models.EmailField()
    customer_first_name = models.CharField(max_length=50)
    customer_last_name = models.CharField(max_length=50)
    customer_phone = models.CharField(max_length=20)
    
    # Online payment data
    chapa_response = models.JSONField(blank=True, null=True)
    checkout_url = models.URLField(blank=True, null=True)
    
    # Cash on delivery fields
    qr_code_data = models.TextField(blank=True, null=True)
    cash_received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cash_payments_received')
    cash_received_at = models.DateTimeField(blank=True, null=True)
    cash_confirmation_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.tx_ref} - {self.amount} {self.currency} ({self.status})"
    
    def generate_qr_code_data(self):
        """Generate QR code data for cash payment"""
        import json
        qr_data = {
            'order_id': self.order.id,
            'amount': str(self.amount),
            'currency': self.currency,
            'payment_type': self.payment_type,
            'customer_name': f"{self.customer_first_name} {self.customer_last_name}",
            'customer_phone': self.customer_phone,
            'pharmacy_name': self.order.pharmacy.name,
            'tx_ref': self.tx_ref,
            'delivery_tracking': True
        }
        
        self.qr_code_data = json.dumps(qr_data)
        self.save()
        return qr_data

class Cart(models.Model):
    """Shopping cart model"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.customer.name}"

    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.cartitem_set.all())

    def get_total_amount(self):
        """Get total amount of all items in cart"""
        return sum(item.get_total_price() for item in self.cartitem_set.all())

    def clear(self):
        """Clear all items from cart"""
        self.cartitem_set.all().delete()

class CartItem(models.Model):
    """Individual item in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    medicine = models.ForeignKey('pharmacy.Medicine', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    prescription_image = models.ImageField(upload_to='cart_prescriptions/', blank=True, null=True)
    validation_data = models.JSONField(blank=True, null=True)
    pharmacy_review_required = models.BooleanField(default=False, help_text="True if OCR confidence is below 100%")
    pharmacy_review_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved by Pharmacy'),
        ('rejected', 'Rejected by Pharmacy'),
        ('not_required', 'Review Not Required')
    ], default='not_required')
    pharmacy_review_notes = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_prescriptions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'medicine']

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"

    def get_total_price(self):
        """Get total price for this cart item"""
        return self.quantity * self.medicine.price
    
    def requires_pharmacy_review(self):
        """Check if this item requires pharmacy review based on OCR confidence"""
        if not self.validation_data:
            return False
        
        confidence = self.validation_data.get('confidence', 0)
        # Require pharmacy review if confidence is less than 100% (including 0% when medicine not found)
        return confidence < 100
    
    def get_ocr_confidence(self):
        """Get OCR confidence percentage"""
        if not self.validation_data:
            return 0
        return self.validation_data.get('confidence', 0)
    
    def get_ocr_best_match(self):
        """Get best OCR match from validation data"""
        if not self.validation_data:
            return None
        return self.validation_data.get('best_match', None)

class Receipt(models.Model):
    """Model for storing receipt information"""
    receipt_number = models.CharField(max_length=20, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey('pharmacy.Pharmacy', on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_printed = models.BooleanField(default=False)
    print_count = models.IntegerField(default=0)
    last_viewed_by_customer = models.DateTimeField(null=True, blank=True)
    last_viewed_by_pharmacy = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"Receipt {self.receipt_number}"

    def mark_viewed_by_customer(self):
        """Mark receipt as viewed by customer"""
        self.last_viewed_by_customer = timezone.now()
        self.save()

    def mark_viewed_by_pharmacy(self):
        """Mark receipt as viewed by pharmacy"""
        self.last_viewed_by_pharmacy = timezone.now()
        self.save()

    def mark_printed(self):
        """Mark receipt as printed"""
        self.is_printed = True
        self.print_count += 1
        self.save()

class IncidentReport(models.Model):
    """Model for storing incident reports"""
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    pharmacy = models.ForeignKey('pharmacy.Pharmacy', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Incident: {self.title}"

class AdminNotification(models.Model):
    """Model for storing admin notifications"""
    NOTIFICATION_TYPES = (
        ('pharmacy_registration', 'Pharmacy Registration'),
        ('incident_report', 'Incident Report'),
        ('payment_issue', 'Payment Issue'),
        ('system_alert', 'System Alert'),
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.notification_type}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()