#!/usr/bin/env python
"""
Create Order from Cart Items with Prescription Reviews
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from customer.models import Customer, Cart, CartItem, Order, OrderItem
from pharmacy.models import Pharmacy

def create_order_from_cart_with_prescriptions():
    """Create order that directly corresponds to cart items with prescription requirements"""
    
    print("Creating Order from Cart Items with Prescription Reviews")
    print("=" * 60)
    
    # Get test data
    customer = Customer.objects.get(user__username='testcustomer')
    pharmacy = Pharmacy.objects.get(user__username='testpharmacy')
    
    # Get cart items that require prescription review
    cart_items_with_prescriptions = CartItem.objects.filter(
        cart__customer=customer,
        medicine__pharmacy=pharmacy,
        pharmacy_review_required=True
    )
    
    if not cart_items_with_prescriptions.exists():
        print("❌ No cart items with prescription requirements found")
        return
    
    print(f"Found {cart_items_with_prescriptions.count()} cart items with prescription requirements:")
    for item in cart_items_with_prescriptions:
        print(f"  - {item.medicine.name} (OCR: {item.get_ocr_confidence()}%, Status: {item.pharmacy_review_status})")
    
    # Calculate total
    total_amount = sum(item.quantity * item.medicine.price for item in cart_items_with_prescriptions)
    
    # Create order
    order = Order.objects.create(
        customer=customer,
        pharmacy=pharmacy,
        total_amount=total_amount,
        status='pending',
        notes='Order created with prescription review requirements'
    )
    
    # Create order items from cart items
    for cart_item in cart_items_with_prescriptions:
        OrderItem.objects.create(
            order=order,
            medicine=cart_item.medicine,
            quantity=cart_item.quantity,
            price=cart_item.medicine.price
        )
    
    print(f"\n✅ Created Order #{order.id}")
    print(f"   Total Amount: {order.total_amount} ETB")
    print(f"   Status: {order.status}")
    print(f"   Items: {order.orderitem_set.count()}")
    
    # Test approval check
    unresolved_reviews = CartItem.objects.filter(
        cart__customer=order.customer,
        medicine__pharmacy=pharmacy,
        pharmacy_review_required=True
    ).exclude(pharmacy_review_status='approved')
    
    print(f"\n🔍 Approval Check:")
    print(f"   Unresolved prescription reviews: {unresolved_reviews.count()}")
    print(f"   Can approve order: {'NO' if unresolved_reviews.exists() else 'YES'}")
    
    if unresolved_reviews.exists():
        print("   📋 Required actions:")
        for item in unresolved_reviews:
            print(f"     - Review {item.medicine.name} (Status: {item.pharmacy_review_status})")
    
    return order

if __name__ == '__main__':
    create_order_from_cart_with_prescriptions()