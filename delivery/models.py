from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from customer.models import Order, Customer
from pharmacy.models import Pharmacy
import json


class DeliveryPerson(models.Model):
    """Delivery personnel model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='delivery_staff')
    employee_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    national_id = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=50, choices=[
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('car', 'Car'),
        ('on_foot', 'On Foot'),
    ], default='motorcycle')
    vehicle_plate = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    current_location_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    current_location_lon = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    total_deliveries = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Delivery Person'
        verbose_name_plural = 'Delivery Personnel'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.pharmacy.name}"

    def update_location(self, lat, lon):
        """Update delivery person's current location"""
        self.current_location_lat = lat
        self.current_location_lon = lon
        self.last_location_update = timezone.now()
        self.save()
    
    def has_active_deliveries(self):
        """Check if delivery person has any active deliveries"""
        active_statuses = ['assigned', 'picked_up', 'in_transit']
        return self.delivery_set.filter(status__in=active_statuses).exists()
    
    def update_availability_status(self):
        """Update availability status based on active deliveries"""
        if self.has_active_deliveries():
            self.is_available = False
        else:
            self.is_available = True
        self.save()
    
    def get_active_deliveries_count(self):
        """Get count of active deliveries"""
        active_statuses = ['assigned', 'picked_up', 'in_transit']
        return self.delivery_set.filter(status__in=active_statuses).count()
    
    def get_active_deliveries(self):
        """Get all active deliveries"""
        active_statuses = ['assigned', 'picked_up', 'in_transit']
        return self.delivery_set.filter(status__in=active_statuses)


class Delivery(models.Model):
    """Delivery tracking model"""
    STATUS_CHOICES = [
        ('pending', 'Pending Assignment'),
        ('assigned', 'Assigned to Delivery Person'),
        ('picked_up', 'Picked up from Pharmacy'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Delivery Failed'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    delivery_person = models.ForeignKey(DeliveryPerson, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Customer location (destination)
    customer_location_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    customer_location_lon = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    customer_address = models.TextField()
    customer_phone = models.CharField(max_length=15)
    
    # Delivery details
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    
    # Distance and cost
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Notes and feedback
    pharmacy_notes = models.TextField(blank=True)
    delivery_notes = models.TextField(blank=True)
    customer_feedback = models.TextField(blank=True)
    customer_rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    
    # Tracking
    tracking_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
        ordering = ['-created_at']

    def __str__(self):
        return f"Delivery #{self.tracking_number} - {self.order.customer.name}"

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = f"DEL{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # Update delivery person availability when delivery status changes
        is_new = self.pk is None
        old_status = None
        
        if not is_new:
            old_delivery = Delivery.objects.get(pk=self.pk)
            old_status = old_delivery.status
        
        super().save(*args, **kwargs)
        
        # Update delivery person availability if status changed
        if self.delivery_person and (is_new or old_status != self.status):
            self.delivery_person.update_availability_status()
    
    def assign_delivery_person(self, delivery_person):
        """Assign delivery person and update their availability"""
        self.delivery_person = delivery_person
        self.status = 'assigned'
        self.save()
        
        # Update delivery person availability
        delivery_person.update_availability_status()
        
        # Create tracking entry
        DeliveryTracking.objects.create(
            delivery=self,
            status='assigned',
            location_lat=delivery_person.current_location_lat,
            location_lon=delivery_person.current_location_lon,
            notes=f'Delivery assigned to {delivery_person.user.get_full_name()}'
        )

    def get_status_display_with_icon(self):
        """Get status with appropriate icon"""
        icons = {
            'pending': '🕐',
            'assigned': '👤',
            'picked_up': '📦',
            'in_transit': '🚚',
            'delivered': '✅',
            'failed': '❌',
            'cancelled': '🚫',
        }
        return f"{icons.get(self.status, '📋')} {self.get_status_display()}"

    def calculate_delivery_fee(self):
        """Calculate delivery fee based on distance"""
        if self.distance_km:
            # Base fee + per km charge
            base_fee = 50  # ETB
            per_km_fee = 10  # ETB per km
            self.delivery_fee = base_fee + (self.distance_km * per_km_fee)
            return self.delivery_fee
        return 0

    def assign_delivery_person(self, delivery_person):
        """Assign delivery to a delivery person"""
        self.delivery_person = delivery_person
        self.status = 'assigned'
        self.save()
        
        # Create notification
        DeliveryNotification.objects.create(
            delivery=self,
            recipient_type='delivery_person',
            recipient_id=delivery_person.user.id,
            message=f"New delivery assigned: Order #{self.order.id}",
            notification_type='assignment'
        )
    
    def needs_cash_payment_confirmation(self):
        """Check if delivery needs cash payment confirmation"""
        try:
            payment = self.order.payment
            return (payment.is_cash_payment() and 
                   payment.needs_cash_confirmation())
        except:
            return False
    
    def confirm_cash_payment(self, delivery_person):
        """Confirm cash payment received"""
        try:
            payment = self.order.payment
            if payment.confirm_cash_payment(delivery_person.user):
                return True
        except:
            pass
        return False


class DeliveryTracking(models.Model):
    """Real-time delivery tracking"""
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='tracking_points')
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Delivery Tracking Point'
        verbose_name_plural = 'Delivery Tracking Points'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Tracking #{self.delivery.tracking_number} - {self.timestamp}"


class DeliveryNotification(models.Model):
    """Notifications for delivery updates"""
    RECIPIENT_TYPES = [
        ('customer', 'Customer'),
        ('delivery_person', 'Delivery Person'),
        ('pharmacy', 'Pharmacy'),
    ]
    
    NOTIFICATION_TYPES = [
        ('assignment', 'Assignment'),
        ('pickup', 'Pickup'),
        ('status_update', 'Status Update'),
        ('delivery_complete', 'Delivery Complete'),
        ('delivery_failed', 'Delivery Failed'),
    ]

    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='notifications')
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_TYPES)
    recipient_id = models.IntegerField()  # User ID
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Delivery Notification'
        verbose_name_plural = 'Delivery Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient_type} - {self.delivery.tracking_number}"


class DeliveryZone(models.Model):
    """Delivery zones for pharmacy coverage"""
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='delivery_zones')
    name = models.CharField(max_length=100)
    polygon_coordinates = models.JSONField(help_text="Array of [lat, lon] coordinates defining the delivery zone")
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2)
    estimated_delivery_time = models.IntegerField(help_text="Estimated delivery time in minutes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Delivery Zone'
        verbose_name_plural = 'Delivery Zones'

    def __str__(self):
        return f"{self.name} - {self.pharmacy.name}"

    def contains_point(self, lat, lon):
        """Check if a point is within this delivery zone"""
        # Simple point-in-polygon check (you can implement more sophisticated algorithms)
        # For now, we'll use a basic bounding box check
        coordinates = self.polygon_coordinates
        if not coordinates:
            return False
            
        # Get bounding box
        lats = [coord[0] for coord in coordinates]
        lons = [coord[1] for coord in coordinates]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon