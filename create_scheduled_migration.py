#!/usr/bin/env python
"""
Create migration for scheduled order fields
"""

import os
import sys
import django
from django.core.management import call_command
from django.utils import timezone

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

def run_migrations():
    """Run the migrations"""
    try:
        # Just run the migrations with existing migration files
        call_command('migrate', verbosity=2)
        print("Migrations completed successfully!")
    except Exception as e:
        print(f"Error running migrations: {e}")

if __name__ == "__main__":
    run_migrations()