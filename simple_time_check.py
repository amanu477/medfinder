#!/usr/bin/env python
"""
Simple time check for Ethiopian timezone
"""

import os
import sys
import django
from datetime import datetime, timezone, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from pharmacy.models import Pharmacy
from django.utils import timezone as django_timezone

def simple_time_check():
    """Simple time check"""
    print("Simple Time Check")
    print("=" * 20)
    
    # Get current UTC time
    utc_now = datetime.now(timezone.utc)
    
    # Ethiopian time is UTC+3
    eat_offset = timedelta(hours=3)
    ethiopian_time = utc_now + eat_offset
    
    print(f"UTC time: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Ethiopian time: {ethiopian_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Ethiopian time (time only): {ethiopian_time.time()}")
    print()
    
    # Check Good Health Pharmacy
    try:
        pharmacy = Pharmacy.objects.get(name="Good health pharmacy")
        print(f"Pharmacy: {pharmacy.name}")
        print(f"Opening: {pharmacy.opening_time}")
        print(f"Closing: {pharmacy.closing_time}")
        print()
        
        # Check with Ethiopian time
        eth_time = ethiopian_time.time()
        print(f"Ethiopian time: {eth_time}")
        print(f"Should be open: {pharmacy.opening_time <= eth_time < pharmacy.closing_time}")
        print(f"Current status: {pharmacy.get_status_display()}")
        print()
        
        # Show what Django timezone.now() returns
        django_time = django_timezone.now()
        print(f"Django timezone.now(): {django_time}")
        print(f"Django time (time only): {django_time.time()}")
        
    except Pharmacy.DoesNotExist:
        print("Good health pharmacy not found")

if __name__ == "__main__":
    simple_time_check()