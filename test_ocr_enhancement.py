#!/usr/bin/env python
"""
Test script for OCR enhancement system
This script demonstrates the enhanced OCR validation requiring pharmacy review when confidence < 100%
"""

import os
import django
import json
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from customer.models import Customer, Cart, CartItem
from pharmacy.models import Pharmacy, Medicine
from customer.ocr_service import PrescriptionOCRService

def test_ocr_enhancement():
    """Test the OCR enhancement system with pharmacy review workflow"""
    
    print("🧪 Testing OCR Enhancement System")
    print("=" * 50)
    
    try:
        # Get or create test pharmacy
        pharmacy_user = User.objects.filter(username='testpharmacy').first()
        if not pharmacy_user:
            print("❌ Test pharmacy not found. Please create a test pharmacy first.")
            return
            
        pharmacy = pharmacy_user.pharmacy
        print(f"✅ Using test pharmacy: {pharmacy.name}")
        
        # Get or create test customer
        customer_user = User.objects.filter(username='testcustomer').first()
        if not customer_user:
            print("❌ Test customer not found. Please create a test customer first.")
            return
            
        customer = customer_user.customer
        print(f"✅ Using test customer: {customer.name}")
        
        # Get or create test medicine
        medicine = Medicine.objects.filter(pharmacy=pharmacy, name__icontains='aspirin').first()
        if not medicine:
            print("❌ No test medicine found. Please add some medicines to the pharmacy.")
            return
            
        print(f"✅ Using test medicine: {medicine.name}")
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(customer=customer)
        print(f"✅ Using customer cart (created: {created})")
        
        # Create cart item for testing
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            medicine=medicine,
            defaults={'quantity': 2}
        )
        print(f"✅ Cart item created (new: {created})")
        
        # Simulate OCR validation with different confidence levels
        test_cases = [
            {
                'confidence': 95,
                'best_match': 'asprin',
                'is_valid': True,
                'description': 'High confidence but not 100%'
            },
            {
                'confidence': 75,
                'best_match': 'asperin',
                'is_valid': False,
                'description': 'Medium confidence'
            },
            {
                'confidence': 45,
                'best_match': 'asirin',
                'is_valid': False,
                'description': 'Low confidence'
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔬 Test Case {i}: {test_case['description']}")
            print(f"   Confidence: {test_case['confidence']}%")
            
            # Simulate OCR result
            ocr_result = {
                'is_valid': test_case['is_valid'],
                'confidence': test_case['confidence'],
                'best_match': test_case['best_match'],
                'extracted_text': f'Patient prescription containing {test_case["best_match"]} 500mg tablets',
                'extracted_medicines': [test_case['best_match'], 'paracetamol']
            }
            
            # Update cart item with OCR result (simulating the bulk_ocr_verification logic)
            cart_item.validation_data = ocr_result
            
            # Check if pharmacy review is required (confidence < 100%)
            if test_case['confidence'] < 100:
                cart_item.pharmacy_review_required = True
                cart_item.pharmacy_review_status = 'pending'
                print(f"   ✅ Pharmacy review REQUIRED (confidence < 100%)")
            else:
                cart_item.pharmacy_review_required = False
                cart_item.pharmacy_review_status = 'not_required'
                print(f"   ✅ Pharmacy review NOT required (confidence = 100%)")
                
            cart_item.save()
            
            # Test cart item methods
            print(f"   📊 requires_pharmacy_review(): {cart_item.requires_pharmacy_review()}")
            print(f"   📊 get_ocr_confidence(): {cart_item.get_ocr_confidence()}%")
            print(f"   📊 get_ocr_best_match(): {cart_item.get_ocr_best_match()}")
            print(f"   📊 pharmacy_review_status: {cart_item.pharmacy_review_status}")
        
        # Test pharmacy review functionality
        print(f"\n🏥 Testing Pharmacy Review Dashboard")
        
        # Get pending reviews for pharmacy
        pending_reviews = CartItem.objects.filter(
            medicine__pharmacy=pharmacy,
            pharmacy_review_required=True,
            pharmacy_review_status='pending'
        )
        
        print(f"   📋 Pending reviews for {pharmacy.name}: {pending_reviews.count()}")
        
        for review in pending_reviews:
            print(f"   - Medicine: {review.medicine.name}")
            print(f"     Customer: {review.cart.customer.name}")
            print(f"     OCR Confidence: {review.get_ocr_confidence()}%")
            print(f"     Status: {review.pharmacy_review_status}")
        
        # Simulate pharmacy approval
        if pending_reviews.exists():
            test_review = pending_reviews.first()
            test_review.pharmacy_review_status = 'approved'
            test_review.pharmacy_review_notes = 'Medicine verified in prescription image. Approved for dispensing.'
            test_review.reviewed_by = pharmacy_user
            test_review.reviewed_at = datetime.now()
            test_review.save()
            
            print(f"\n   ✅ Simulated pharmacy approval for {test_review.medicine.name}")
            print(f"   📝 Review notes: {test_review.pharmacy_review_notes}")
        
        print(f"\n🎉 OCR Enhancement Test Completed Successfully!")
        print(f"📊 Summary:")
        print(f"   - Pharmacy: {pharmacy.name}")
        print(f"   - Customer: {customer.name}")
        print(f"   - Medicine: {medicine.name}")
        print(f"   - Cart items requiring review: {CartItem.objects.filter(medicine__pharmacy=pharmacy, pharmacy_review_required=True).count()}")
        print(f"   - Approved reviews: {CartItem.objects.filter(medicine__pharmacy=pharmacy, pharmacy_review_status='approved').count()}")
        print(f"   - Pending reviews: {CartItem.objects.filter(medicine__pharmacy=pharmacy, pharmacy_review_status='pending').count()}")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_ocr_enhancement()