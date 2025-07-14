#!/usr/bin/env python
"""
Test script to verify pharmacy opening/closing hours logic
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
from django.contrib.auth.models import User

def test_pharmacy_hours():
    """Test pharmacy opening hours logic"""
    print("Testing Pharmacy Opening Hours Logic")
    print("=" * 50)
    
    # Get current time
    current_time = datetime.now().time()
    print(f"Current time: {current_time.strftime('%I:%M %p')}")
    print()
    
    # Test all pharmacies
    pharmacies = Pharmacy.objects.all()
    
    for pharmacy in pharmacies:
        print(f"Pharmacy: {pharmacy.name}")
        print(f"  Opening time: {pharmacy.opening_time.strftime('%I:%M %p')}")
        print(f"  Closing time: {pharmacy.closing_time.strftime('%I:%M %p')}")
        print(f"  Is 24-hour: {pharmacy.is_24_hour}")
        print(f"  Is open now: {pharmacy.is_open_now()}")
        print(f"  Status: {pharmacy.get_status_display()}")
        
        next_opening = pharmacy.get_next_opening_time()
        if next_opening:
            print(f"  Next opening: {next_opening}")
        else:
            print(f"  Next opening: Currently open or 24/7")
        print()
    
    print("Testing specific time scenarios:")
    print("-" * 30)
    
    # Test edge cases
    test_times = [
        time(8, 0),   # 8:00 AM
        time(9, 59),  # 9:59 AM
        time(10, 0),  # 10:00 AM (exact closing)
        time(10, 1),  # 10:01 AM (just closed)
        time(18, 0),  # 6:00 PM
        time(23, 59), # 11:59 PM
    ]
    
    for test_time in test_times:
        print(f"Testing time: {test_time.strftime('%I:%M %p')}")
        
        # Simulate current time being the test time
        for pharmacy in pharmacies[:2]:  # Test first 2 pharmacies
            # Manually check logic
            if pharmacy.is_24_hour:
                status = "Open (24/7)"
            elif pharmacy.opening_time <= pharmacy.closing_time:
                # Normal hours
                if pharmacy.opening_time <= test_time < pharmacy.closing_time:
                    status = "Open"
                else:
                    status = "Closed"
            else:
                # Overnight hours
                if test_time >= pharmacy.opening_time or test_time < pharmacy.closing_time:
                    status = "Open"
                else:
                    status = "Closed"
            
            print(f"  {pharmacy.name}: {status}")
        print()

if __name__ == "__main__":
    test_pharmacy_hours()