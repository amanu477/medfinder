#!/usr/bin/env python
"""
Script to reset admin password for local installation
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User

def reset_admin_password():
    """Reset admin password to a known value"""
    
    username = 'admin'
    new_password = 'admin123'
    
    try:
        # Get existing admin user
        admin_user = User.objects.get(username=username)
        
        # Reset password
        admin_user.set_password(new_password)
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        
        print("✓ Admin password reset successfully!")
        print(f"Username: {username}")
        print(f"Password: {new_password}")
        print(f"Email: {admin_user.email}")
        
    except User.DoesNotExist:
        # Create new admin user if doesn't exist
        admin_user = User.objects.create_superuser(
            username=username,
            email='admin@example.com',
            password=new_password,
            first_name='Admin',
            last_name='User'
        )
        print("✓ New admin user created!")
        print(f"Username: {username}")
        print(f"Password: {new_password}")
        print(f"Email: {admin_user.email}")
    
    print("\nYou can now login to:")
    print("- Django Admin: http://127.0.0.1:8000/admin/")
    print("- Platform Admin: http://127.0.0.1:8000/platform-admin/")

if __name__ == '__main__':
    reset_admin_password()