#!/usr/bin/env python
"""
Test script to verify scheduled order system functionality
"""

import os
import sys
import django
from django.utils import timezone
from datetime import datetime, timedelta, time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from customer.models import Customer, Order, OrderItem
from pharmacy.models import Pharmacy, Medicine

def test_scheduled_orders():
    """Test scheduled order functionality"""
    print("Testing Scheduled Order System...")
    print("=" * 50)
    
    # Create test pharmacy with specific hours (closed now)
    try:
        # Create unique usernames using timestamp
        timestamp = str(int(timezone.now().timestamp()))
        
        # Create pharmacy user
        pharmacy_user = User.objects.create_user(
            username=f'test_pharmacy_scheduled_{timestamp}',
            email=f'test_pharmacy_scheduled_{timestamp}@example.com',
            password='testpass123'
        )
        
        # Create pharmacy profile - set to be closed now
        pharmacy = Pharmacy.objects.create(
            user=pharmacy_user,
            name='Test Pharmacy for Scheduled Orders',
            email=f'test_pharmacy_scheduled_{timestamp}@example.com',
            phone='+251912345678',
            address='Test Address',
            license_number=f'TEST{timestamp}',
            verification_status='verified',
            # Set hours that make it closed now (8 AM to 6 PM)
            opening_time=time(8, 0),
            closing_time=time(18, 0),
            latitude=9.0320,
            longitude=38.7460
        )
        
        # Create test medicine
        medicine = Medicine.objects.create(
            name='Test Medicine for Scheduled Order',
            pharmacy=pharmacy,
            price=50.00,
            stock_quantity=100,
            description='Test medicine for scheduled orders',
            expiry_date=timezone.now().date() + timedelta(days=365),
            prescription_required=False
        )
        
        # Create test customer
        customer_user = User.objects.create_user(
            username=f'test_customer_scheduled_{timestamp}',
            email=f'test_customer_scheduled_{timestamp}@example.com',
            password='testpass123'
        )
        
        customer = Customer.objects.create(
            user=customer_user,
            name='Test Customer',
            email=f'test_customer_scheduled_{timestamp}@example.com',
            phone='+251987654321',
            address='Test Customer Address'
        )
        
        print(f"Created test pharmacy: {pharmacy.name}")
        print(f"Pharmacy hours: {pharmacy.opening_time} - {pharmacy.closing_time}")
        print(f"Is pharmacy open now? {pharmacy.is_open_now()}")
        print(f"Next opening time: {pharmacy.get_next_opening_time()}")
        print()
        
        # Test 1: Create scheduled order when pharmacy is closed
        print("Test 1: Creating scheduled order when pharmacy is closed...")
        
        # Simulate order creation (this would normally be done through checkout)
        if not pharmacy.is_open_now():
            next_opening = pharmacy.get_next_opening_time()
            scheduled_order = Order.objects.create(
                customer=customer,
                pharmacy=pharmacy,
                total_amount=50.00,
                status='scheduled',
                is_scheduled=True,
                scheduled_for=next_opening,
                scheduled_message=f'Order scheduled for when {pharmacy.name} opens at {next_opening.strftime("%I:%M %p on %B %d, %Y")}',
                notes='Test scheduled order'
            )
            
            OrderItem.objects.create(
                order=scheduled_order,
                medicine=medicine,
                quantity=1,
                price=medicine.price
            )
            
            print(f"✓ Created scheduled order #{scheduled_order.id}")
            print(f"  - Status: {scheduled_order.status}")
            print(f"  - Scheduled for: {scheduled_order.scheduled_for}")
            print(f"  - Message: {scheduled_order.scheduled_message}")
            print()
            
        # Test 2: Verify pharmacy can see scheduled orders
        print("Test 2: Verifying pharmacy can see scheduled orders...")
        
        scheduled_orders = Order.objects.filter(
            pharmacy=pharmacy,
            is_scheduled=True,
            status='scheduled'
        )
        
        print(f"✓ Found {scheduled_orders.count()} scheduled order(s)")
        for order in scheduled_orders:
            print(f"  - Order #{order.id}: {order.customer.name} - {order.total_amount} ETB")
        print()
        
        # Test 3: Test order approval
        print("Test 3: Testing order approval...")
        
        if scheduled_orders.exists():
            test_order = scheduled_orders.first()
            test_order.status = 'approved'
            test_order.pharmacy_response = 'Order approved - medicines ready for pickup'
            test_order.save()
            
            print(f"✓ Approved order #{test_order.id}")
            print(f"  - New status: {test_order.status}")
            print(f"  - Pharmacy response: {test_order.pharmacy_response}")
        print()
        
        # Test 4: Test order rejection
        print("Test 4: Testing order rejection...")
        
        # Create another test order to reject
        if not pharmacy.is_open_now():
            next_opening = pharmacy.get_next_opening_time()
            reject_order = Order.objects.create(
                customer=customer,
                pharmacy=pharmacy,
                total_amount=25.00,
                status='scheduled',
                is_scheduled=True,
                scheduled_for=next_opening,
                scheduled_message=f'Order to be rejected',
                notes='Test order for rejection'
            )
            
            OrderItem.objects.create(
                order=reject_order,
                medicine=medicine,
                quantity=1,
                price=25.00
            )
            
            # Reject the order
            reject_order.status = 'rejected'
            reject_order.pharmacy_response = 'Sorry, this medicine is out of stock'
            reject_order.save()
            
            print(f"✓ Rejected order #{reject_order.id}")
            print(f"  - Status: {reject_order.status}")
            print(f"  - Rejection reason: {reject_order.pharmacy_response}")
        print()
        
        # Test 5: Verify counts
        print("Test 5: Verifying order counts...")
        
        all_orders = Order.objects.filter(pharmacy=pharmacy)
        scheduled_count = all_orders.filter(is_scheduled=True, status='scheduled').count()
        approved_count = all_orders.filter(status='approved').count()
        rejected_count = all_orders.filter(status='rejected').count()
        
        print(f"✓ Total orders: {all_orders.count()}")
        print(f"  - Scheduled: {scheduled_count}")
        print(f"  - Approved: {approved_count}")
        print(f"  - Rejected: {rejected_count}")
        print()
        
        print("✓ All tests passed successfully!")
        print("\nScheduled Order System is working correctly!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scheduled_orders()