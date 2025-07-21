#!/usr/bin/env python
"""
Main entry point for the Ethiopian Pharmacy Connection Platform
This file provides a simple WSGI interface for the Django application
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

# For Gunicorn compatibility, expose the Django app
app = application

if __name__ == '__main__':
    # For development, use Django's built-in server
    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], 'runserver', '0.0.0.0:5000'])