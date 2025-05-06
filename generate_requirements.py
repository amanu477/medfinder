#!/usr/bin/env python
"""
Script to generate requirements.txt file for the Pharmacy Connection Platform.
This helps when deploying the application outside of Replit.
"""

with open('requirements.txt', 'w') as f:
    f.write("""Django==5.2
django-bootstrap5==23.3
dj-database-url==2.1.0
gunicorn==21.2.0
Pillow==10.2.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
""")