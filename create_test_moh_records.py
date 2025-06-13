#!/usr/bin/env python
"""
Script to create test MoH pharmacy records for license validation testing
"""
import os
import sys
import django
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from pharmacy.models import MoHPharmacyRecord

def create_test_moh_records():
    """Create test MoH pharmacy records"""
    
    test_pharmacies = [
        {
            'pharmacy_name': 'Addis Pharmacy',
            'license_number': 'MOH-AA-001',
            'owner_name': 'Alemayehu Tadesse',
            'pharmacist_name': 'Dr. Meron Gebru',
            'pharmacist_license': 'PHARM-001',
            'region': 'addis_ababa',
            'city': 'Addis Ababa',
            'woreda': 'Bole',
            'kebele': '03',
            'address_detail': 'Bole Road, Near Edna Mall',
            'license_type': 'retail',
            'issue_date': date(2023, 1, 15),
            'expiry_date': date(2025, 1, 15),
            'status': 'active',
            'phone_number': '+251911123456',
            'email': 'info@addispharmacy.com',
            'moh_officer': 'Dr. Hanna Mekonnen'
        },
        {
            'pharmacy_name': 'Oromia Health Pharmacy',
            'license_number': 'MOH-OR-002',
            'owner_name': 'Bekele Alemu',
            'pharmacist_name': 'Dr. Saron Haile',
            'pharmacist_license': 'PHARM-002',
            'region': 'oromia',
            'city': 'Adama',
            'woreda': 'Adama City',
            'kebele': '05',
            'address_detail': 'Main Street, Central Market Area',
            'license_type': 'retail',
            'issue_date': date(2023, 3, 10),
            'expiry_date': date(2025, 3, 10),
            'status': 'active',
            'phone_number': '+251922234567',
            'email': 'contact@oromiahealth.com',
            'moh_officer': 'Dr. Kassahun Berhanu'
        },
        {
            'pharmacy_name': 'Amhara Medical Center',
            'license_number': 'MOH-AM-003',
            'owner_name': 'Tigist Worku',
            'pharmacist_name': 'Dr. Dawit Fiseha',
            'pharmacist_license': 'PHARM-003',
            'region': 'amhara',
            'city': 'Bahir Dar',
            'woreda': 'Bahir Dar City',
            'kebele': '07',
            'address_detail': 'Blue Nile Avenue, Hospital District',
            'license_type': 'hospital',
            'issue_date': date(2022, 11, 20),
            'expiry_date': date(2024, 11, 20),
            'status': 'active',
            'phone_number': '+251933345678',
            'email': 'admin@amharamedical.com',
            'moh_officer': 'Dr. Mulugeta Assefa'
        },
        {
            'pharmacy_name': 'City Center Pharmacy',
            'license_number': 'MOH-AA-004',
            'owner_name': 'Rahel Tesfaye',
            'pharmacist_name': 'Dr. Yonas Bekele',
            'pharmacist_license': 'PHARM-004',
            'region': 'addis_ababa',
            'city': 'Addis Ababa',
            'woreda': 'Kirkos',
            'kebele': '01',
            'address_detail': 'Mexico Square, Commercial District',
            'license_type': 'retail',
            'issue_date': date(2023, 6, 5),
            'expiry_date': date(2025, 6, 5),
            'status': 'active',
            'phone_number': '+251944456789',
            'email': 'info@citycenterpharmacy.com',
            'moh_officer': 'Dr. Selamawit Tadesse'
        },
        {
            'pharmacy_name': 'Expired License Pharmacy',
            'license_number': 'MOH-EX-005',
            'owner_name': 'Test Owner',
            'pharmacist_name': 'Dr. Test Pharmacist',
            'pharmacist_license': 'PHARM-005',
            'region': 'addis_ababa',
            'city': 'Addis Ababa',
            'woreda': 'Test',
            'kebele': '00',
            'address_detail': 'Test Address',
            'license_type': 'retail',
            'issue_date': date(2022, 1, 1),
            'expiry_date': date(2023, 1, 1),  # Expired
            'status': 'expired',
            'phone_number': '+251900000000',
            'email': 'test@expired.com',
            'moh_officer': 'Dr. Test Officer'
        }
    ]
    
    created_count = 0
    for pharmacy_data in test_pharmacies:
        # Check if record already exists
        if not MoHPharmacyRecord.objects.filter(license_number=pharmacy_data['license_number']).exists():
            MoHPharmacyRecord.objects.create(**pharmacy_data)
            created_count += 1
            print(f"Created MoH record: {pharmacy_data['pharmacy_name']} ({pharmacy_data['license_number']})")
        else:
            print(f"Already exists: {pharmacy_data['pharmacy_name']} ({pharmacy_data['license_number']})")
    
    print(f"\nCreated {created_count} new MoH pharmacy records")
    print(f"Total MoH records: {MoHPharmacyRecord.objects.count()}")
    
    print("\n" + "="*50)
    print("TEST LICENSE NUMBERS FOR VALIDATION:")
    print("="*50)
    print("Valid licenses:")
    for pharmacy in test_pharmacies[:4]:  # First 4 are valid
        print(f"  {pharmacy['license_number']} - {pharmacy['pharmacy_name']}")
    print("\nInvalid/Expired licenses:")
    print(f"  {test_pharmacies[4]['license_number']} - {test_pharmacies[4]['pharmacy_name']} (EXPIRED)")
    print("\nNon-existent license (for testing):")
    print("  MOH-INVALID-999 - Should show 'not found' error")

if __name__ == '__main__':
    create_test_moh_records()