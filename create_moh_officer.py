#!/usr/bin/env python
"""
Script to create a test MoH officer account for testing login functionality
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from moh.models import MoHOfficer

def create_moh_officer():
    """Create a test MoH officer account"""
    
    # Create Django user first
    username = 'moh_admin'
    password = 'moh123'
    email = 'admin@moh.gov.et'
    
    try:
        # Check if user already exists
        user = User.objects.get(username=username)
        print(f"User '{username}' already exists. Updating password...")
        user.set_password(password)
        user.save()
    except User.DoesNotExist:
        # Create new user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name='Dr. Ahmed',
            last_name='Hassan'
        )
        print(f"Created user: {username}")
    
    # Create or update MoH officer record
    try:
        moh_officer = MoHOfficer.objects.get(user=user)
        print(f"MoH officer record already exists for {username}")
    except MoHOfficer.DoesNotExist:
        moh_officer = MoHOfficer.objects.create(
            user=user,
            officer_id='MOH-2025-002',
            department='licensing',
            position='Senior Pharmacy Licensing Administrator',
            phone='+251-911-123457',
            email=email,
            is_active=True
        )
        print(f"Created MoH officer record for {username}")
    
    print("\n=== MoH Officer Login Credentials ===")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Officer ID: {moh_officer.officer_id}")
    print(f"Department: {moh_officer.get_department_display()}")
    print(f"Position: {moh_officer.position}")
    print("=====================================")

if __name__ == '__main__':
    create_moh_officer()