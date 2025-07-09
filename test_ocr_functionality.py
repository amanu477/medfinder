#!/usr/bin/env python3
"""
Test script to verify OCR functionality for prescription validation
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append('/home/runner/workspace')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from customer.ocr_service import PrescriptionOCRService
from PIL import Image, ImageDraw, ImageFont

def create_test_prescription_image():
    """Create a simple test prescription image with medicine names"""
    # Create a white background image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fall back to basic font if needed
    try:
        font_size = 24
        font = ImageFont.load_default()
    except:
        font = None
    
    # Add prescription content
    prescription_text = [
        "PRESCRIPTION",
        "Patient: John Doe",
        "Date: 2025-01-09",
        "",
        "1. Paracetamol 500mg - Take 2 tablets twice daily",
        "2. Amoxicillin 250mg - Take 1 capsule three times daily",
        "3. Vitamin C 1000mg - Take 1 tablet daily",
        "",
        "Dr. Smith",
        "Medical License: 12345"
    ]
    
    y_position = 50
    for line in prescription_text:
        draw.text((50, y_position), line, fill='black', font=font)
        y_position += 40
    
    # Save the test image
    test_image_path = '/tmp/test_prescription.png'
    image.save(test_image_path)
    print(f"Created test prescription image: {test_image_path}")
    return test_image_path

def test_ocr_service():
    """Test the OCR service with a sample prescription"""
    print("Testing OCR functionality...")
    
    # Create test prescription image
    test_image_path = create_test_prescription_image()
    
    # Initialize OCR service
    ocr_service = PrescriptionOCRService()
    
    # Test 1: Extract text from the image
    print("\n1. Testing text extraction...")
    extracted_text = ocr_service.extract_text_from_image(test_image_path)
    print(f"Extracted text: {extracted_text[:200]}...")
    
    # Test 2: Extract medicine names
    print("\n2. Testing medicine name extraction...")
    medicine_names = ocr_service.extract_medicine_names(extracted_text)
    print(f"Extracted medicine names: {medicine_names}")
    
    # Test 3: Validate medicine names
    print("\n3. Testing medicine validation...")
    test_medicines = ['Paracetamol', 'Amoxicillin', 'Vitamin C', 'Aspirin']
    
    for medicine in test_medicines:
        result = ocr_service.validate_medicine_name(medicine, test_image_path, threshold=60)
        print(f"Medicine: {medicine}")
        print(f"  Valid: {result['is_valid']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Best Match: {result.get('best_match', 'None')}")
        print(f"  Error: {result.get('error', 'None')}")
        print()
    
    # Test 4: Get prescription summary
    print("\n4. Testing prescription summary...")
    summary = ocr_service.get_prescription_summary(test_image_path)
    print(f"Summary: {summary}")
    
    # Clean up
    try:
        os.remove(test_image_path)
        print(f"\nCleaned up test image: {test_image_path}")
    except:
        pass

if __name__ == "__main__":
    test_ocr_service()