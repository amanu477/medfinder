#!/usr/bin/env python3
"""
Comprehensive data loading script for Ethiopian Pharmacy Platform
This script loads all necessary data including users, pharmacies, medicines, and test records
"""

import os
import sys
import django
from django.db import transaction

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from customer.models import Customer, Order, OrderItem, Prescription, IncidentReport
from pharmacy.models import Pharmacy, Medicine
from moh.models import MoHPharmacyRegistry, MoHOfficer
# from platform_admin.models import AdminNotification

def clear_all_data():
    """Clear all existing data to start fresh"""
    print("Clearing existing data...")
    
    # Clear in reverse dependency order
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Prescription.objects.all().delete()
    Medicine.objects.all().delete()
    IncidentReport.objects.all().delete()
    # AdminNotification.objects.all().delete()
    
    # Clear user-related data
    Customer.objects.all().delete()
    Pharmacy.objects.all().delete()
    MoHOfficer.objects.all().delete()
    
    # Clear users (except superuser)
    User.objects.filter(is_superuser=False).delete()
    
    print("✓ All data cleared successfully")

def create_test_users():
    """Create test users for all systems"""
    print("\nCreating test users...")
    
    # 1. Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@pharmacy.et',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✓ Admin user created: admin/admin123")
    
    # 2. Create customer users
    customers_data = [
        {'username': 'customer', 'email': 'customer@test.et', 'name': 'Alemayehu Tadesse', 'phone': '+251911234567', 'address': 'Addis Ababa, Ethiopia'},
        {'username': 'customer2', 'email': 'customer2@test.et', 'name': 'Meron Haile', 'phone': '+251912345678', 'address': 'Bahir Dar, Ethiopia'},
        {'username': 'customer3', 'email': 'customer3@test.et', 'name': 'Dawit Bekele', 'phone': '+251913456789', 'address': 'Dire Dawa, Ethiopia'},
    ]
    
    for customer_data in customers_data:
        user, created = User.objects.get_or_create(
            username=customer_data['username'],
            defaults={
                'email': customer_data['email'],
                'first_name': customer_data['name'].split()[0],
                'last_name': customer_data['name'].split()[1],
            }
        )
        if created:
            user.set_password('customer123')
            user.save()
            
            Customer.objects.create(
                user=user,
                name=customer_data['name'],
                email=customer_data['email'],
                phone=customer_data['phone'],
                address=customer_data['address']
            )
            print(f"✓ Customer created: {customer_data['username']}/customer123")
    
    # 3. Create MoH officer
    moh_user, created = User.objects.get_or_create(
        username='moh_officer',
        defaults={
            'email': 'moh.officer@moh.gov.et',
            'first_name': 'Ministry',
            'last_name': 'Officer',
            'is_staff': True
        }
    )
    if created:
        moh_user.set_password('moh123')
        moh_user.save()
        
        MoHOfficer.objects.create(
            user=moh_user,
            officer_id='MOH-001',
            department='licensing',
            position='Senior Inspector',
            phone='+251115551234',
            email='moh.officer@moh.gov.et',
            is_active=True
        )
        print("✓ MoH Officer created: moh_officer/moh123")
    
    # 4. Create pharmacy users
    pharmacies_data = [
        {
            'username': 'pharmacy',
            'email': 'contact@addispharmacy.et',
            'name': 'Addis Pharmacy',
            'license_number': 'MOH-AA-001',
            'address': 'Merkato, Addis Ababa',
            'phone': '+251111234567',
            'latitude': 9.0307,
            'longitude': 38.7578
        },
        {
            'username': 'pharmacy2',
            'email': 'info@oromiahealth.et',
            'name': 'Oromia Health Pharmacy',
            'license_number': 'MOH-OR-002',
            'address': 'Jimma, Oromia',
            'phone': '+251112345678',
            'latitude': 7.6699,
            'longitude': 36.8341
        },
        {
            'username': 'pharmacy3',
            'email': 'support@amharamedical.et',
            'name': 'Amhara Medical Center',
            'license_number': 'MOH-AM-003',
            'address': 'Bahir Dar, Amhara',
            'phone': '+251113456789',
            'latitude': 11.5922,
            'longitude': 37.3914
        }
    ]
    
    for pharmacy_data in pharmacies_data:
        user, created = User.objects.get_or_create(
            username=pharmacy_data['username'],
            defaults={
                'email': pharmacy_data['email'],
                'first_name': pharmacy_data['name'].split()[0],
                'last_name': 'Pharmacy',
                'is_staff': False
            }
        )
        if created:
            user.set_password('pharmacy123')
            user.save()
            
            from datetime import time
            Pharmacy.objects.create(
                user=user,
                name=pharmacy_data['name'],
                license_number=pharmacy_data['license_number'],
                address=pharmacy_data['address'],
                phone=pharmacy_data['phone'],
                email=pharmacy_data['email'],
                latitude=pharmacy_data['latitude'],
                longitude=pharmacy_data['longitude'],
                opening_time=time(8, 0),  # 8:00 AM
                closing_time=time(20, 0),  # 8:00 PM
                is_active=True,
                verification_status='verified'
            )
            print(f"✓ Pharmacy created: {pharmacy_data['username']}/pharmacy123")

def create_medicines():
    """Create sample medicines for pharmacies"""
    print("\nCreating medicines...")
    
    from datetime import date, timedelta
    import random
    
    medicines_data = [
        # Common medicines
        {'name': 'Paracetamol 500mg', 'price': 25.00, 'prescription_required': False},
        {'name': 'Amoxicillin 500mg', 'price': 45.00, 'prescription_required': True},
        {'name': 'Ibuprofen 400mg', 'price': 30.00, 'prescription_required': False},
        {'name': 'Cetirizine 10mg', 'price': 35.00, 'prescription_required': False},
        {'name': 'Omeprazole 20mg', 'price': 55.00, 'prescription_required': True},
        {'name': 'Metformin 500mg', 'price': 40.00, 'prescription_required': True},
        {'name': 'Aspirin 100mg', 'price': 20.00, 'prescription_required': False},
        {'name': 'Ciprofloxacin 500mg', 'price': 65.00, 'prescription_required': True},
        {'name': 'Loratadine 10mg', 'price': 32.00, 'prescription_required': False},
        {'name': 'Dexamethasone 0.5mg', 'price': 28.00, 'prescription_required': True},
        {'name': 'Vitamins B-Complex', 'price': 48.00, 'prescription_required': False},
        {'name': 'Iron Tablets', 'price': 35.00, 'prescription_required': False},
        {'name': 'Cough Syrup', 'price': 42.00, 'prescription_required': False},
        {'name': 'Antacid Tablets', 'price': 25.00, 'prescription_required': False},
        {'name': 'Multivitamin', 'price': 55.00, 'prescription_required': False},
    ]
    
    pharmacies = Pharmacy.objects.all()
    
    for medicine_data in medicines_data:
        for pharmacy in pharmacies:
            # Create medicine with random stock quantity (10-100)
            stock_quantity = random.randint(10, 100)
            # Random expiry date between 6 months and 2 years from now
            expiry_date = date.today() + timedelta(days=random.randint(180, 730))
            
            Medicine.objects.create(
                name=medicine_data['name'],
                price=medicine_data['price'],
                pharmacy=pharmacy,
                stock_quantity=stock_quantity,
                description=f"High quality {medicine_data['name']} available at {pharmacy.name}",
                prescription_required=medicine_data['prescription_required'],
                expiry_date=expiry_date,
                is_available=True
            )
    
    print(f"✓ Created {len(medicines_data)} medicines for each pharmacy")

def create_sample_orders():
    """Create sample orders and prescriptions"""
    print("\nCreating sample orders...")
    
    customers = Customer.objects.all()
    pharmacies = Pharmacy.objects.all()
    
    for customer in customers:
        for i, pharmacy in enumerate(pharmacies):
            if i < 2:  # Create 2 orders per customer
                # Create order
                order = Order.objects.create(
                    customer=customer,
                    pharmacy=pharmacy,
                    status='pending',
                    total_amount=0,
                    notes=f"Sample order from {customer.name}"
                )
                
                # Add order items
                medicines = Medicine.objects.filter(pharmacy=pharmacy)[:3]  # Get first 3 medicines
                total_amount = 0
                
                for medicine in medicines:
                    quantity = 2
                    OrderItem.objects.create(
                        order=order,
                        medicine=medicine,
                        quantity=quantity,
                        price=medicine.price
                    )
                    total_amount += medicine.price * quantity
                
                order.total_amount = total_amount
                order.save()
    
    print("✓ Created sample orders")

def create_sample_prescriptions():
    """Create sample prescriptions"""
    print("\nCreating sample prescriptions...")
    
    customers = Customer.objects.all()
    pharmacies = Pharmacy.objects.all()
    
    for customer in customers:
        for i, pharmacy in enumerate(pharmacies):
            if i < 1:  # Create 1 prescription per customer
                Prescription.objects.create(
                    customer_name=customer.name,
                    customer_email=customer.email,
                    customer_phone=customer.phone,
                    pharmacy=pharmacy,
                    notes=f"Sample prescription from {customer.name}",
                    status='pending'
                )
    
    print("✓ Created sample prescriptions")

def main():
    """Main function to load all data"""
    print("=" * 60)
    print("Ethiopian Pharmacy Platform - Data Loading Script")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # Clear existing data
            clear_all_data()
            
            # Create all test data
            create_test_users()
            create_medicines()
            create_sample_orders()
            create_sample_prescriptions()
            
            print("\n" + "=" * 60)
            print("✓ ALL DATA LOADED SUCCESSFULLY!")
            print("=" * 60)
            
            print("\nLogin Credentials:")
            print("- Admin: admin/admin123")
            print("- Customer: customer/customer123, customer2/customer123, customer3/customer123")
            print("- Pharmacy: pharmacy/pharmacy123, pharmacy2/pharmacy123, pharmacy3/pharmacy123")
            print("- MoH Officer: moh_officer/moh123")
            
            print(f"\nData Summary:")
            print(f"- Users: {User.objects.count()}")
            print(f"- Customers: {Customer.objects.count()}")
            print(f"- Pharmacies: {Pharmacy.objects.count()}")
            print(f"- MoH Officers: {MoHOfficer.objects.count()}")
            print(f"- Medicines: {Medicine.objects.count()}")
            print(f"- Orders: {Order.objects.count()}")
            print(f"- Prescriptions: {Prescription.objects.count()}")
            print(f"- MoH Records: {MoHPharmacyRegistry.objects.count()}")
            
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()