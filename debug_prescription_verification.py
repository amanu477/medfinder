#!/usr/bin/env python
"""
Debug Prescription Verification Issue
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from customer.models import Customer, Cart, CartItem, Order, OrderItem
from pharmacy.models import Pharmacy

def debug_prescription_verification():
    """Debug why prescription verification isn't blocking order approval"""
    
    print("Debugging Prescription Verification Issue")
    print("=" * 50)
    
    # Get test data
    customer = Customer.objects.get(user__username='testcustomer')
    pharmacy = Pharmacy.objects.get(user__username='testpharmacy')
    
    print(f"Customer: {customer.name}")
    print(f"Pharmacy: {pharmacy.name}")
    
    # Check cart items
    cart_items = CartItem.objects.filter(
        cart__customer=customer,
        medicine__pharmacy=pharmacy
    )
    
    print(f"\nCart items for customer: {cart_items.count()}")
    for item in cart_items:
        print(f"  - {item.medicine.name}")
        print(f"    OCR Confidence: {item.get_ocr_confidence()}%")
        print(f"    Review Required: {item.pharmacy_review_required}")
        print(f"    Review Status: {item.pharmacy_review_status}")
        print(f"    Prescription Image: {'Yes' if item.prescription_image else 'No'}")
    
    # Check orders
    orders = Order.objects.filter(
        customer=customer,
        pharmacy=pharmacy
    ).order_by('-id')
    
    print(f"\nOrders for customer: {orders.count()}")
    for order in orders:
        print(f"\nOrder #{order.id}:")
        print(f"  Status: {order.status}")
        print(f"  Total: {order.total_amount} ETB")
        
        # Check order items
        order_items = OrderItem.objects.filter(order=order)
        print(f"  Order Items: {order_items.count()}")
        for item in order_items:
            print(f"    - {item.medicine.name} (Qty: {item.quantity})")
            
            # Find corresponding cart item
            corresponding_cart_item = CartItem.objects.filter(
                cart__customer=customer,
                medicine=item.medicine,
                pharmacy_review_required=True
            ).first()
            
            if corresponding_cart_item:
                print(f"      Corresponding cart item found:")
                print(f"      - OCR Confidence: {corresponding_cart_item.get_ocr_confidence()}%")
                print(f"      - Review Status: {corresponding_cart_item.pharmacy_review_status}")
                print(f"      - Review Required: {corresponding_cart_item.pharmacy_review_required}")
            else:
                print(f"      No corresponding cart item with review requirements")
    
    # Test the actual query used in views
    print(f"\n=== TESTING QUERY USED IN VIEWS ===")
    
    for order in orders[:2]:  # Test latest 2 orders
        print(f"\nTesting Order #{order.id}:")
        
        unresolved_prescription_reviews = CartItem.objects.filter(
            cart__customer=order.customer,
            medicine__pharmacy=pharmacy,
            pharmacy_review_required=True
        ).exclude(pharmacy_review_status='approved')
        
        print(f"  Unresolved prescription reviews: {unresolved_prescription_reviews.count()}")
        
        for item in unresolved_prescription_reviews:
            print(f"    - {item.medicine.name}")
            print(f"      Status: {item.pharmacy_review_status}")
            print(f"      OCR: {item.get_ocr_confidence()}%")
        
        can_approve = not unresolved_prescription_reviews.exists()
        print(f"  Can approve order: {'YES' if can_approve else 'NO'}")
        
        if not can_approve:
            print(f"  SHOULD BLOCK: Order approval should be blocked")
        else:
            print(f"  ISSUE: Order approval is allowed when it shouldn't be")

if __name__ == '__main__':
    debug_prescription_verification()