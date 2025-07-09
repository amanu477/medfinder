#!/usr/bin/env python
"""
Main entry point for the Ethiopian Pharmacy Connection Platform
This file provides a Flask-compatible interface for the Django application
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
from pharmacy_finder.wsgi import application as django_app

# For Flask compatibility, we can wrap the Django app
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Flask

# Create a simple Flask app that routes to Django
app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(django_app)

if __name__ == '__main__':
    # Run the Django application directly
    run_simple('0.0.0.0', 5000, django_app, use_reloader=True, use_debugger=True)