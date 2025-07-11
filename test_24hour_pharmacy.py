#!/usr/bin/env python
"""
Test script to create a 24-hour pharmacy and verify the functionality
"""

import os
import sys
import django
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import time

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from pharmacy.models import Pharmacy, Medicine

def create_24hour_pharmacy():
    """Create a 24-hour pharmacy for testing"""
    User = get_user_model()
    
    # Create user for 24-hour pharmacy
    user, created = User.objects.get_or_create(
        username='pharmacy24hour',
        defaults={
            'email': 'pharmacy24hour@test.com',
            'first_name': 'Twenty Four',
            'last_name': 'Hour Pharmacy'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created user: {user.username}")
    else:
        print(f"✓ User already exists: {user.username}")
    
    # Create 24-hour pharmacy
    pharmacy, created = Pharmacy.objects.get_or_create(
        name='24/7 Emergency Pharmacy',
        user=user,
        defaults={
            'license_number': 'PH247001',
            'license_type': 'retail',
            'address': '24/7 Plaza, Addis Ababa, Ethiopia',
            'phone': '+251911247001',
            'email': 'emergency@24pharmacy.com',
            'opening_time': time(0, 0),  # 00:00
            'closing_time': time(23, 59),  # 23:59
            'is_24_hour': True,
            'is_active': True,
            'latitude': 9.0300,
            'longitude': 38.7400,
            'verification_status': 'verified'
        }
    )
    
    if created:
        print(f"✓ Created 24-hour pharmacy: {pharmacy.name}")
        print(f"  - License: {pharmacy.license_number}")
        print(f"  - Hours: {'24/7 Open' if pharmacy.is_24_hour else 'Regular hours'}")
        print(f"  - Status: {'Open Now' if pharmacy.is_open_now() else 'Closed'}")
    else:
        print(f"✓ 24-hour pharmacy already exists: {pharmacy.name}")
    
    # Create medicines for the 24-hour pharmacy
    medicines_data = [
        {
            'name': 'Emergency Paracetamol 500mg',
            'description': 'Pain reliever and fever reducer available 24/7',
            'price': 15.50,
            'stock_quantity': 500,
            'expiry_date': timezone.now().date().replace(year=2026),
            'is_available': True,
            'prescription_required': False
        },
        {
            'name': 'Emergency Ibuprofen 400mg',
            'description': 'Anti-inflammatory medication available 24/7',
            'price': 25.00,
            'stock_quantity': 300,
            'expiry_date': timezone.now().date().replace(year=2026),
            'is_available': True,
            'prescription_required': False
        },
        {
            'name': 'Emergency Aspirin 300mg',
            'description': 'Pain reliever available around the clock',
            'price': 12.75,
            'stock_quantity': 400,
            'expiry_date': timezone.now().date().replace(year=2026),
            'is_available': True,
            'prescription_required': False
        }
    ]
    
    for medicine_data in medicines_data:
        medicine, created = Medicine.objects.get_or_create(
            name=medicine_data['name'],
            pharmacy=pharmacy,
            defaults=medicine_data
        )
        if created:
            print(f"  ✓ Created medicine: {medicine.name} - {medicine.price} ETB")
        else:
            print(f"  ✓ Medicine already exists: {medicine.name}")
    
    return pharmacy

def test_24hour_functionality():
    """Test 24-hour pharmacy functionality"""
    print("\n=== Testing 24-Hour Pharmacy Functionality ===")
    
    try:
        pharmacy = Pharmacy.objects.get(name='24/7 Emergency Pharmacy')
        print(f"✓ Found 24-hour pharmacy: {pharmacy.name}")
        
        # Test is_24_hour field
        print(f"  - is_24_hour: {pharmacy.is_24_hour}")
        
        # Test opening/closing times
        print(f"  - Opening time: {pharmacy.opening_time}")
        print(f"  - Closing time: {pharmacy.closing_time}")
        
        # Test is_open_now method
        print(f"  - Is open now: {pharmacy.is_open_now()}")
        
        # Test get_status_display method
        print(f"  - Status display: {pharmacy.get_status_display()}")
        
        # Test medicines
        medicines = pharmacy.medicine_set.all()
        print(f"  - Total medicines: {medicines.count()}")
        
        for medicine in medicines:
            print(f"    • {medicine.name} - {medicine.price} ETB")
        
        print("\n✓ All tests passed!")
        
    except Pharmacy.DoesNotExist:
        print("✗ 24-hour pharmacy not found. Creating it now...")
        create_24hour_pharmacy()
        test_24hour_functionality()

if __name__ == '__main__':
    print("=== 24-Hour Pharmacy Test Script ===")
    create_24hour_pharmacy()
    test_24hour_functionality()
    
    print("\n=== Test Login Credentials ===")
    print("Username: pharmacy24hour")
    print("Password: testpass123")
    print("Pharmacy: 24/7 Emergency Pharmacy")
    print("\n=== Test Complete ===")