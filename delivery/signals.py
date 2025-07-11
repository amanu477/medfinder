from django.db.models.signals import post_save
from django.dispatch import receiver
from customer.models import Order
from .models import Delivery
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def create_delivery_on_order_completion(sender, instance, created, **kwargs):
    """
    Automatically create delivery record when order status is changed to 'completed'
    """
    if not created and instance.status == 'completed':
        # Check if delivery already exists
        if not hasattr(instance, 'delivery'):
            try:
                # Use customer's current location or default to Addis Ababa
                customer_lat = instance.customer.latitude or 9.0320
                customer_lon = instance.customer.longitude or 38.7615
                
                # Create delivery record with customer's current location
                delivery = Delivery.objects.create(
                    order=instance,
                    customer_location_lat=customer_lat,
                    customer_location_lon=customer_lon,
                    customer_address=f"Customer Address: Lat {customer_lat:.4f}, Lon {customer_lon:.4f}",
                    customer_phone=instance.customer.phone,
                    status='pending'
                )
                
                # Update order status to ready for delivery
                instance.status = 'ready_for_delivery'
                instance.save()
                
                logger.info(f"Delivery created for order {instance.id}: {delivery.tracking_number}")
                
            except Exception as e:
                logger.error(f"Error creating delivery for order {instance.id}: {str(e)}")
        else:
            logger.info(f"Delivery already exists for order {instance.id}")