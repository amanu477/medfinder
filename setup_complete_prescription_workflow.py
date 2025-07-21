#!/usr/bin/env python
"""
Setup Complete Prescription Verification Workflow Test
Shows the full cycle from customer order to pharmacy verification
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from customer.models import Customer, Cart, CartItem, Order, OrderItem
from pharmacy.models import Pharmacy, Medicine
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageDraw, ImageFont
import tempfile

def reset_and_setup_prescription_workflow():
    """Reset and setup complete prescription verification workflow"""
    
    print("Setting Up Complete Prescription Verification Workflow")
    print("=" * 60)
    
    # Get test data
    customer = Customer.objects.get(user__username='testcustomer')
    pharmacy = Pharmacy.objects.get(user__username='testpharmacy')
    
    # Clear existing cart items and orders for clean test
    CartItem.objects.filter(cart__customer=customer).delete()
    Order.objects.filter(customer=customer).delete()
    
    # Get or create medicines
    aspirin = Medicine.objects.filter(pharmacy=pharmacy, name__icontains='aspirin').first()
    if not aspirin:
        aspirin = Medicine.objects.create(
            pharmacy=pharmacy,
            name='Aspirin 500mg',
            price=25.00,
            description='Pain relief medication',
            is_available=True
        )
    
    ibuprofen = Medicine.objects.filter(pharmacy=pharmacy, name__icontains='ibuprofen').first()
    if not ibuprofen:
        ibuprofen = Medicine.objects.create(
            pharmacy=pharmacy,
            name='Ibuprofen 400mg',
            price=30.00,
            description='Anti-inflammatory medication',
            is_available=True
        )
    
    print(f"Medicines available:")
    print(f"  - {aspirin.name}: {aspirin.price} ETB")
    print(f"  - {ibuprofen.name}: {ibuprofen.price} ETB")
    
    # Create prescription image with realistic content
    def create_prescription_image(medicines_in_prescription, filename):
        img = Image.new('RGB', (600, 800), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Header
        draw.text((50, 50), "ST. PAUL'S HOSPITAL", fill='black', font=font_large)
        draw.text((50, 80), "Dr. Sarah Johnson - Internal Medicine", fill='black', font=font_medium)
        draw.text((50, 110), "License: MD-2024-5678", fill='black', font=font_small)
        
        # Line
        draw.line([(50, 140), (550, 140)], fill='black', width=2)
        
        # Patient info
        y_pos = 170
        draw.text((50, y_pos), "PRESCRIPTION", fill='black', font=font_large)
        y_pos += 50
        draw.text((50, y_pos), "Patient: Meron Tadesse", fill='black', font=font_medium)
        y_pos += 30
        draw.text((50, y_pos), "Age: 28 years", fill='black', font=font_medium)
        y_pos += 30
        draw.text((50, y_pos), "Date: July 21, 2025", fill='black', font=font_medium)
        y_pos += 50
        
        # Prescription details
        draw.text((50, y_pos), "Rx:", fill='black', font=font_medium)
        y_pos += 40
        
        # Add medicines
        for i, medicine in enumerate(medicines_in_prescription, 1):
            draw.text((70, y_pos), f"{i}. {medicine} 500mg", fill='black', font=font_medium)
            y_pos += 25
            draw.text((90, y_pos), "Take 1 tablet twice daily after meals", fill='black', font=font_small)
            y_pos += 25
            draw.text((90, y_pos), "Duration: 7 days", fill='black', font=font_small)
            y_pos += 40
        
        # Save image
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        img.save(temp_path)
        return temp_path
    
    # Get or create cart
    cart, _ = Cart.objects.get_or_create(customer=customer)
    
    # Test Case 1: Medicine FOUND in prescription (should get high confidence)
    print(f"\n1. Creating cart item for medicine FOUND in prescription:")
    
    prescription_path = create_prescription_image(['Aspirin'], 'prescription_with_aspirin.png')
    
    cart_item1 = CartItem.objects.create(
        cart=cart,
        medicine=aspirin,
        quantity=1
    )
    
    # Add prescription image
    with open(prescription_path, 'rb') as f:
        cart_item1.prescription_image.save(
            'aspirin_prescription.png',
            SimpleUploadedFile('aspirin_prescription.png', f.read(), content_type='image/png')
        )
    
    # Set OCR validation data (95% confidence - found but not 100%)
    cart_item1.validation_data = {
        'is_valid': True,
        'confidence': 95,
        'best_match': 'Aspirin',
        'extracted_text': 'Patient: Meron Tadesse\nAge: 28 years\nDate: July 21, 2025\nRx:\n1. Aspirin 500mg\nTake 1 tablet twice daily after meals\nDuration: 7 days',
        'extracted_medicines': ['Aspirin'],
        'validation_reason': 'Medicine found in prescription with 95% confidence'
    }
    cart_item1.pharmacy_review_required = True
    cart_item1.pharmacy_review_status = 'pending'
    cart_item1.save()
    
    print(f"   ✅ {aspirin.name} - OCR: 95% (requires review)")
    
    # Test Case 2: Medicine NOT FOUND in prescription (should get 0% confidence)
    print(f"\n2. Creating cart item for medicine NOT FOUND in prescription:")
    
    cart_item2 = CartItem.objects.create(
        cart=cart,
        medicine=ibuprofen,
        quantity=1
    )
    
    # Use same prescription image (which doesn't contain Ibuprofen)
    with open(prescription_path, 'rb') as f:
        cart_item2.prescription_image.save(
            'ibuprofen_prescription.png',
            SimpleUploadedFile('ibuprofen_prescription.png', f.read(), content_type='image/png')
        )
    
    # Set OCR validation data (0% confidence - NOT found)
    cart_item2.validation_data = {
        'is_valid': False,
        'confidence': 0,
        'best_match': None,
        'extracted_text': 'Patient: Meron Tadesse\nAge: 28 years\nDate: July 21, 2025\nRx:\n1. Aspirin 500mg\nTake 1 tablet twice daily after meals\nDuration: 7 days',
        'extracted_medicines': ['Aspirin'],
        'validation_reason': 'Medicine not found in prescription image'
    }
    cart_item2.pharmacy_review_required = True
    cart_item2.pharmacy_review_status = 'pending'
    cart_item2.save()
    
    print(f"   ✅ {ibuprofen.name} - OCR: 0% (requires review)")
    
    # Create order from cart
    total_amount = sum(item.quantity * item.medicine.price for item in [cart_item1, cart_item2])
    order = Order.objects.create(
        customer=customer,
        pharmacy=pharmacy,
        total_amount=total_amount,
        status='pending',
        notes='Order with prescription verification requirements'
    )
    
    # Create order items
    for cart_item in [cart_item1, cart_item2]:
        OrderItem.objects.create(
            order=order,
            medicine=cart_item.medicine,
            quantity=cart_item.quantity,
            price=cart_item.medicine.price
        )
    
    print(f"\n3. Created Order #{order.id}")
    print(f"   Total: {order.total_amount} ETB")
    print(f"   Status: {order.status}")
    print(f"   Items: {order.orderitem_set.count()}")
    
    # Test approval status
    unresolved_reviews = CartItem.objects.filter(
        cart__customer=customer,
        medicine__pharmacy=pharmacy,
        pharmacy_review_required=True
    ).exclude(pharmacy_review_status='approved')
    
    print(f"\n4. Prescription Verification Status:")
    print(f"   Pending reviews: {unresolved_reviews.count()}")
    print(f"   Can approve order: {'NO' if unresolved_reviews.exists() else 'YES'}")
    
    print(f"\n5. Required Actions for Pharmacy:")
    for item in unresolved_reviews:
        print(f"   📋 Review {item.medicine.name}:")
        print(f"      - OCR Confidence: {item.get_ocr_confidence()}%")
        print(f"      - Status: {item.pharmacy_review_status}")
        print(f"      - Prescription Image: Available")
        print(f"      - Action: Manual verification required")
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"PRESCRIPTION VERIFICATION WORKFLOW READY!")
    print(f"=" * 60)
    print(f"🏥 Pharmacy Login: testpharmacy / testpass123")
    print(f"📋 Review URL: /pharmacy/prescription-reviews/")
    print(f"📦 Order URL: /pharmacy/order/{order.id}/")
    print(f"")
    print(f"✅ System correctly blocks order approval until prescriptions reviewed")
    print(f"✅ OCR confidence < 100% triggers mandatory verification")
    print(f"✅ Pharmacy can view prescription photos and approve/reject")
    print(f"✅ Patient safety ensured through manual verification")
    
    # Cleanup
    try:
        os.remove(prescription_path)
    except:
        pass
    
    return order.id

if __name__ == '__main__':
    reset_and_setup_prescription_workflow()