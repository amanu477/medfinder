#!/usr/bin/env python
"""
Debug script to check current server time and pharmacy hours
"""

import os
import sys
import django
from datetime import datetime, time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from pharmacy.models import Pharmacy
from django.utils import timezone

def debug_time():
    """Debug current time and pharmacy hours"""
    print("Debug: Current Time and Pharmacy Hours")
    print("=" * 50)
    
    # Get current time in different formats
    current_time = datetime.now().time()
    current_datetime = datetime.now()
    django_time = timezone.now()
    
    print(f"Python datetime.now().time(): {current_time}")
    print(f"Python datetime.now(): {current_datetime}")
    print(f"Django timezone.now(): {django_time}")
    print(f"Django timezone.now().time(): {django_time.time()}")
    print()
    
    # Check a specific pharmacy
    try:
        pharmacy = Pharmacy.objects.filter(name="Test Pharmacy for Scheduled Orders", closing_time__hour=18).first()
        if pharmacy:
            print(f"Pharmacy: {pharmacy.name}")
            print(f"Opening time: {pharmacy.opening_time}")
            print(f"Closing time: {pharmacy.closing_time}")
            print(f"Current time: {current_time}")
            print()
            
            # Manual calculation
            print("Manual calculation:")
            print(f"opening_time <= closing_time: {pharmacy.opening_time <= pharmacy.closing_time}")
            print(f"opening_time <= current_time: {pharmacy.opening_time <= current_time}")
            print(f"current_time < closing_time: {current_time < pharmacy.closing_time}")
            print(f"Combined: {pharmacy.opening_time <= current_time < pharmacy.closing_time}")
            print()
            
            # Using pharmacy method
            print(f"is_open_now(): {pharmacy.is_open_now()}")
            print(f"get_status_display(): {pharmacy.get_status_display()}")
        else:
            print("Test pharmacy not found")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nAll pharmacies:")
    for pharmacy in Pharmacy.objects.all():
        print(f"{pharmacy.name}: {pharmacy.get_status_display()}")

if __name__ == "__main__":
    debug_time()