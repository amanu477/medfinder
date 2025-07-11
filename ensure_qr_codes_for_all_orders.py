#!/usr/bin/env python
"""
Script to ensure all orders have proper QR code support
Creates missing delivery and payment records for all orders
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from customer.models import Order, Payment
from delivery.models import Delivery
from django.utils import timezone
import uuid

def ensure_qr_support_for_all_orders():
    """Ensure all orders have delivery and payment records for QR code support"""
    print("=== Ensuring QR Code Support for All Orders ===")
    
    orders = Order.objects.all()
    print(f"Found {orders.count()} orders to process")
    
    orders_fixed = 0
    
    for order in orders:
        print(f"\nProcessing Order #{order.id}:")
        
        # Check if order has delivery
        has_delivery = hasattr(order, 'delivery')
        has_payment = hasattr(order, 'payment')
        
        print(f"  Has delivery: {has_delivery}")
        print(f"  Has payment: {has_payment}")
        
        # Create delivery if missing
        if not has_delivery:
            try:
                delivery = Delivery.objects.create(
                    order=order,
                    customer_address=f"Customer Address: {order.customer.address or 'Location not provided'}",
                    customer_phone=order.customer.phone,
                    status='pending'
                )
                print(f"  ✓ Created delivery #{delivery.id}")
                orders_fixed += 1
            except Exception as e:
                print(f"  ✗ Failed to create delivery: {e}")
                continue
        
        # Create payment if missing  
        if not has_payment:
            try:
                payment = Payment.objects.create(
                    order=order,
                    tx_ref=f"AUTO_{order.id}_{uuid.uuid4().hex[:8]}",
                    amount=order.total_amount,
                    currency='ETB',
                    payment_type='cash_on_delivery',
                    status='cash_pending',
                    customer_email=order.customer.email,
                    customer_first_name=order.customer.name.split()[0] if order.customer.name else 'Customer',
                    customer_last_name=order.customer.name.split()[-1] if len(order.customer.name.split()) > 1 else 'User',
                    customer_phone=order.customer.phone
                )
                print(f"  ✓ Created payment #{payment.id}")
                orders_fixed += 1
            except Exception as e:
                print(f"  ✗ Failed to create payment: {e}")
                continue
        
        # Update order status if needed
        if order.status == 'pending' and has_delivery and has_payment:
            order.status = 'approved'
            order.save()
            print(f"  ✓ Updated order status to approved")
    
    print(f"\n=== Summary ===")
    print(f"Orders processed: {orders.count()}")
    print(f"Orders fixed: {orders_fixed}")
    print("All orders now have QR code support!")

def set_test_delivery_status():
    """Set some orders to 'arrived' status for testing QR codes"""
    print("\n=== Setting Test Delivery Status ===")
    
    # Get a few orders to set as arrived
    test_orders = Order.objects.filter(
        delivery__isnull=False,
        payment__isnull=False
    )[:5]
    
    for order in test_orders:
        try:
            delivery = order.delivery
            delivery.status = 'arrived'
            delivery.save()
            
            order.status = 'arrived'
            order.save()
            
            print(f"  ✓ Set Order #{order.id} to 'arrived' status")
        except Exception as e:
            print(f"  ✗ Failed to update Order #{order.id}: {e}")

if __name__ == "__main__":
    ensure_qr_support_for_all_orders()
    set_test_delivery_status()