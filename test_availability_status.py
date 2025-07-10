#!/usr/bin/env python
"""
Test script to verify automatic delivery person availability status management
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from delivery.models import DeliveryPerson, Delivery
from customer.models import Order
from django.contrib.auth.models import User

def test_availability_status():
    """Test automatic availability status management"""
    
    print("Testing Delivery Person Availability Status Management")
    print("=" * 50)
    
    # Get delivery person
    try:
        delivery_person = DeliveryPerson.objects.get(user__username='jj')
        print(f"Testing with delivery person: {delivery_person.user.get_full_name()}")
        print(f"Phone: {delivery_person.phone}")
        print(f"Vehicle: {delivery_person.vehicle_type}")
        print()
        
        # Check current status
        print("Current Status:")
        print(f"- Is Available: {delivery_person.is_available}")
        print(f"- Active Deliveries: {delivery_person.get_active_deliveries_count()}")
        print(f"- Has Active Deliveries: {delivery_person.has_active_deliveries()}")
        print()
        
        # List active deliveries
        active_deliveries = delivery_person.get_active_deliveries()
        print(f"Active Deliveries ({active_deliveries.count()}):")
        for delivery in active_deliveries:
            print(f"  - Delivery #{delivery.tracking_number}")
            print(f"    Order: #{delivery.order.id}")
            print(f"    Customer: {delivery.order.customer.name}")
            print(f"    Status: {delivery.get_status_display()}")
            print(f"    Created: {delivery.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
        
        # Test availability update
        print("Testing availability update...")
        delivery_person.update_availability_status()
        delivery_person.refresh_from_db()
        print(f"Updated availability: {delivery_person.is_available}")
        print()
        
        # Show rules
        print("Availability Rules:")
        print("- Available: No active deliveries (assigned, picked_up, in_transit)")
        print("- Not Available: Has active deliveries")
        print("- Status updates automatically when delivery status changes")
        print("- Status updates when deliveries are assigned or completed")
        print()
        
    except DeliveryPerson.DoesNotExist:
        print("Error: Delivery person 'jj' not found")
        return
    except Exception as e:
        print(f"Error: {e}")
        return

def test_status_change_simulation():
    """Simulate status changes to test availability updates"""
    
    print("\nTesting Status Change Simulation")
    print("=" * 50)
    
    try:
        delivery_person = DeliveryPerson.objects.get(user__username='jj')
        
        # Get a delivery to test with
        deliveries = Delivery.objects.filter(delivery_person=delivery_person)
        
        if not deliveries.exists():
            print("No deliveries found for testing")
            return
            
        test_delivery = deliveries.first()
        
        print(f"Testing with delivery: {test_delivery.tracking_number}")
        print(f"Current delivery status: {test_delivery.get_status_display()}")
        print(f"Current availability: {delivery_person.is_available}")
        print()
        
        # Save original status
        original_status = test_delivery.status
        
        # Test different status changes
        test_statuses = ['assigned', 'picked_up', 'in_transit', 'delivered']
        
        for status in test_statuses:
            print(f"Setting delivery status to: {status}")
            test_delivery.status = status
            test_delivery.save()
            
            # Refresh delivery person
            delivery_person.refresh_from_db()
            
            print(f"  - Delivery person availability: {delivery_person.is_available}")
            print(f"  - Active deliveries count: {delivery_person.get_active_deliveries_count()}")
            print()
        
        # Restore original status
        test_delivery.status = original_status
        test_delivery.save()
        
        print(f"Restored original status: {test_delivery.get_status_display()}")
        
    except Exception as e:
        print(f"Error in simulation: {e}")

if __name__ == "__main__":
    test_availability_status()
    test_status_change_simulation()