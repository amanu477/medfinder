#!/usr/bin/env python
"""
Check Ethiopian time and pharmacy status
"""

import os
import sys
import django
from datetime import datetime
import pytz

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from pharmacy.models import Pharmacy
from django.utils import timezone

def check_ethiopian_time():
    """Check current Ethiopian time and pharmacy status"""
    print("Ethiopian Time Check")
    print("=" * 30)
    
    # Get current time in different formats
    utc_now = datetime.utcnow()
    django_now = timezone.now()
    
    # Ethiopian timezone (EAT - UTC+3)
    eat_tz = pytz.timezone('Africa/Addis_Ababa')
    ethiopian_time = utc_now.replace(tzinfo=pytz.UTC).astimezone(eat_tz)
    
    print(f"UTC time: {utc_now}")
    print(f"Django timezone.now(): {django_now}")
    print(f"Ethiopian time: {ethiopian_time}")
    print(f"Ethiopian time (time only): {ethiopian_time.time()}")
    print()
    
    # Check Good Health Pharmacy specifically
    try:
        pharmacy = Pharmacy.objects.get(name="Good health pharmacy")
        print(f"Pharmacy: {pharmacy.name}")
        print(f"Opening time: {pharmacy.opening_time}")
        print(f"Closing time: {pharmacy.closing_time}")
        print(f"Current Django time: {django_now.time()}")
        print(f"Current Ethiopian time: {ethiopian_time.time()}")
        print()
        
        # Check logic with Ethiopian time
        eth_time = ethiopian_time.time()
        should_be_open = pharmacy.opening_time <= eth_time < pharmacy.closing_time
        
        print(f"Ethiopian time logic:")
        print(f"  opening_time <= eth_time: {pharmacy.opening_time <= eth_time}")
        print(f"  eth_time < closing_time: {eth_time < pharmacy.closing_time}")
        print(f"  Should be open: {should_be_open}")
        print()
        
        print(f"Current pharmacy status: {pharmacy.get_status_display()}")
        print(f"Pharmacy is_open_now(): {pharmacy.is_open_now()}")
        
    except Pharmacy.DoesNotExist:
        print("Good health pharmacy not found")

if __name__ == "__main__":
    check_ethiopian_time()