#!/usr/bin/env python
"""
Setup test data for OCR enhancement system
"""

import os
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from customer.models import Customer
from pharmacy.models import Pharmacy, Medicine

def setup_test_data():
    """Create test data for OCR enhancement testing"""
    
    print("Setting up test data for OCR enhancement...")
    
    # Create test pharmacy user
    pharmacy_user, created = User.objects.get_or_create(
        username='testpharmacy',
        defaults={
            'email': 'pharmacy@test.com',
            'password': make_password('testpass123'),
            'first_name': 'Test',
            'last_name': 'Pharmacy'
        }
    )
    print(f"Pharmacy user created: {created}")
    
    # Create test pharmacy
    pharmacy, created = Pharmacy.objects.get_or_create(
        user=pharmacy_user,
        defaults={
            'name': 'Test Pharmacy',
            'license_number': 'TEST123',
            'license_type': 'commercial',
            'address': 'Test Address, Addis Ababa',
            'phone': '+251911234567',
            'email': 'pharmacy@test.com',
            'verification_status': 'verified',
            'is_24_hour': False,
            'opening_time': datetime.strptime('08:00', '%H:%M').time(),
            'closing_time': datetime.strptime('20:00', '%H:%M').time()
        }
    )
    print(f"Pharmacy created: {created}")
    
    # Create test customer user
    customer_user, created = User.objects.get_or_create(
        username='testcustomer',
        defaults={
            'email': 'customer@test.com',
            'password': make_password('testpass123'),
            'first_name': 'Test',
            'last_name': 'Customer'
        }
    )
    print(f"Customer user created: {created}")
    
    # Create test customer
    customer, created = Customer.objects.get_or_create(
        user=customer_user,
        defaults={
            'name': 'Test Customer',
            'phone': '+251911234568',
            'email': 'customer@test.com',
            'address': 'Customer Address, Addis Ababa'
        }
    )
    print(f"Customer created: {created}")
    
    # Create test medicines
    medicines_data = [
        {'name': 'Aspirin 500mg', 'description': 'Pain relief tablets', 'price': 25.00, 'stock_quantity': 100},
        {'name': 'Paracetamol 500mg', 'description': 'Pain and fever relief', 'price': 15.00, 'stock_quantity': 150},
        {'name': 'Ibuprofen 400mg', 'description': 'Anti-inflammatory tablets', 'price': 30.00, 'stock_quantity': 80},
        {'name': 'Amoxicillin 250mg', 'description': 'Antibiotic capsules', 'price': 45.00, 'stock_quantity': 60},
    ]
    
    for med_data in medicines_data:
        medicine, created = Medicine.objects.get_or_create(
            pharmacy=pharmacy,
            name=med_data['name'],
            defaults={
                'description': med_data['description'],
                'price': med_data['price'],
                'stock_quantity': med_data['stock_quantity'],
                'expiry_date': datetime.now().date() + timedelta(days=365),
                'is_available': True,
                'prescription_required': True
            }
        )
        print(f"Medicine {med_data['name']} created: {created}")
    
    print("\nTest data setup completed!")
    print(f"- Pharmacy: {pharmacy.name} (User: {pharmacy_user.username})")
    print(f"- Customer: {customer.name} (User: {customer_user.username})")
    print(f"- Medicines: {Medicine.objects.filter(pharmacy=pharmacy).count()}")
    
    return pharmacy, customer

if __name__ == '__main__':
    setup_test_data()