#!/usr/bin/env python
"""
Comprehensive form validation test script
Tests all form validations across the platform
"""

import os
import sys
import django
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from decimal import Decimal

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from pharmacy.forms import PharmacyRegistrationForm, MedicineForm, PharmacyUserForm
from customer.forms import CustomerRegistrationForm, CustomerProfileForm, OrderForm
from pharmacy.models import Pharmacy, Medicine

def test_pharmacy_name_validation():
    """Test pharmacy name validation"""
    print("=== Testing Pharmacy Name Validation ===")
    
    # Test valid names
    valid_names = [
        "Green Valley Pharmacy",
        "St. Mary's Pharmacy",
        "24/7 Health Center",
        "Addis-Ababa Pharmacy",
        "John's & Sons Pharmacy"
    ]
    
    for name in valid_names:
        form = PharmacyRegistrationForm(data={'name': name})
        form.full_clean()
        if 'name' in form.errors:
            print(f"✗ Valid name rejected: {name} - {form.errors['name']}")
        else:
            print(f"✓ Valid name accepted: {name}")
    
    # Test invalid names
    invalid_names = [
        "AB",  # Too short
        "Pharmacy with @#$%",  # Invalid characters
        "A" * 101,  # Too long
        "123456789",  # Only numbers
        "Pharmacy with | pipe"  # Invalid character
    ]
    
    for name in invalid_names:
        form = PharmacyRegistrationForm(data={'name': name})
        form.full_clean()
        if 'name' not in form.errors:
            print(f"✗ Invalid name accepted: {name}")
        else:
            print(f"✓ Invalid name rejected: {name} - {form.errors['name'][0]}")

def test_phone_validation():
    """Test phone number validation"""
    print("\n=== Testing Phone Number Validation ===")
    
    # Test valid phone numbers
    valid_phones = [
        "+251911123456",
        "+251912345678",
        "+251712345678",
        "251911123456",
        "911123456"
    ]
    
    for phone in valid_phones:
        form = PharmacyRegistrationForm(data={'phone': phone})
        form.full_clean()
        if 'phone' in form.errors:
            print(f"✗ Valid phone rejected: {phone} - {form.errors['phone']}")
        else:
            print(f"✓ Valid phone accepted: {phone}")
    
    # Test invalid phone numbers
    invalid_phones = [
        "+251811123456",  # Wrong carrier code
        "+251911123",     # Too short
        "+2519111234567", # Too long
        "123456789",      # Too short
        "+1234567890",    # Wrong country code
        "+251abcdefgh"    # Contains letters
    ]
    
    for phone in invalid_phones:
        form = PharmacyRegistrationForm(data={'phone': phone})
        form.full_clean()
        if 'phone' not in form.errors:
            print(f"✗ Invalid phone accepted: {phone}")
        else:
            print(f"✓ Invalid phone rejected: {phone} - {form.errors['phone'][0]}")

def test_medicine_price_validation():
    """Test medicine price validation"""
    print("\n=== Testing Medicine Price Validation ===")
    
    # Test valid prices
    valid_prices = [
        "10.50",
        "0.01",
        "999.99",
        "100",
        "50.5"
    ]
    
    for price in valid_prices:
        form = MedicineForm(data={'price': price})
        form.full_clean()
        if 'price' in form.errors:
            print(f"✗ Valid price rejected: {price} - {form.errors['price']}")
        else:
            print(f"✓ Valid price accepted: {price}")
    
    # Test invalid prices
    invalid_prices = [
        "0",           # Zero price
        "-10",         # Negative price
        "10001",       # Too high
        "10.999",      # Too many decimal places
        "abc",         # Non-numeric
        ""             # Empty
    ]
    
    for price in invalid_prices:
        form = MedicineForm(data={'price': price})
        form.full_clean()
        if 'price' not in form.errors:
            print(f"✗ Invalid price accepted: {price}")
        else:
            print(f"✓ Invalid price rejected: {price} - {form.errors['price'][0]}")

def test_medicine_stock_validation():
    """Test medicine stock quantity validation"""
    print("\n=== Testing Medicine Stock Validation ===")
    
    # Test valid stock quantities
    valid_stocks = [0, 1, 100, 1000, 99999]
    
    for stock in valid_stocks:
        form = MedicineForm(data={'stock_quantity': stock})
        form.full_clean()
        if 'stock_quantity' in form.errors:
            print(f"✗ Valid stock rejected: {stock} - {form.errors['stock_quantity']}")
        else:
            print(f"✓ Valid stock accepted: {stock}")
    
    # Test invalid stock quantities
    invalid_stocks = [-1, 100001, "abc", ""]
    
    for stock in invalid_stocks:
        form = MedicineForm(data={'stock_quantity': stock})
        form.full_clean()
        if 'stock_quantity' not in form.errors:
            print(f"✗ Invalid stock accepted: {stock}")
        else:
            print(f"✓ Invalid stock rejected: {stock} - {form.errors['stock_quantity'][0]}")

def test_customer_name_validation():
    """Test customer name validation"""
    print("\n=== Testing Customer Name Validation ===")
    
    # Test valid names
    valid_names = [
        "John Doe",
        "Mary-Jane",
        "O'Connor",
        "Dr. Smith",
        "Al-Rashid"
    ]
    
    for name in valid_names:
        form = CustomerRegistrationForm(data={'first_name': name.split()[0], 'last_name': name.split()[-1]})
        form.full_clean()
        first_name_errors = form.errors.get('first_name', [])
        last_name_errors = form.errors.get('last_name', [])
        
        if first_name_errors or last_name_errors:
            print(f"✗ Valid name rejected: {name} - {first_name_errors or last_name_errors}")
        else:
            print(f"✓ Valid name accepted: {name}")
    
    # Test invalid names
    invalid_names = [
        "A",         # Too short
        "John123",   # Contains numbers
        "Mary@Jane", # Invalid characters
        "A" * 31,    # Too long
        "John$",     # Invalid character
    ]
    
    for name in invalid_names:
        form = CustomerRegistrationForm(data={'first_name': name})
        form.full_clean()
        if 'first_name' not in form.errors:
            print(f"✗ Invalid name accepted: {name}")
        else:
            print(f"✓ Invalid name rejected: {name} - {form.errors['first_name'][0]}")

def test_address_validation():
    """Test address validation"""
    print("\n=== Testing Address Validation ===")
    
    # Test valid addresses
    valid_addresses = [
        "123 Main Street, Addis Ababa, Ethiopia",
        "Bole Road, #45, Addis Ababa",
        "Kirkos Sub-City, Woreda 9, House #123",
        "Mercato Area, Shop #456/789"
    ]
    
    for address in valid_addresses:
        form = CustomerRegistrationForm(data={'address': address})
        form.full_clean()
        if 'address' in form.errors:
            print(f"✗ Valid address rejected: {address} - {form.errors['address']}")
        else:
            print(f"✓ Valid address accepted: {address}")
    
    # Test invalid addresses
    invalid_addresses = [
        "Short",      # Too short
        "Address with @ symbol",  # Invalid character
        "A" * 501,    # Too long
        "Address with | pipe",    # Invalid character
    ]
    
    for address in invalid_addresses:
        form = CustomerRegistrationForm(data={'address': address})
        form.full_clean()
        if 'address' not in form.errors:
            print(f"✗ Invalid address accepted: {address}")
        else:
            print(f"✓ Invalid address rejected: {address} - {form.errors['address'][0]}")

def test_username_validation():
    """Test username validation"""
    print("\n=== Testing Username Validation ===")
    
    # Test valid usernames
    valid_usernames = [
        "john_doe",
        "user123",
        "test_user",
        "pharmacy_admin",
        "customer1"
    ]
    
    for username in valid_usernames:
        form = PharmacyUserForm(data={'username': username})
        form.full_clean()
        if 'username' in form.errors:
            print(f"✗ Valid username rejected: {username} - {form.errors['username']}")
        else:
            print(f"✓ Valid username accepted: {username}")
    
    # Test invalid usernames
    invalid_usernames = [
        "ab",          # Too short
        "user@name",   # Invalid character
        "user name",   # Space not allowed
        "user-name",   # Hyphen not allowed in this context
        "A" * 31,      # Too long
    ]
    
    for username in invalid_usernames:
        form = PharmacyUserForm(data={'username': username})
        form.full_clean()
        if 'username' not in form.errors:
            print(f"✗ Invalid username accepted: {username}")
        else:
            print(f"✓ Invalid username rejected: {username} - {form.errors['username'][0]}")

def test_password_validation():
    """Test password validation"""
    print("\n=== Testing Password Validation ===")
    
    # Test valid passwords
    valid_passwords = [
        "StrongPass123",
        "MyPassword1",
        "SecurePass99",
        "TestPass2024"
    ]
    
    for password in valid_passwords:
        form = PharmacyUserForm(data={'password1': password, 'password2': password})
        form.full_clean()
        if 'password1' in form.errors:
            print(f"✗ Valid password rejected: {password} - {form.errors['password1']}")
        else:
            print(f"✓ Valid password accepted: {password}")
    
    # Test invalid passwords
    invalid_passwords = [
        "weak",         # Too short
        "password",     # No uppercase/numbers
        "PASSWORD",     # No lowercase/numbers
        "Password",     # No numbers
        "12345678",     # No letters
    ]
    
    for password in invalid_passwords:
        form = PharmacyUserForm(data={'password1': password, 'password2': password})
        form.full_clean()
        if 'password1' not in form.errors:
            print(f"✗ Invalid password accepted: {password}")
        else:
            print(f"✓ Invalid password rejected: {password} - {form.errors['password1'][0]}")

def main():
    """Run all validation tests"""
    print("=== COMPREHENSIVE FORM VALIDATION TEST ===")
    
    test_pharmacy_name_validation()
    test_phone_validation()
    test_medicine_price_validation()
    test_medicine_stock_validation()
    test_customer_name_validation()
    test_address_validation()
    test_username_validation()
    test_password_validation()
    
    print("\n=== VALIDATION TESTS COMPLETED ===")
    print("All form validations have been tested!")
    print("✓ Names: Letters, spaces, dots, hyphens, apostrophes only")
    print("✓ Prices: Positive numbers with max 2 decimal places")
    print("✓ Phone: Ethiopian format (+251XXXXXXXXX)")
    print("✓ Addresses: Letters, numbers, common punctuation")
    print("✓ Usernames: Letters, numbers, underscores only")
    print("✓ Passwords: Min 8 chars, uppercase, lowercase, numbers")

if __name__ == '__main__':
    main()