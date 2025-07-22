#!/usr/bin/env python3
"""
Script to create MoH (Ministry of Health) test accounts for local development
Run this script after setting up your database to create login accounts for MoH system
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User
from moh.models import MoHOfficer

def create_moh_accounts():
    """Create single MoH admin account"""
    
    print("Creating MoH (Ministry of Health) Admin account...")
    
    # MoH Admin Account
    print("\nCreating MoH Admin account...")
    
    # Create user account
    try:
        moh_user = User.objects.get(username='moh_admin')
        print(f"   ✓ User 'moh_admin' already exists")
    except User.DoesNotExist:
        moh_user = User.objects.create_user(
            username='moh_admin',
            email='admin@moh.gov.et',
            password='moh123',
            first_name='Mohammed',
            last_name='Ahmed'
        )
        print(f"   ✓ Created user: moh_admin")
    
    # Create MoH officer profile
    try:
        moh_officer = MoHOfficer.objects.get(user=moh_user)
        print(f"   ✓ MoH Officer profile already exists")
    except MoHOfficer.DoesNotExist:
        moh_officer = MoHOfficer.objects.create(
            user=moh_user,
            officer_id='MOH001',
            department='administration',
            position='Senior Administrator',
            phone='+251911123456',
            email='admin@moh.gov.et'
        )
        print(f"   ✓ Created MoH Officer profile")
    
    print("\n" + "="*50)
    print("MoH ADMIN ACCOUNT CREATED SUCCESSFULLY!")
    print("="*50)
    print("\nMoH Admin Login Details:")
    print("   Username: moh_admin")
    print("   Password: moh123")
    print("   Department: Administration")
    
    print("\nAccess MoH system at: http://127.0.0.1:8000/moh/login/")
    print("="*50)

if __name__ == '__main__':
    try:
        create_moh_accounts()
    except Exception as e:
        print(f"Error creating MoH accounts: {e}")
        sys.exit(1)