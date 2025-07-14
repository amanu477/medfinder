#!/usr/bin/env python
"""
Test specific time scenarios to verify pharmacy opening/closing logic
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

def test_time_scenarios():
    """Test pharmacy status at different times"""
    print("Testing Pharmacy Status at Different Times")
    print("=" * 50)
    
    # Get a pharmacy that closes at 6 PM
    pharmacy = Pharmacy.objects.filter(closing_time__hour=18).first()
    if not pharmacy:
        print("No pharmacy found that closes at 6 PM")
        return
    
    print(f"Testing pharmacy: {pharmacy.name}")
    print(f"Opening time: {pharmacy.opening_time.strftime('%I:%M %p')}")
    print(f"Closing time: {pharmacy.closing_time.strftime('%I:%M %p')}")
    print()
    
    # Test different times
    test_times = [
        (time(7, 59), "7:59 AM - Before opening"),
        (time(8, 0), "8:00 AM - Exact opening"),
        (time(8, 1), "8:01 AM - Just opened"),
        (time(12, 0), "12:00 PM - Midday"),
        (time(17, 59), "5:59 PM - Almost closing"),
        (time(18, 0), "6:00 PM - Exact closing"),
        (time(18, 1), "6:01 PM - Just closed"),
        (time(20, 0), "8:00 PM - Evening"),
    ]
    
    print("Time scenario tests:")
    print("-" * 30)
    
    for test_time, description in test_times:
        # Check if pharmacy should be open at this time
        if pharmacy.opening_time <= pharmacy.closing_time:
            # Normal hours
            should_be_open = pharmacy.opening_time <= test_time < pharmacy.closing_time
        else:
            # Overnight hours
            should_be_open = test_time >= pharmacy.opening_time or test_time < pharmacy.closing_time
        
        print(f"{description}: {'OPEN' if should_be_open else 'CLOSED'}")
    
    print()
    print("Current actual status:")
    print(f"Current time: {timezone.now().time()}")
    print(f"Is open now: {pharmacy.is_open_now()}")
    print(f"Status: {pharmacy.get_status_display()}")
    next_opening = pharmacy.get_next_opening_time()
    if next_opening:
        print(f"Next opening: {next_opening}")

if __name__ == "__main__":
    test_time_scenarios()