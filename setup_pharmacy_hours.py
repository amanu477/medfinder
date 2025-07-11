#!/usr/bin/env python3
"""
Script to set up pharmacy opening hours for testing the pharmacy status functionality
"""

import os
import django
from datetime import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from pharmacy.models import Pharmacy

def setup_pharmacy_hours():
    """Set up different opening hours for pharmacies to test the status display"""
    
    pharmacies = Pharmacy.objects.all()
    
    if not pharmacies.exists():
        print("No pharmacies found. Please create pharmacies first.")
        return
    
    # Different schedule examples
    schedules = [
        {
            'name': 'Early Bird Pharmacy',
            'opening_time': time(6, 0),  # 6:00 AM
            'closing_time': time(20, 0),  # 8:00 PM
        },
        {
            'name': 'Night Owl Pharmacy', 
            'opening_time': time(18, 0),  # 6:00 PM
            'closing_time': time(6, 0),   # 6:00 AM (next day)
        },
        {
            'name': 'Regular Hours Pharmacy',
            'opening_time': time(8, 0),   # 8:00 AM
            'closing_time': time(22, 0),  # 10:00 PM
        },
        {
            'name': '24/7 Pharmacy',
            'opening_time': time(0, 0),   # 12:00 AM
            'closing_time': time(23, 59), # 11:59 PM
        },
        {
            'name': 'Morning Only Pharmacy',
            'opening_time': time(7, 0),   # 7:00 AM
            'closing_time': time(12, 0),  # 12:00 PM
        }
    ]
    
    updated_count = 0
    
    for i, pharmacy in enumerate(pharmacies):
        if i < len(schedules):
            schedule = schedules[i]
            
            # Update pharmacy details
            pharmacy.opening_time = schedule['opening_time']
            pharmacy.closing_time = schedule['closing_time']
            pharmacy.save()
            
            print(f"✓ Updated {pharmacy.name}:")
            print(f"  Opening: {schedule['opening_time'].strftime('%I:%M %p')}")
            print(f"  Closing: {schedule['closing_time'].strftime('%I:%M %p')}")
            print(f"  Status: {'Open' if pharmacy.is_open_now() else 'Closed'}")
            print()
            
            updated_count += 1
        else:
            # Set default hours for remaining pharmacies
            pharmacy.opening_time = time(8, 0)   # 8:00 AM
            pharmacy.closing_time = time(20, 0)  # 8:00 PM
            pharmacy.save()
            updated_count += 1
    
    print(f"✅ Successfully updated {updated_count} pharmacies with different opening hours!")
    print("\nNow you can test the pharmacy status functionality by:")
    print("1. Searching for medicines at different times")
    print("2. Viewing pharmacy cards to see 'Open' or 'Closed' status")
    print("3. Placing orders to see the closed pharmacy warnings")

if __name__ == "__main__":
    setup_pharmacy_hours()