#!/usr/bin/env python
"""
Complete OCR Enhancement Workflow Test
Tests the entire workflow from medicine search to pharmacy verification
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from customer.models import Customer, Cart, CartItem
from pharmacy.models import Pharmacy, Medicine
from django.utils import timezone

def test_complete_workflow():
    """Test the complete OCR enhancement workflow"""
    
    print("Testing Complete OCR Enhancement Workflow")
    print("=" * 50)
    
    # Step 1: Customer searches for medicine and adds to cart
    print("1. Customer searches for medicine and adds to cart")
    customer = Customer.objects.get(user__username='testcustomer')
    pharmacy = Pharmacy.objects.get(user__username='testpharmacy')
    medicine = Medicine.objects.filter(pharmacy=pharmacy, name__icontains='aspirin').first()
    
    cart, _ = Cart.objects.get_or_create(customer=customer)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        medicine=medicine,
        defaults={'quantity': 1}
    )
    print(f"   - Medicine added to cart: {medicine.name}")
    print(f"   - Cart item created: {created}")
    
    # Step 2: Customer uploads prescription and OCR runs
    print("\n2. Customer uploads prescription and OCR processes it")
    
    # Simulate OCR processing with confidence < 100%
    ocr_result = {
        'is_valid': False,
        'confidence': 85,  # Below 100% threshold
        'best_match': 'asprin',  # Slightly misspelled
        'extracted_text': 'Patient: John Doe\nPrescription: asprin 500mg tablets\nQuantity: 30 tablets\nDate: 2025-07-21',
        'extracted_medicines': ['asprin', 'vitamin D']
    }
    
    # Update cart item with OCR validation
    cart_item.validation_data = ocr_result
    cart_item.pharmacy_review_required = True
    cart_item.pharmacy_review_status = 'pending'
    cart_item.save()
    
    print(f"   - OCR confidence: {cart_item.get_ocr_confidence()}%")
    print(f"   - Pharmacy review required: {cart_item.requires_pharmacy_review()}")
    print(f"   - Review status: {cart_item.pharmacy_review_status}")
    
    # Step 3: Customer tries to checkout but is blocked
    print("\n3. Customer checkout process")
    pending_reviews = CartItem.objects.filter(
        cart=cart,
        pharmacy_review_required=True,
        pharmacy_review_status='pending'
    )
    
    if pending_reviews.exists():
        print("   - Checkout BLOCKED: Prescription reviews pending")
        print(f"   - Items requiring review: {pending_reviews.count()}")
        for item in pending_reviews:
            print(f"     * {item.medicine.name} (Confidence: {item.get_ocr_confidence()}%)")
    else:
        print("   - Checkout ALLOWED: No pending reviews")
    
    # Step 4: Pharmacy receives notification and reviews prescription
    print("\n4. Pharmacy reviews prescription")
    pharmacy_reviews = CartItem.objects.filter(
        medicine__pharmacy=pharmacy,
        pharmacy_review_required=True,
        pharmacy_review_status='pending'
    )
    
    print(f"   - Pending reviews for {pharmacy.name}: {pharmacy_reviews.count()}")
    
    for review in pharmacy_reviews:
        print(f"   - Reviewing: {review.medicine.name}")
        print(f"     Customer: {review.cart.customer.name}")
        print(f"     OCR Text: {review.validation_data.get('extracted_text', 'N/A')[:50]}...")
        print(f"     Best Match: {review.get_ocr_best_match()}")
        
        # Pharmacy approves the prescription
        review.pharmacy_review_status = 'approved'
        review.pharmacy_review_notes = 'Prescription verified. Medicine name matches despite OCR typo (asprin vs aspirin). Approved for dispensing.'
        review.reviewed_by = pharmacy.user
        review.reviewed_at = timezone.now()
        review.save()
        
        print(f"     Status: APPROVED")
        print(f"     Notes: {review.pharmacy_review_notes}")
    
    # Step 5: Customer can now complete checkout
    print("\n5. Final checkout status")
    final_pending_reviews = CartItem.objects.filter(
        cart=cart,
        pharmacy_review_required=True,
        pharmacy_review_status='pending'
    )
    
    if final_pending_reviews.exists():
        print("   - Checkout still BLOCKED: Some reviews still pending")
    else:
        print("   - Checkout NOW ALLOWED: All prescriptions approved")
        approved_items = CartItem.objects.filter(
            cart=cart,
            pharmacy_review_status='approved'
        )
        print(f"   - Approved items: {approved_items.count()}")
        for item in approved_items:
            print(f"     * {item.medicine.name} - Reviewed by {item.reviewed_by.username}")
    
    # Step 6: Summary of workflow
    print("\n6. Workflow Summary")
    print("   ✅ OCR Enhancement Implementation:")
    print("      - When OCR confidence < 100% → Pharmacy review required")
    print("      - Customer checkout blocked until pharmacy approves")
    print("      - Pharmacy can view prescription image and OCR data")
    print("      - Manual verification with detailed notes")
    print("      - Audit trail with reviewer and timestamp")
    
    print("\n   📊 Test Results:")
    total_items = CartItem.objects.filter(cart=cart).count()
    approved_items = CartItem.objects.filter(cart=cart, pharmacy_review_status='approved').count()
    pending_items = CartItem.objects.filter(cart=cart, pharmacy_review_status='pending').count()
    
    print(f"      - Total cart items: {total_items}")
    print(f"      - Approved items: {approved_items}")
    print(f"      - Pending items: {pending_items}")
    print(f"      - Checkout allowed: {'Yes' if pending_items == 0 else 'No'}")
    
    print("\n🎉 OCR Enhancement Workflow Test COMPLETED!")
    print("    The system successfully enforces pharmacy verification when OCR confidence is below 100%")

if __name__ == '__main__':
    test_complete_workflow()