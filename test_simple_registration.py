#!/usr/bin/env python3
"""
Simple test to verify registration system works
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from customer.models import Customer, EmailVerification
from customer.forms import CustomerRegistrationForm

def test_registration_system():
    """Test the registration system works without database issues"""
    
    print("Testing registration system...")
    
    # Test data
    test_data = {
        'username': 'newuser456',
        'email': 'newuser@example.com',
        'first_name': 'New',
        'last_name': 'User',
        'phone': '+251911456789',
        'address': 'Test Address, Addis Ababa',
        'password1': 'SecurePass123',
        'password2': 'SecurePass123',
    }
    
    # Clean up any existing test data
    try:
        User.objects.filter(username='newuser456').delete()
        User.objects.filter(email='newuser@example.com').delete()
    except Exception as e:
        print(f"Note: cleanup had issues: {e}")
    
    print("\n1. Testing form validation...")
    form = CustomerRegistrationForm(test_data)
    if form.is_valid():
        print("✓ Form validation passed")
    else:
        print(f"✗ Form validation failed: {form.errors}")
        return False
    
    print("\n2. Testing user creation...")
    try:
        user = form.save()
        print(f"✓ User created: {user.username}")
        
        # Test customer creation
        customer = Customer.objects.create(
            user=user,
            name=f"{user.first_name} {user.last_name}",
            email=user.email,
            phone=test_data['phone'],
            address=test_data['address'],
            is_verified=False
        )
        print(f"✓ Customer profile created: {customer.name}")
        
        # Test email verification creation
        verification = EmailVerification.objects.create(
            email=user.email,
            verification_code='123456',
            user_type='customer'
        )
        print(f"✓ Email verification record created: {verification.verification_code}")
        
        print("\n3. Testing duplicate prevention...")
        # Try to create duplicate user
        form2 = CustomerRegistrationForm(test_data)
        if not form2.is_valid():
            print("✓ Duplicate prevention working - form rejected duplicate data")
        else:
            print("✗ Duplicate prevention failed - form accepted duplicate data")
        
        # Clean up
        user.delete()
        print("✓ Test data cleaned up")
        
        print("\n🎉 Registration system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Registration system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        test_registration_system()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)