#!/usr/bin/env python3
"""
Test script to verify duplicate email and username prevention
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from customer.models import Customer
from customer.forms import CustomerRegistrationForm

def test_duplicate_prevention():
    """Test that duplicate emails and usernames are properly prevented"""
    
    print("Testing duplicate prevention system...")
    
    # Test data
    test_data = {
        'username': 'testuser123',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'phone': '+251911123456',
        'address': 'Test Address, Addis Ababa',
        'password1': 'SecurePass456',
        'password2': 'SecurePass456',
    }
    
    # Clean up any existing test data
    User.objects.filter(username='testuser123').delete()
    User.objects.filter(email='test@example.com').delete()
    
    print("\n1. Testing initial registration (should succeed)...")
    
    # First registration - should succeed
    form1 = CustomerRegistrationForm(test_data)
    if form1.is_valid():
        user1 = form1.save()
        print(f"✓ First registration successful: {user1.username} - {user1.email}")
    else:
        print(f"✗ First registration failed: {form1.errors}")
        return False
    
    print("\n2. Testing duplicate username (should fail)...")
    
    # Try to register with same username but different email
    test_data_duplicate_username = test_data.copy()
    test_data_duplicate_username['email'] = 'different@example.com'
    
    form2 = CustomerRegistrationForm(test_data_duplicate_username)
    if form2.is_valid():
        print("✗ Duplicate username validation failed - form should be invalid")
        return False
    else:
        username_error = form2.errors.get('username', [])
        print(f"✓ Duplicate username properly rejected: {username_error}")
    
    print("\n3. Testing duplicate email (should fail)...")
    
    # Try to register with same email but different username
    test_data_duplicate_email = test_data.copy()
    test_data_duplicate_email['username'] = 'differentuser123'
    
    form3 = CustomerRegistrationForm(test_data_duplicate_email)
    if form3.is_valid():
        print("✗ Duplicate email validation failed - form should be invalid")
        return False
    else:
        email_error = form3.errors.get('email', [])
        print(f"✓ Duplicate email properly rejected: {email_error}")
    
    print("\n4. Testing both username and email duplicates (should fail)...")
    
    # Try to register with same username and email
    form4 = CustomerRegistrationForm(test_data)
    if form4.is_valid():
        print("✗ Duplicate username and email validation failed - form should be invalid")
        return False
    else:
        username_error = form4.errors.get('username', [])
        email_error = form4.errors.get('email', [])
        print(f"✓ Duplicate username and email properly rejected:")
        print(f"  Username error: {username_error}")
        print(f"  Email error: {email_error}")
    
    print("\n5. Testing new valid registration (should succeed)...")
    
    # Try to register with completely new data
    new_test_data = {
        'username': 'newuser123',
        'email': 'newuser@example.com',
        'first_name': 'New',
        'last_name': 'User',
        'phone': '+251911654321',
        'address': 'New Address, Addis Ababa',
        'password1': 'SecurePass789',
        'password2': 'SecurePass789',
    }
    
    form5 = CustomerRegistrationForm(new_test_data)
    if form5.is_valid():
        user2 = form5.save()
        print(f"✓ New registration successful: {user2.username} - {user2.email}")
    else:
        print(f"✗ New registration failed: {form5.errors}")
        return False
    
    print("\n6. Database verification...")
    
    # Verify users exist in database
    users = User.objects.filter(username__in=['testuser123', 'newuser123'])
    print(f"✓ Users in database: {list(users.values_list('username', 'email'))}")
    
    # Clean up test data
    User.objects.filter(username__in=['testuser123', 'newuser123']).delete()
    print("✓ Test data cleaned up")
    
    print("\n🎉 All duplicate prevention tests passed successfully!")
    return True

if __name__ == '__main__':
    try:
        test_duplicate_prevention()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)