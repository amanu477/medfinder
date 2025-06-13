#!/usr/bin/env python
"""
Fix Platform Admin Dashboard access
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User

def fix_platform_admin():
    """Ensure admin user can access platform admin dashboard"""
    
    username = 'admin'
    password = 'admin123'
    
    try:
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': 'admin@pharmacy.com',
                'first_name': 'Platform',
                'last_name': 'Admin',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True
            }
        )
        
        # Ensure user has proper permissions
        admin_user.set_password(password)
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.is_active = True
        admin_user.save()
        
        if created:
            print("✓ Created new admin user")
        else:
            print("✓ Updated existing admin user")
            
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Superuser: {admin_user.is_superuser}")
        print(f"Staff: {admin_user.is_staff}")
        
        print("\nAccess Platform Admin Dashboard:")
        print("1. Go to: http://127.0.0.1:8000/platform-admin/")
        print("2. Login with Django admin credentials above")
        print("3. The same credentials work for Django admin panel")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_platform_admin()