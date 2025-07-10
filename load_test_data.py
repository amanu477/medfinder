#!/usr/bin/env python
"""
Load test data for the Ethiopian Pharmacy Platform
Creates sample users, pharmacies, medicines, and test data
"""
import os
import sys
import django
from django.conf import settings

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from customer.models import Customer
from pharmacy.models import Pharmacy, Medicine
from delivery.models import DeliveryPerson
from moh.models import MoHOfficer
import logging

logger = logging.getLogger(__name__)

def create_test_pharmacies():
    """Create test pharmacies with location data"""
    pharmacies_data = [
        {
            'name': 'Addis Pharmacy',
            'address': 'Bole Road, Addis Ababa',
            'phone': '+251911234567',
            'email': 'addis@pharmacy.com',
            'latitude': 9.0317,
            'longitude': 38.7614,
            'is_active': True,
            'is_verified': True,
        },
        {
            'name': 'Merkato Health Center',
            'address': 'Merkato, Addis Ababa',
            'phone': '+251911234568',
            'email': 'merkato@pharmacy.com',
            'latitude': 9.0145,
            'longitude': 38.7422,
            'is_active': True,
            'is_verified': True,
        },
        {
            'name': 'Piazza Medical Store',
            'address': 'Piazza, Addis Ababa',
            'phone': '+251911234569',
            'email': 'piazza@pharmacy.com',
            'latitude': 9.0355,
            'longitude': 38.7635,
            'is_active': True,
            'is_verified': True,
        },
        {
            'name': 'Gerji Pharmacy',
            'address': 'Gerji, Addis Ababa',
            'phone': '+251911234570',
            'email': 'gerji@pharmacy.com',
            'latitude': 9.0765,
            'longitude': 38.7918,
            'is_active': True,
            'is_verified': True,
        },
        {
            'name': 'Kazanchis Health Pharmacy',
            'address': 'Kazanchis, Addis Ababa',
            'phone': '+251911234571',
            'email': 'kazanchis@pharmacy.com',
            'latitude': 9.0265,
            'longitude': 38.7515,
            'is_active': True,
            'is_verified': True,
        },
    ]
    
    for pharmacy_data in pharmacies_data:
        # Create user for pharmacy
        username = pharmacy_data['name'].lower().replace(' ', '_')
        try:
            user = User.objects.create_user(
                username=username,
                email=pharmacy_data['email'],
                password='pharmacy123',
                first_name=pharmacy_data['name'],
                last_name='Pharmacy'
            )
            
            # Create pharmacy
            pharmacy = Pharmacy.objects.create(
                user=user,
                name=pharmacy_data['name'],
                address=pharmacy_data['address'],
                phone=pharmacy_data['phone'],
                email=pharmacy_data['email'],
                latitude=pharmacy_data['latitude'],
                longitude=pharmacy_data['longitude'],
                is_active=pharmacy_data['is_active'],
                verification_status='verified'
            )
            
            print(f"Created pharmacy: {pharmacy.name}")
            
            # Create medicines for this pharmacy
            create_medicines_for_pharmacy(pharmacy)
            
        except Exception as e:
            print(f"Error creating pharmacy {pharmacy_data['name']}: {e}")

def create_medicines_for_pharmacy(pharmacy):
    """Create sample medicines for a pharmacy"""
    medicines_data = [
        {
            'name': 'Paracetamol 500mg',
            'description': 'Pain reliever and fever reducer',
            'price': 25.00,
            'stock_quantity': 100,
            'prescription_required': False,
        },
        {
            'name': 'Amoxicillin 500mg',
            'description': 'Antibiotic for bacterial infections',
            'price': 45.00,
            'stock_quantity': 50,
            'prescription_required': True,
        },
        {
            'name': 'Ibuprofen 400mg',
            'description': 'Anti-inflammatory and pain reliever',
            'price': 30.00,
            'stock_quantity': 75,
            'prescription_required': False,
        },
        {
            'name': 'Metformin 500mg',
            'description': 'Diabetes medication',
            'price': 60.00,
            'stock_quantity': 40,
            'prescription_required': True,
        },
        {
            'name': 'Cetirizine 10mg',
            'description': 'Allergy medication',
            'price': 20.00,
            'stock_quantity': 80,
            'prescription_required': False,
        },
        {
            'name': 'Omeprazole 20mg',
            'description': 'Stomach acid reducer',
            'price': 35.00,
            'stock_quantity': 60,
            'prescription_required': True,
        },
        {
            'name': 'Vitamin D3 1000IU',
            'description': 'Vitamin supplement',
            'price': 40.00,
            'stock_quantity': 90,
            'prescription_required': False,
        },
        {
            'name': 'Aspirin 81mg',
            'description': 'Blood thinner and pain reliever',
            'price': 15.00,
            'stock_quantity': 120,
            'prescription_required': False,
        },
    ]
    
    for medicine_data in medicines_data:
        try:
            medicine = Medicine.objects.create(
                pharmacy=pharmacy,
                name=medicine_data['name'],
                description=medicine_data['description'],
                price=medicine_data['price'],
                stock_quantity=medicine_data['stock_quantity'],
                prescription_required=medicine_data['prescription_required'],
                is_available=True
            )
            print(f"  Created medicine: {medicine.name}")
        except Exception as e:
            print(f"  Error creating medicine {medicine_data['name']}: {e}")

def create_test_customer():
    """Create test customer"""
    try:
        user = User.objects.create_user(
            username='testcustomer',
            email='customer@test.com',
            password='customer123',
            first_name='Test',
            last_name='Customer'
        )
        
        customer = Customer.objects.create(
            user=user,
            name='Test Customer',
            email='customer@test.com',
            phone='+251911111111',
            address='Test Address, Addis Ababa',
            latitude=9.0317,
            longitude=38.7614
        )
        
        print(f"Created customer: {customer.name}")
        
    except Exception as e:
        print(f"Error creating customer: {e}")

def create_test_delivery_person():
    """Create test delivery person"""
    try:
        user = User.objects.create_user(
            username='testdelivery',
            email='delivery@test.com',
            password='delivery123',
            first_name='Test',
            last_name='Delivery'
        )
        
        # Get the first pharmacy to associate with delivery person
        pharmacy = Pharmacy.objects.first()
        
        delivery_person = DeliveryPerson.objects.create(
            user=user,
            pharmacy=pharmacy,
            employee_id='EMP001',
            phone='+251922222222',
            national_id='ID12345',
            vehicle_type='motorcycle',
            vehicle_plate='AA-12345',
            is_active=True
        )
        
        print(f"Created delivery person: {delivery_person.user.get_full_name()}")
        
    except Exception as e:
        print(f"Error creating delivery person: {e}")

def create_test_moh_officer():
    """Create test MoH officer"""
    try:
        user = User.objects.create_user(
            username='testmoh',
            email='moh@test.com',
            password='moh123',
            first_name='Test',
            last_name='MoH Officer'
        )
        
        moh_officer = MoHOfficer.objects.create(
            user=user,
            officer_id='MOH001',
            department='Pharmacy Regulation',
            phone='+251933333333',
            is_active=True
        )
        
        print(f"Created MoH officer: {moh_officer.user.get_full_name()}")
        
    except Exception as e:
        print(f"Error creating MoH officer: {e}")

def main():
    """Main function to create all test data"""
    print("Loading test data for Ethiopian Pharmacy Platform...")
    
    try:
        with transaction.atomic():
            print("\nCreating test pharmacies...")
            create_test_pharmacies()
            
            print("\nCreating test customer...")
            create_test_customer()
            
            print("\nCreating test delivery person...")
            create_test_delivery_person()
            
            print("\nCreating test MoH officer...")
            create_test_moh_officer()
            
            print("\n✅ Test data loaded successfully!")
            print("\nTest login credentials:")
            print("- Customer: testcustomer / customer123")
            print("- Pharmacy: addis_pharmacy / pharmacy123")
            print("- Delivery: testdelivery / delivery123")
            print("- MoH Officer: testmoh / moh123")
            
    except Exception as e:
        print(f"❌ Error loading test data: {e}")
        raise

if __name__ == "__main__":
    main()