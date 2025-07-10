#!/usr/bin/env python3

"""
Test script to create a sample prescription image and test OCR with it
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import tempfile

def create_test_prescription_image():
    """Create a test prescription image with medicine names"""
    
    # Create a white background image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to default if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Draw prescription content
    y_position = 50
    
    # Title
    draw.text((50, y_position), "PRESCRIPTION", font=title_font, fill='black')
    y_position += 60
    
    # Patient info
    draw.text((50, y_position), "Patient: John Doe", font=font, fill='black')
    y_position += 40
    draw.text((50, y_position), "Date: 2024-01-15", font=font, fill='black')
    y_position += 60
    
    # Medicine prescriptions
    medicines = [
        "1. Aspirin 100mg - Take one tablet daily after meals",
        "2. Paracetamol 500mg - Take as needed for pain",
        "3. Amoxicillin 250mg - Take three times daily",
        "4. Ibuprofen 400mg - Take with food"
    ]
    
    for medicine in medicines:
        draw.text((50, y_position), medicine, font=font, fill='black')
        y_position += 40
    
    y_position += 40
    draw.text((50, y_position), "Instructions: Take all medications with food", font=font, fill='black')
    y_position += 40
    draw.text((50, y_position), "Dr. Smith", font=font, fill='black')
    
    # Save the image
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    img.save(temp_file.name, 'JPEG')
    temp_file.close()
    
    print(f"Test prescription image created: {temp_file.name}")
    return temp_file.name

def test_ocr_with_image():
    """Test OCR with the created image"""
    
    # Add Django setup
    import django
    from django.conf import settings
    
    # Configure Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
    django.setup()
    
    from customer.ocr_service import PrescriptionOCRService
    
    # Create test image
    image_path = create_test_prescription_image()
    
    try:
        # Initialize OCR service
        ocr_service = PrescriptionOCRService()
        
        # Test aspirin detection
        print("\n=== Testing OCR with Real Image ===")
        result = ocr_service.validate_medicine_name("aspirin", image_path)
        
        print(f"Aspirin validation result: {result}")
        print(f"Is Valid: {result['is_valid']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Best Match: {result.get('best_match', 'None')}")
        
        # Test paracetamol detection
        result2 = ocr_service.validate_medicine_name("paracetamol", image_path)
        print(f"\nParacetamol validation result: {result2}")
        print(f"Is Valid: {result2['is_valid']}")
        print(f"Confidence: {result2['confidence']}")
        print(f"Best Match: {result2.get('best_match', 'None')}")
        
        # Test medicine extraction
        extracted_medicines = ocr_service.extract_medicine_names(
            ocr_service.extract_text_from_image(image_path)
        )
        print(f"\nExtracted medicines: {extracted_medicines}")
        
        # Test with different medicine names
        test_medicines = ['aspirin', 'paracetamol', 'amoxicillin', 'ibuprofen']
        print("\n=== Testing Multiple Medicines ===")
        for med in test_medicines:
            result = ocr_service.validate_medicine_name(med, image_path)
            print(f"{med}: Valid={result['is_valid']}, Confidence={result['confidence']:.1f}%")
        
    finally:
        # Clean up
        os.unlink(image_path)
        print(f"\nCleaned up temporary file: {image_path}")

if __name__ == "__main__":
    test_ocr_with_image()