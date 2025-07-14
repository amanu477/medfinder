#!/usr/bin/env python
"""
Test all pharmacies with Ethiopian time
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

def test_all_pharmacies():
    """Test all pharmacies with Ethiopian time"""
    print("All Pharmacies Status Test (Ethiopian Time)")
    print("=" * 50)
    
    # Get current Ethiopian time
    utc_now = datetime.now(timezone.utc)
    ethiopian_time = utc_now + timedelta(hours=3)
    
    print(f"Current Ethiopian time: {ethiopian_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Current Ethiopian time (time only): {ethiopian_time.time()}")
    print()
    
    # Test all pharmacies
    for pharmacy in Pharmacy.objects.all():
        print(f"Pharmacy: {pharmacy.name}")
        print(f"  Hours: {pharmacy.opening_time.strftime('%I:%M %p')} - {pharmacy.closing_time.strftime('%I:%M %p')}")
        print(f"  24-hour: {pharmacy.is_24_hour}")
        print(f"  Status: {pharmacy.get_status_display()}")
        
        # Manual calculation
        eth_time = ethiopian_time.time()
        if pharmacy.is_24_hour:
            expected_status = "Open Now"
        elif pharmacy.opening_time <= pharmacy.closing_time:
            # Normal hours
            expected_status = "Open Now" if pharmacy.opening_time <= eth_time < pharmacy.closing_time else "Closed"
        else:
            # Overnight hours
            expected_status = "Open Now" if eth_time >= pharmacy.opening_time or eth_time < pharmacy.closing_time else "Closed"
        
        print(f"  Expected: {expected_status}")
        
        # Check if actual matches expected
        actual_status = pharmacy.get_status_display()
        if actual_status == expected_status:
            print(f"  ✓ CORRECT")
        else:
            print(f"  ✗ INCORRECT (Expected: {expected_status}, Got: {actual_status})")
        
        print()

if __name__ == "__main__":
    test_all_pharmacies()