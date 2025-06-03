from django.db import models
from django.contrib.auth.models import User
from pharmacy.models import Pharmacy, Medicine

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

    def __str__(self):
        return self.name


class Order(models.Model):
    """Model for storing medicine orders"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
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
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.medicine.name} x{self.quantity}"

    def get_total_price(self):
        """Get total price for this item"""
        return self.quantity * self.price


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

    def __str__(self):
        return f"Prescription #{self.id} - {self.customer_name}"
