#!/usr/bin/env python3

"""
Debug script to test aspirin detection in OCR
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from customer.ocr_service import PrescriptionOCRService

def test_aspirin_detection():
    """Test aspirin detection with sample prescription text"""
    
    # Initialize OCR service
    ocr_service = PrescriptionOCRService()
    
    # Test with different sample prescription texts
    test_cases = [
        "Take Aspirin 100mg once daily after meals",
        "Aspirin tablet 81mg daily for heart health",
        "Prescribe: Paracetamol 500mg, Aspirin 100mg",
        "1. Aspirin 100mg - Take one tablet daily\n2. Paracetamol 500mg - Take as needed",
        "Patient needs:\n- Aspirin 100mg tablets\n- Paracetamol 500mg tablets",
        "Rx: Aspirin (low dose) 81mg od",
        "ASA 100mg daily", # ASA is a common abbreviation for aspirin
        "Acetylsalicylic acid 100mg daily", # Chemical name for aspirin
    ]
    
    print("=== Testing Aspirin Detection ===")
    print()
    
    for i, prescription_text in enumerate(test_cases, 1):
        print(f"Test Case {i}: {prescription_text}")
        print("-" * 60)
        
        # Test aspirin detection
        result = ocr_service.validate_medicine_name("aspirin", prescription_text)
        
        print(f"Result: {result}")
        print(f"Is Valid: {result['is_valid']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Best Match: {result.get('best_match', 'None')}")
        print(f"Extracted Medicines: {result.get('extracted_medicines', [])}")
        print()
        
        # Also test with variations
        aspirin_variations = ['aspirin', 'asprin', 'asa', 'acetylsalicylic']
        for variation in aspirin_variations:
            if variation != 'aspirin':
                var_result = ocr_service.validate_medicine_name(variation, prescription_text)
                print(f"  {variation} -> Valid: {var_result['is_valid']}, Confidence: {var_result['confidence']}")
        print()

def test_medicine_extraction():
    """Test medicine extraction from text"""
    
    ocr_service = PrescriptionOCRService()
    
    test_text = """
    Patient: John Doe
    Date: 2024-01-01
    
    Prescription:
    1. Aspirin 100mg - Take one tablet daily after meals
    2. Paracetamol 500mg - Take as needed for pain
    3. Amoxicillin 250mg - Take three times daily
    
    Instructions: Take all medications with food
    """
    
    print("=== Testing Medicine Extraction ===")
    print(f"Test text: {test_text}")
    print()
    
    extracted_medicines = ocr_service.extract_medicine_names(test_text)
    print(f"Extracted medicines: {extracted_medicines}")
    print()
    
    # Test each extracted medicine
    for medicine in extracted_medicines:
        result = ocr_service.validate_medicine_name(medicine, test_text)
        print(f"{medicine} -> Valid: {result['is_valid']}, Confidence: {result['confidence']}")

if __name__ == "__main__":
    test_aspirin_detection()
    test_medicine_extraction()