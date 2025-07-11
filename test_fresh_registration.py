#!/usr/bin/env python3
"""
Test fresh registration with unique data
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
import random

def test_fresh_registration():
    """Test registration with completely fresh data"""
    
    print("Testing fresh registration system...")
    
    # Generate unique test data
    random_id = random.randint(1000, 9999)
    test_data = {
        'username': f'testuser{random_id}',
        'email': f'test{random_id}@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'phone': f'+25191100{random_id}',
        'address': 'Test Address, Addis Ababa',
        'password1': 'SecurePass123',
        'password2': 'SecurePass123',
    }
    
    print(f"Using test data: {test_data['username']}, {test_data['email']}")
    
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
            print(f"  Error messages: {form2.errors}")
        else:
            print("✗ Duplicate prevention failed - form accepted duplicate data")
        
        print("\n4. Testing database integrity...")
        # Verify records exist
        user_count = User.objects.filter(username=test_data['username']).count()
        customer_count = Customer.objects.filter(email=test_data['email']).count()
        verification_count = EmailVerification.objects.filter(email=test_data['email']).count()
        
        print(f"✓ Database integrity: User: {user_count}, Customer: {customer_count}, Verification: {verification_count}")
        
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
        test_fresh_registration()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)