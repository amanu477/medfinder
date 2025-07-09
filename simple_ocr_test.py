#!/usr/bin/env python3
"""
Simple OCR test to verify the functionality works
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from customer.ocr_service import PrescriptionOCRService

def test_basic_ocr():
    """Test basic OCR functionality"""
    print("Testing Basic OCR Functionality")
    print("=" * 50)
    
    ocr_service = PrescriptionOCRService()
    
    # Test simple text validation
    test_cases = [
        ("Paracetamol", "Paracetamol 500mg tablets"),
        ("Paracetamol", "Paracetam0l 500mg tablets"),  # 0 instead of o
        ("Paracetamol", "Para cetamol 500mg tablets"),  # Space error
        ("Ibuprofen", "Ibuprofen 400mg capsules"),
        ("Ibuprofen", "lbuprofen 400mg capsules"),  # l instead of I
        ("Amoxicillin", "Amoxicillin 500mg"),
        ("Amoxicillin", "Arnoxicillin 500mg"),  # A instead of A
    ]
    
    print("Testing OCR corrections and fuzzy matching:")
    for medicine, prescription_text in test_cases:
        result = ocr_service.validate_medicine_name(medicine, prescription_text)
        status = "✓ FOUND" if result['is_valid'] else "✗ NOT FOUND"
        confidence = result['confidence']
        print(f"  '{medicine}' in '{prescription_text}': {confidence:.1f}% - {status}")
    
    print("\nTesting OCR corrections:")
    test_text = "Paracetam0l 500mg tab1ets - Take 1 tab1et twice dai1y"
    corrected = ocr_service.apply_ocr_corrections(test_text)
    print(f"Original: {test_text}")
    print(f"Corrected: {corrected}")
    
    print("\nTesting medicine name extraction:")
    sample_prescriptions = [
        "Rx: Paracetamol 500mg tablets - Take 1 tablet twice daily",
        "1. Paracetamol 500mg - 1 tab BD\n2. Ibuprofen 400mg - 1 tab TDS",
        "PARACETAMOL 500MG TABLETS\nTAKE ONE TABLET TWICE DAILY"
    ]
    
    for i, prescription in enumerate(sample_prescriptions):
        print(f"\nSample {i+1}: {prescription}")
        medicines = ocr_service.extract_medicine_names(prescription)
        print(f"Extracted medicines: {medicines}")
        
        # Test validation
        for med in ["Paracetamol", "Ibuprofen", "Aspirin"]:
            confidence = ocr_service.get_medicine_confidence(med, prescription)
            status = "✓" if confidence >= 60 else "✗"
            print(f"  {med}: {confidence:.1f}% {status}")

if __name__ == "__main__":
    test_basic_ocr()