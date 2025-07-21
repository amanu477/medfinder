#!/usr/bin/env python
"""
Test Mandatory Prescription Verification Before Order Approval
Verifies that orders cannot be approved when OCR confidence < 100% without prescription verification
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from customer.models import Customer, Cart, CartItem, Order, OrderItem
from pharmacy.models import Pharmacy, Medicine
from django.test import Client
from django.urls import reverse
from django.contrib.messages import get_messages

def test_mandatory_prescription_verification():
    """Test that order approval requires prescription verification when OCR < 100%"""
    
    print("Testing Mandatory Prescription Verification Before Order Approval")
    print("=" * 65)
    
    try:
        # Get test data
        customer = Customer.objects.get(user__username='testcustomer')
        pharmacy = Pharmacy.objects.get(user__username='testpharmacy')
        pharmacy_user = pharmacy.user
        
        # Create test order
        order = Order.objects.create(
            customer=customer,
            pharmacy=pharmacy,
            total_amount=50.00,
            status='pending'
        )
        
        # Get medicine with 0% OCR confidence (not in prescription)
        cart_item = CartItem.objects.filter(
            cart__customer=customer,
            medicine__pharmacy=pharmacy,
            pharmacy_review_required=True,
            pharmacy_review_status='pending'
        ).first()
        
        if not cart_item:
            print("❌ No cart items with pending prescription reviews found")
            return False
        
        # Create order item from cart item
        order_item = OrderItem.objects.create(
            order=order,
            medicine=cart_item.medicine,
            quantity=cart_item.quantity,
            price=cart_item.medicine.price
        )
        
        print(f"Created test order #{order.id}")
        print(f"Medicine: {cart_item.medicine.name}")
        print(f"OCR Confidence: {cart_item.get_ocr_confidence()}%")
        print(f"Prescription Review Status: {cart_item.pharmacy_review_status}")
        
        # Test 1: Try to approve order without prescription verification
        print("\n1. Testing order approval WITHOUT prescription verification:")
        
        client = Client()
        client.force_login(pharmacy_user)
        
        # Try to approve the order
        response = client.post(
            reverse('update_order_status', args=[order.id]),
            {'status': 'approved'},
            follow=True
        )
        
        # Check if approval was blocked
        order.refresh_from_db()
        approval_blocked = order.status == 'pending'
        
        print(f"   Order status after approval attempt: {order.status}")
        print(f"   Approval blocked: {'✅ YES' if approval_blocked else '❌ NO'}")
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        has_error_message = any('prescription' in str(msg).lower() for msg in messages)
        print(f"   Error message shown: {'✅ YES' if has_error_message else '❌ NO'}")
        
        # Test 2: Approve prescription first, then approve order
        print("\n2. Testing order approval AFTER prescription verification:")
        
        # Approve the prescription
        cart_item.pharmacy_review_status = 'approved'
        cart_item.pharmacy_review_notes = 'Prescription verified manually. Medicine matches doctor recommendation.'
        cart_item.reviewed_by = pharmacy_user
        cart_item.save()
        
        print(f"   Prescription review status: {cart_item.pharmacy_review_status}")
        
        # Now try to approve the order again
        response = client.post(
            reverse('update_order_status', args=[order.id]),
            {'status': 'approved'},
            follow=True
        )
        
        # Check if approval was successful
        order.refresh_from_db()
        approval_successful = order.status == 'approved'
        
        print(f"   Order status after approval attempt: {order.status}")
        print(f"   Approval successful: {'✅ YES' if approval_successful else '❌ NO'}")
        
        # Test 3: Test with rejected prescription
        print("\n3. Testing order approval with REJECTED prescription:")
        
        # Create another cart item and reject its prescription
        cart_item.pharmacy_review_status = 'rejected'
        cart_item.pharmacy_review_notes = 'Medicine not found in prescription. Cannot dispense.'
        cart_item.save()
        
        # Reset order status
        order.status = 'pending'
        order.save()
        
        # Try to approve order with rejected prescription
        response = client.post(
            reverse('update_order_status', args=[order.id]),
            {'status': 'approved'},
            follow=True
        )
        
        order.refresh_from_db()
        approval_blocked_rejected = order.status == 'pending'
        
        print(f"   Prescription review status: {cart_item.pharmacy_review_status}")
        print(f"   Order status after approval attempt: {order.status}")
        print(f"   Approval blocked: {'✅ YES' if approval_blocked_rejected else '❌ NO'}")
        
        # Summary
        print("\n" + "=" * 65)
        print("MANDATORY PRESCRIPTION VERIFICATION TEST RESULTS:")
        print("=" * 65)
        
        test_results = [
            ("Order approval blocked without prescription verification", approval_blocked),
            ("Error message shown to pharmacy", has_error_message),
            ("Order approval allowed after prescription approval", approval_successful),
            ("Order approval blocked with rejected prescription", approval_blocked_rejected)
        ]
        
        passed_tests = sum(1 for _, passed in test_results if passed)
        total_tests = len(test_results)
        
        for test_name, passed in test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {test_name}")
        
        print(f"\nTest Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED!")
            print("   Orders cannot be approved without prescription verification when OCR < 100%")
            print("   Pharmacy must manually review prescription photos before approval")
            print("   System enforces medication safety through mandatory verification")
        else:
            print("⚠️ Some tests failed. Mandatory verification needs adjustment.")
        
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == '__main__':
    test_mandatory_prescription_verification()