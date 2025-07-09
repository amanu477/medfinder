#!/usr/bin/env python3
"""
Debug script to test OCR functionality and identify issues
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from customer.ocr_service import PrescriptionOCRService
from pharmacy.models import Medicine
import glob

def test_ocr_with_existing_images():
    """Test OCR with existing prescription images"""
    print("=" * 60)
    print("OCR DEBUG TEST")
    print("=" * 60)
    
    ocr_service = PrescriptionOCRService()
    
    # Find prescription images
    prescription_images = glob.glob("media/order_prescriptions/*.jpg") + \
                         glob.glob("media/order_prescriptions/*.png") + \
                         glob.glob("media/order_prescriptions/*.jpeg")
    
    if not prescription_images:
        print("No prescription images found in media/order_prescriptions/")
        print("Looking for any images in media/...")
        
        # Check for any images in media folder
        all_images = glob.glob("media/**/*.jpg", recursive=True) + \
                    glob.glob("media/**/*.png", recursive=True) + \
                    glob.glob("media/**/*.jpeg", recursive=True)
        
        if all_images:
            print(f"Found {len(all_images)} images in media folder:")
            for img in all_images[:5]:  # Show first 5
                print(f"  - {img}")
        else:
            print("No images found in media folder")
            return
    
    # Test with available images
    test_images = prescription_images[:3] if prescription_images else all_images[:3]
    
    print(f"\nTesting OCR with {len(test_images)} images:")
    
    for i, image_path in enumerate(test_images):
        print(f"\n--- Testing Image {i+1}: {image_path} ---")
        
        # Extract text
        extracted_text = ocr_service.extract_text_from_image(image_path)
        print(f"Extracted text: '{extracted_text}'")
        print(f"Text length: {len(extracted_text)}")
        
        if extracted_text:
            # Extract medicine names
            medicine_names = ocr_service.extract_medicine_names(extracted_text)
            print(f"Extracted medicine names: {medicine_names}")
            
            # Test with sample medicine names
            sample_medicines = ["Paracetamol", "Ibuprofen", "Amoxicillin", "Aspirin"]
            
            for medicine_name in sample_medicines:
                confidence = ocr_service.get_medicine_confidence(medicine_name, extracted_text)
                print(f"  {medicine_name}: {confidence:.2f}% confidence")
        else:
            print("  No text extracted from image")

def test_ocr_with_sample_text():
    """Test OCR validation with sample prescription text"""
    print("\n" + "=" * 60)
    print("TESTING OCR WITH SAMPLE TEXT")
    print("=" * 60)
    
    ocr_service = PrescriptionOCRService()
    
    # Sample prescription texts
    sample_texts = [
        "Paracetamol 500mg tablets - Take 1 tablet twice daily",
        "Amoxicillin 500mg capsules - Take 1 capsule three times daily",
        "Ibuprofen 400mg tablets - Take 1 tablet as needed for pain",
        "Rx: Paracetamol 500mg Tab BD x 7 days",
        "1. Paracetamol 500mg - 1 tab BD\n2. Ibuprofen 400mg - 1 tab TDS",
        "PARACETAMOL 500MG TABLETS\nTAKE ONE TABLET TWICE DAILY",
        "paracetamol 500mg tab bd",
        "Paracetam0l 500mg (OCR error simulation)",
        "Para cetamol 500mg (space error simulation)"
    ]
    
    test_medicines = ["Paracetamol", "Amoxicillin", "Ibuprofen", "Aspirin", "Ciprofloxacin"]
    
    for i, text in enumerate(sample_texts):
        print(f"\n--- Sample Text {i+1}: {text} ---")
        
        # Extract medicine names
        medicine_names = ocr_service.extract_medicine_names(text)
        print(f"Extracted medicine names: {medicine_names}")
        
        # Test validation
        for medicine in test_medicines:
            confidence = ocr_service.get_medicine_confidence(medicine, text)
            status = "✓ FOUND" if confidence >= 60 else "✗ NOT FOUND"
            print(f"  {medicine}: {confidence:.2f}% - {status}")

def test_database_medicines():
    """Test with actual medicines from database"""
    print("\n" + "=" * 60)
    print("TESTING WITH DATABASE MEDICINES")
    print("=" * 60)
    
    ocr_service = PrescriptionOCRService()
    
    # Get medicines from database
    medicines = Medicine.objects.all()[:10]  # First 10 medicines
    
    if not medicines:
        print("No medicines found in database")
        return
    
    print(f"Found {medicines.count()} medicines in database")
    print("Testing first 10 medicines:")
    
    # Sample prescription text
    sample_text = "Paracetamol 500mg tablets - Take 1 tablet twice daily. Ibuprofen 400mg - Take as needed."
    
    print(f"\nSample prescription text: '{sample_text}'")
    print("Medicine validation results:")
    
    for medicine in medicines:
        confidence = ocr_service.get_medicine_confidence(medicine.name, sample_text)
        status = "✓ FOUND" if confidence >= 60 else "✗ NOT FOUND"
        print(f"  {medicine.name}: {confidence:.2f}% - {status}")

def test_fuzzy_matching():
    """Test fuzzy matching capabilities"""
    print("\n" + "=" * 60)
    print("TESTING FUZZY MATCHING")
    print("=" * 60)
    
    ocr_service = PrescriptionOCRService()
    
    # Test fuzzy matching with various text variations
    test_cases = [
        ("Paracetamol", "Paracetamol 500mg"),
        ("Paracetamol", "paracetamol"),
        ("Paracetamol", "PARACETAMOL"),
        ("Paracetamol", "Paracetam0l"),  # OCR error: o -> 0
        ("Paracetamol", "Para cetamol"),  # Space error
        ("Paracetamol", "Paracetamal"),  # Typo
        ("Ibuprofen", "Ibuprofen 400mg"),
        ("Ibuprofen", "lbuprofen"),  # I -> l OCR error
        ("Amoxicillin", "Amoxicillin 500mg capsules"),
        ("Amoxicillin", "Amoxicilin"),  # Missing l
    ]
    
    for medicine, text in test_cases:
        confidence = ocr_service.get_medicine_confidence(medicine, text)
        status = "✓ FOUND" if confidence >= 60 else "✗ NOT FOUND"
        print(f"'{medicine}' in '{text}': {confidence:.2f}% - {status}")

def main():
    """Main function to run all tests"""
    print("Starting OCR Debug Tests...\n")
    
    try:
        test_ocr_with_existing_images()
        test_ocr_with_sample_text()
        test_database_medicines()
        test_fuzzy_matching()
        
        print("\n" + "=" * 60)
        print("OCR DEBUG COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during OCR testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()