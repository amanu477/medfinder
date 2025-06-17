#!/usr/bin/env python
"""
Script to create a test order for payment integration demonstration
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from customer.models import Customer, Order, OrderItem
from pharmacy.models import Pharmacy, Medicine
from datetime import date, timedelta

def create_test_order():
    """Create a test order for payment integration testing"""
    
    # Get existing customer and pharmacy
    customer = Customer.objects.first()
    pharmacy = Pharmacy.objects.first()
    
    if not customer or not pharmacy:
        print("Error: No customer or pharmacy found. Please ensure test users exist.")
        return
    
    print(f"Customer: {customer.name} ({customer.email})")
    print(f"Pharmacy: {pharmacy.name}")
    
    # Create test medicines with correct fields
    medicine1, created = Medicine.objects.get_or_create(
        name='Paracetamol 500mg',
        pharmacy=pharmacy,
        defaults={
            'description': 'Pain relief and fever reducer',
            'price': 75.00,
            'stock_quantity': 100,
            'prescription_required': False,
            'expiry_date': date.today() + timedelta(days=365),
            'is_available': True
        }
    )
    
    medicine2, created = Medicine.objects.get_or_create(
        name='Amoxicillin 250mg',
        pharmacy=pharmacy,
        defaults={
            'description': 'Antibiotic for bacterial infections',
            'price': 125.00,
            'stock_quantity': 50,
            'prescription_required': True,
            'expiry_date': date.today() + timedelta(days=300),
            'is_available': True
        }
    )
    
    print(f"Created medicines: {medicine1.name} (${medicine1.price}), {medicine2.name} (${medicine2.price})")
    
    # Create a test order
    order = Order.objects.create(
        customer=customer,
        pharmacy=pharmacy,
        status='approved',  # Create as approved so we can test payment
        total_amount=400.00,
        notes='Test order for payment integration - 2x Paracetamol + 2x Amoxicillin'
    )
    
    # Add order items
    OrderItem.objects.create(
        order=order,
        medicine=medicine1,
        quantity=2,
        price=medicine1.price
    )
    
    OrderItem.objects.create(
        order=order,
        medicine=medicine2,
        quantity=2,
        price=medicine2.price
    )
    
    print(f"✓ Created test order #{order.id} with status: {order.status}")
    print(f"✓ Order total: {order.total_amount} ETB")
    print(f"✓ Order items: {order.get_total_items()}")
    print(f"✓ Test order detail URL: /order/{order.id}/")
    print(f"✓ Payment initiation URL: /order/{order.id}/payment/")
    
    return order

if __name__ == "__main__":
    create_test_order()