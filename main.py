#!/usr/bin/env python
"""
Main entry point for the Ethiopian Pharmacy Connection Platform
Pure Django WSGI application interface
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')

# Import Django and configure
import django
django.setup()

# Import Django WSGI application
from pharmacy_finder.wsgi import application

# Pure Django app - no Flask dependencies
app = application

if __name__ == '__main__':
    # Use Django's built-in development server
    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], 'runserver', '0.0.0.0:5000'])