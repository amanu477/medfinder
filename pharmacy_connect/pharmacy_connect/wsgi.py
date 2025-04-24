"""
WSGI config for pharmacy_connect project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_connect.settings')

application = get_wsgi_application()
