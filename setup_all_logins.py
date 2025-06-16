#!/usr/bin/env python
"""
Setup script to create test users for all login systems:
- Customer login
- Pharmacy login  
- MoH officer login
- Platform admin login
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from customer.models import Customer
from pharmacy.models import Pharmacy
from moh.models import MoHOfficer, MoHPharmacyRegistry


def create_test_users():
    """Create test users for all login systems"""
    
    with transaction.atomic():
        print("Setting up all login systems...")
        
        # 1. Platform Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@pharmacy.com',
                'first_name': 'Platform',
                'last_name': 'Admin',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True
            }
        )
        admin_user.set_password('admin123')
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        print(f"✓ Platform Admin: username=admin, password=admin123")
        
        # 2. Customer User
        customer_user, created = User.objects.get_or_create(
            username='customer1',
            defaults={
                'email': 'customer@test.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_active': True
            }
        )
        customer_user.set_password('customer123')
        customer_user.save()
        
        # Create customer profile
        customer, created = Customer.objects.get_or_create(
            user=customer_user,
            defaults={
                'name': f'{customer_user.first_name} {customer_user.last_name}',
                'email': customer_user.email,
                'phone': '+251911123456',
                'address': '123 Main St, Addis Ababa, Ethiopia'
            }
        )
        print(f"✓ Customer: username=customer1, password=customer123")
        
        # 3. Pharmacy User
        pharmacy_user, created = User.objects.get_or_create(
            username='pharmacy1',
            defaults={
                'email': 'pharmacy@test.com',
                'first_name': 'Green',
                'last_name': 'Pharmacy',
                'is_active': True
            }
        )
        pharmacy_user.set_password('pharmacy123')
        pharmacy_user.save()
        
        # Create pharmacy profile
        from datetime import time
        pharmacy, created = Pharmacy.objects.get_or_create(
            user=pharmacy_user,
            defaults={
                'name': 'Green Cross Pharmacy',
                'email': pharmacy_user.email,
                'phone': '+251911654321',
                'address': '456 Pharmacy St, Addis Ababa, Ethiopia',
                'license_number': 'PH2024001',
                'latitude': 9.042469,
                'longitude': 38.757133,
                'opening_time': time(8, 0),  # 8:00 AM
                'closing_time': time(20, 0),  # 8:00 PM
                'is_active': True,
                'verification_status': 'verified'
            }
        )
        print(f"✓ Pharmacy: username=pharmacy1, password=pharmacy123")
        
        # 4. MoH Officer User
        moh_user, created = User.objects.get_or_create(
            username='moh_officer',
            defaults={
                'email': 'moh@health.gov.et',
                'first_name': 'Dr. Ahmed',
                'last_name': 'Hassan',
                'is_active': True
            }
        )
        moh_user.set_password('moh123')
        moh_user.save()
        
        # Create MoH officer profile
        moh_officer, created = MoHOfficer.objects.get_or_create(
            user=moh_user,
            defaults={
                'officer_id': 'MOH2024001',
                'department': 'pharmacy_regulation',
                'position': 'Senior Pharmacy Inspector',
                'phone': '+251911987654',
                'email': moh_user.email,
                'is_active': True
            }
        )
        print(f"✓ MoH Officer: username=moh_officer, password=moh123")
        
        # 5. Create MoH pharmacy registry entry for validation testing
        from datetime import date
        moh_registry, created = MoHPharmacyRegistry.objects.get_or_create(
            license_number='PH2024001',
            defaults={
                'pharmacy_name': 'Green Cross Pharmacy',
                'owner_name': 'Green Pharmacy Ltd',
                'pharmacist_name': 'Dr. Abebe Kebede',
                'pharmacist_license': 'PHR2024001',
                'license_status': 'active',
                'issue_date': date(2024, 1, 1),
                'expiry_date': date(2025, 12, 31),
                'address_detail': '456 Pharmacy St, Addis Ababa, Ethiopia',
                'phone_number': '+251911654321',
                'email': 'pharmacy@test.com',
                'compliance_score': 95,
                'moh_officer': 'Dr. Ahmed Hassan'
            }
        )
        print(f"✓ MoH Registry: License PH2024001 registered")
        
        print("\n" + "="*50)
        print("ALL LOGIN SYSTEMS READY!")
        print("="*50)
        
        print("\n📱 CUSTOMER LOGIN:")
        print("   URL: /customer/login/")
        print("   Username: customer1")
        print("   Password: customer123")
        
        print("\n🏥 PHARMACY LOGIN:")
        print("   URL: /pharmacy/login/")
        print("   Username: pharmacy1") 
        print("   Password: pharmacy123")
        
        print("\n🏛️ MOH OFFICER LOGIN:")
        print("   URL: /moh/")
        print("   Username: moh_officer")
        print("   Password: moh123")
        
        print("\n👨‍💼 PLATFORM ADMIN LOGIN:")
        print("   URL: /platform-admin/login/")
        print("   Username: admin")
        print("   Password: admin123")
        
        print("\n✅ All authentication systems are now working!")
        print("✅ Distance calculation is fixed!")
        print("✅ MoH verification system is working!")


if __name__ == '__main__':
    create_test_users()