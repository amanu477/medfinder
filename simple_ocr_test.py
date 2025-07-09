#!/usr/bin/env python3
"""
Simple OCR test to verify the functionality works
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

def test_basic_ocr():
    """Test basic OCR functionality"""
    print("Testing basic OCR functionality...")
    
    # Initialize OCR service
    ocr_service = PrescriptionOCRService()
    
    # Test validation with common medicine names
    test_medicines = ['Paracetamol', 'Amoxicillin', 'Aspirin']
    
    for medicine in test_medicines:
        # Test the extract_medicine_names function with simple text
        test_text = f"Patient Name: John Doe\nPrescription:\n1. {medicine} 500mg - Take 2 tablets twice daily\nDr. Smith"
        
        extracted_names = ocr_service.extract_medicine_names(test_text)
        print(f"Medicine: {medicine}")
        print(f"Test text: {test_text}")
        print(f"Extracted names: {extracted_names}")
        
        # Check if medicine is found
        found = any(medicine.lower() in name.lower() for name in extracted_names)
        print(f"Found: {found}")
        print("-" * 50)

if __name__ == "__main__":
    test_basic_ocr()