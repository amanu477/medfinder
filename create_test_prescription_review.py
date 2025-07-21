#!/usr/bin/env python
"""
Create Test Data for Prescription Review Demo
Shows pharmacy interface for checking prescription photos
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from customer.models import Customer, Cart, CartItem
from pharmacy.models import Pharmacy, Medicine
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageDraw, ImageFont
import tempfile

def create_prescription_image_with_medicine(medicine_name, filename="test_prescription.png"):
    """Create a prescription image containing the specified medicine"""
    # Create a realistic prescription image
    img = Image.new('RGB', (600, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add header
    draw.text((50, 50), "ADDIS ABABA MEDICAL CENTER", fill='black', font=font_large)
    draw.text((50, 80), "Dr. Alemayehu Tadesse - Internal Medicine", fill='black', font=font_medium)
    draw.text((50, 110), "Phone: +251-11-123-4567", fill='black', font=font_small)
    
    # Add a line
    draw.line([(50, 140), (550, 140)], fill='black', width=2)
    
    # Patient info
    y_pos = 170
    draw.text((50, y_pos), "PRESCRIPTION", fill='black', font=font_large)
    y_pos += 50
    
    draw.text((50, y_pos), "Patient: Dawit Gebeyehu", fill='black', font=font_medium)
    y_pos += 30
    draw.text((50, y_pos), "Age: 35 years", fill='black', font=font_medium)
    y_pos += 30
    draw.text((50, y_pos), "Date: July 21, 2025", fill='black', font=font_medium)
    y_pos += 50
    
    # Prescription details
    draw.text((50, y_pos), "Rx:", fill='black', font=font_medium)
    y_pos += 40
    
    # Add the requested medicine
    draw.text((70, y_pos), f"1. {medicine_name} 500mg", fill='black', font=font_medium)
    y_pos += 25
    draw.text((90, y_pos), "Take 1 tablet twice daily after meals", fill='black', font=font_small)
    y_pos += 25
    draw.text((90, y_pos), "Duration: 7 days", fill='black', font=font_small)
    y_pos += 40
    
    # Add some other medicines
    draw.text((70, y_pos), "2. Paracetamol 500mg", fill='black', font=font_medium)
    y_pos += 25
    draw.text((90, y_pos), "Take 1 tablet as needed for fever", fill='black', font=font_small)
    y_pos += 40
    
    # Doctor signature area
    y_pos += 50
    draw.text((50, y_pos), "Doctor's Signature:", fill='black', font=font_medium)
    y_pos += 30
    draw.text((50, y_pos), "Dr. Alemayehu Tadesse", fill='black', font=font_medium)
    
    # Add medical seal (simple circle)
    draw.ellipse([400, y_pos-20, 500, y_pos+30], outline='blue', width=2)
    draw.text((415, y_pos-5), "MEDICAL", fill='blue', font=font_small)
    draw.text((425, y_pos+10), "SEAL", fill='blue', font=font_small)
    
    # Save the image
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    img.save(temp_path)
    return temp_path

def create_test_prescription_review_data():
    """Create test data for pharmacy prescription review"""
    
    print("Creating Test Data for Pharmacy Prescription Review")
    print("=" * 55)
    
    try:
        # Get test users
        customer = Customer.objects.get(user__username='testcustomer')
        pharmacy = Pharmacy.objects.get(user__username='testpharmacy')
        
        print(f"Customer: {customer.name}")
        print(f"Pharmacy: {pharmacy.name}")
        
        # Get or create cart
        cart, _ = Cart.objects.get_or_create(customer=customer)
        
        # Test Case 1: Medicine found in prescription (Aspirin)
        print("\n1. Creating test case: Medicine FOUND in prescription")
        
        aspirin = Medicine.objects.filter(pharmacy=pharmacy, name__icontains='aspirin').first()
        if not aspirin:
            aspirin = Medicine.objects.create(
                pharmacy=pharmacy,
                name='Aspirin 500mg',
                price=15.00,
                description='Pain relief and anti-inflammatory',
                is_available=True
            )
        
        # Create prescription image with Aspirin
        prescription_path = create_prescription_image_with_medicine('Aspirin', 'aspirin_prescription.png')
        
        # Create cart item with prescription
        cart_item1, created = CartItem.objects.get_or_create(
            cart=cart,
            medicine=aspirin,
            defaults={'quantity': 2}
        )
        
        # Add prescription image to cart item
        with open(prescription_path, 'rb') as f:
            cart_item1.prescription_image.save(
                'aspirin_prescription.png',
                SimpleUploadedFile('aspirin_prescription.png', f.read(), content_type='image/png')
            )
        
        # Set OCR validation data (high confidence - found in prescription)
        cart_item1.validation_data = {
            'is_valid': True,
            'confidence': 95,
            'best_match': 'Aspirin',
            'extracted_text': 'Patient: Dawit Gebeyehu\nAge: 35 years\nDate: July 21, 2025\nRx:\n1. Aspirin 500mg\nTake 1 tablet twice daily after meals\nDuration: 7 days\n2. Paracetamol 500mg\nTake 1 tablet as needed for fever',
            'extracted_medicines': ['Aspirin', 'Paracetamol'],
            'validation_reason': 'Medicine found in prescription image'
        }
        cart_item1.pharmacy_review_required = True
        cart_item1.pharmacy_review_status = 'pending'
        cart_item1.save()
        
        print(f"   Created: {aspirin.name} - OCR Confidence: 95%")
        print(f"   Status: Requires pharmacy review (confidence < 100%)")
        
        # Test Case 2: Medicine NOT found in prescription (Ibuprofen)
        print("\n2. Creating test case: Medicine NOT FOUND in prescription")
        
        ibuprofen = Medicine.objects.filter(pharmacy=pharmacy, name__icontains='ibuprofen').first()
        if not ibuprofen:
            ibuprofen = Medicine.objects.create(
                pharmacy=pharmacy,
                name='Ibuprofen 400mg',
                price=25.00,
                description='Anti-inflammatory pain relief',
                is_available=True
            )
        
        # Create cart item for ibuprofen (but prescription doesn't contain it)
        cart_item2, created = CartItem.objects.get_or_create(
            cart=cart,
            medicine=ibuprofen,
            defaults={'quantity': 1}
        )
        
        # Use the same prescription image (which doesn't contain Ibuprofen)
        with open(prescription_path, 'rb') as f:
            cart_item2.prescription_image.save(
                'ibuprofen_prescription.png',
                SimpleUploadedFile('ibuprofen_prescription.png', f.read(), content_type='image/png')
            )
        
        # Set OCR validation data (0% confidence - NOT found in prescription)
        cart_item2.validation_data = {
            'is_valid': False,
            'confidence': 0,
            'best_match': None,
            'extracted_text': 'Patient: Dawit Gebeyehu\nAge: 35 years\nDate: July 21, 2025\nRx:\n1. Aspirin 500mg\nTake 1 tablet twice daily after meals\nDuration: 7 days\n2. Paracetamol 500mg\nTake 1 tablet as needed for fever',
            'extracted_medicines': ['Aspirin', 'Paracetamol'],
            'validation_reason': 'Medicine not found in prescription image'
        }
        cart_item2.pharmacy_review_required = True
        cart_item2.pharmacy_review_status = 'pending'
        cart_item2.save()
        
        print(f"   Created: {ibuprofen.name} - OCR Confidence: 0%")
        print(f"   Status: Requires pharmacy review (medicine not in prescription)")
        
        # Summary
        print("\n" + "=" * 55)
        print("TEST DATA CREATED SUCCESSFULLY!")
        print("=" * 55)
        
        pending_reviews = CartItem.objects.filter(
            medicine__pharmacy=pharmacy,
            pharmacy_review_required=True,
            pharmacy_review_status='pending'
        )
        
        print(f"Pharmacy: {pharmacy.name}")
        print(f"Pending Reviews: {pending_reviews.count()}")
        
        for item in pending_reviews:
            print(f"  • {item.medicine.name}")
            print(f"    Customer: {item.cart.customer.name}")
            print(f"    OCR Confidence: {item.get_ocr_confidence()}%")
            print(f"    Prescription Image: {'✓' if item.prescription_image else '✗'}")
            print(f"    Review Required: {'✓' if item.requires_pharmacy_review() else '✗'}")
        
        print(f"\n📋 Pharmacy can now review prescriptions at:")
        print(f"   /pharmacy/prescription-reviews/")
        print(f"\n🔍 Each review shows:")
        print(f"   • Customer prescription image")
        print(f"   • OCR analysis results") 
        print(f"   • Medicine being requested")
        print(f"   • Manual approval/rejection form")
        
        # Cleanup temp file
        try:
            os.remove(prescription_path)
        except:
            pass
            
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")

if __name__ == '__main__':
    create_test_prescription_review_data()