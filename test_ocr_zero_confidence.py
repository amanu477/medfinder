#!/usr/bin/env python
"""
Test OCR Zero Confidence Enhancement
Verifies that OCR returns 0% confidence when manually selected medicine is not found in prescription
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from customer.ocr_service import PrescriptionOCRService
from customer.models import Customer, Cart, CartItem
from pharmacy.models import Pharmacy, Medicine
import tempfile
from PIL import Image, ImageDraw, ImageFont

def create_test_prescription_image(medicines_list, filename="test_prescription.png"):
    """Create a test prescription image with specific medicines"""
    # Create a white image
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to default if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Create prescription content
    y_position = 50
    draw.text((50, y_position), "PRESCRIPTION", fill='black', font=font)
    y_position += 40
    
    draw.text((50, y_position), "Patient: John Doe", fill='black', font=font)
    y_position += 30
    
    draw.text((50, y_position), "Date: 2025-07-21", fill='black', font=font)
    y_position += 40
    
    # Add prescribed medicines
    for medicine in medicines_list:
        draw.text((50, y_position), f"• {medicine} 500mg - Take twice daily", fill='black', font=font)
        y_position += 30
    
    draw.text((50, y_position + 20), "Doctor's Signature", fill='black', font=font)
    
    # Save the image
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    img.save(temp_path)
    return temp_path

def test_zero_confidence_when_medicine_not_found():
    """Test that OCR returns 0% confidence when medicine is not in prescription"""
    
    print("Testing OCR Zero Confidence Enhancement")
    print("=" * 50)
    
    # Initialize OCR service
    ocr_service = PrescriptionOCRService()
    
    # Test Case 1: Medicine found in prescription (should have good confidence)
    print("1. Testing medicine FOUND in prescription:")
    
    # Create prescription with aspirin and paracetamol
    prescription_path = create_test_prescription_image(['Aspirin', 'Paracetamol'], "prescription_with_aspirin.png")
    
    # Test aspirin (should be found)
    result_found = ocr_service.validate_medicine_name('Aspirin', prescription_path)
    
    print(f"   Medicine searched: Aspirin")
    print(f"   OCR Confidence: {result_found['confidence']}%")
    print(f"   Best match: {result_found['best_match']}")
    print(f"   Validation reason: {result_found.get('validation_reason', 'N/A')}")
    print(f"   Expected: Should have confidence > 0%")
    print(f"   Result: {'✅ PASS' if result_found['confidence'] > 0 else '❌ FAIL'}")
    
    # Test Case 2: Medicine NOT found in prescription (should have 0% confidence)
    print("\n2. Testing medicine NOT FOUND in prescription:")
    
    # Test ibuprofen (NOT in the prescription)
    result_not_found = ocr_service.validate_medicine_name('Ibuprofen', prescription_path)
    
    print(f"   Medicine searched: Ibuprofen")
    print(f"   OCR Confidence: {result_not_found['confidence']}%")
    print(f"   Best match: {result_not_found['best_match']}")
    print(f"   Validation reason: {result_not_found.get('validation_reason', 'N/A')}")
    print(f"   Expected: Should have 0% confidence")
    print(f"   Result: {'✅ PASS' if result_not_found['confidence'] == 0 else '❌ FAIL'}")
    
    # Test Case 3: Completely different medicine (should have 0% confidence)
    print("\n3. Testing completely different medicine:")
    
    # Test a medicine that's definitely not in prescription
    result_different = ocr_service.validate_medicine_name('Amoxicillin', prescription_path)
    
    print(f"   Medicine searched: Amoxicillin")
    print(f"   OCR Confidence: {result_different['confidence']}%")
    print(f"   Best match: {result_different['best_match']}")
    print(f"   Validation reason: {result_different.get('validation_reason', 'N/A')}")
    print(f"   Expected: Should have 0% confidence")
    print(f"   Result: {'✅ PASS' if result_different['confidence'] == 0 else '❌ FAIL'}")
    
    # Test Case 4: Test with empty prescription
    print("\n4. Testing with empty prescription:")
    
    # Create empty prescription
    empty_prescription_path = create_test_prescription_image([], "empty_prescription.png")
    result_empty = ocr_service.validate_medicine_name('Aspirin', empty_prescription_path)
    
    print(f"   Medicine searched: Aspirin")
    print(f"   OCR Confidence: {result_empty['confidence']}%")
    print(f"   Best match: {result_empty['best_match']}")
    print(f"   Expected: Should have 0% confidence")
    print(f"   Result: {'✅ PASS' if result_empty['confidence'] == 0 else '❌ FAIL'}")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY - OCR Zero Confidence Enhancement:")
    
    test_results = [
        ("Medicine found in prescription", result_found['confidence'] > 0),
        ("Medicine not found in prescription", result_not_found['confidence'] == 0),
        ("Different medicine not in prescription", result_different['confidence'] == 0),
        ("Empty prescription", result_empty['confidence'] == 0)
    ]
    
    passed_tests = sum(1 for _, passed in test_results if passed)
    total_tests = len(test_results)
    
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\nTest Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("   OCR now correctly returns 0% confidence when medicine is not found in prescription")
        print("   This ensures pharmacy review is required for all non-matching medicines")
    else:
        print("⚠️ Some tests failed. OCR enhancement needs adjustment.")
    
    # Cleanup test files
    try:
        os.remove(prescription_path)
        os.remove(empty_prescription_path)
    except:
        pass

def test_integration_with_cart_system():
    """Test integration with cart system and pharmacy review workflow"""
    
    print("\n" + "=" * 50)
    print("INTEGRATION TEST - Cart System with Zero Confidence OCR")
    print("=" * 50)
    
    try:
        # Get test data
        customer = Customer.objects.get(user__username='testcustomer')
        pharmacy = Pharmacy.objects.get(user__username='testpharmacy')
        
        # Get a medicine that won't be in our test prescription
        medicine = Medicine.objects.filter(pharmacy=pharmacy, name__icontains='ibuprofen').first()
        if not medicine:
            # Create a test medicine if it doesn't exist
            medicine = Medicine.objects.create(
                pharmacy=pharmacy,
                name='Ibuprofen 400mg',
                price=25.00,
                description='Pain relief medicine',
                is_available=True
            )
        
        # Create cart and add medicine
        cart, _ = Cart.objects.get_or_create(customer=customer)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            medicine=medicine,
            defaults={'quantity': 1}
        )
        
        # Create prescription without ibuprofen (contains only aspirin)
        prescription_path = create_test_prescription_image(['Aspirin'], "test_integration_prescription.png")
        
        # Simulate OCR validation for ibuprofen (should get 0% confidence)
        ocr_service = PrescriptionOCRService()
        ocr_result = ocr_service.validate_medicine_name(medicine.name, prescription_path)
        
        # Update cart item with OCR validation
        cart_item.validation_data = {
            'is_valid': ocr_result['is_valid'],
            'confidence': ocr_result['confidence'],
            'best_match': ocr_result['best_match'],
            'extracted_text': ocr_result['extracted_text'],
            'extracted_medicines': ocr_result['extracted_medicines'],
            'validation_reason': ocr_result.get('validation_reason', 'OCR validation completed')
        }
        
        # Set pharmacy review requirements based on confidence  
        cart_item.pharmacy_review_required = (ocr_result['confidence'] < 100)
        if cart_item.pharmacy_review_required:
            cart_item.pharmacy_review_status = 'pending'
        
        cart_item.save()
        
        print(f"Medicine: {medicine.name}")
        print(f"Prescription contains: Aspirin only")
        print(f"OCR Confidence: {cart_item.get_ocr_confidence()}%")
        print(f"Pharmacy review required: {cart_item.requires_pharmacy_review()}")
        print(f"Review status: {cart_item.pharmacy_review_status}")
        print(f"Can checkout: {'No' if cart_item.requires_pharmacy_review() and cart_item.pharmacy_review_status == 'pending' else 'Yes'}")
        
        # Verify expected behavior
        expected_confidence = 0
        expected_review_required = True
        expected_status = 'pending'
        
        integration_success = (
            cart_item.get_ocr_confidence() == expected_confidence and
            cart_item.requires_pharmacy_review() == expected_review_required and
            cart_item.pharmacy_review_status == expected_status
        )
        
        print(f"\nIntegration Test Result: {'✅ PASS' if integration_success else '❌ FAIL'}")
        
        if integration_success:
            print("🎉 Integration successful!")
            print("   Medicine not in prescription → 0% confidence → Pharmacy review required")
        
        # Cleanup
        try:
            os.remove(prescription_path)
        except:
            pass
            
        return integration_success
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False

if __name__ == '__main__':
    test_zero_confidence_when_medicine_not_found()
    test_integration_with_cart_system()