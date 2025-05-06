#!/usr/bin/env python
"""
Script to export database data for local development.
Runs django-admin dumpdata command with formatting for better readability.
"""

import os
import subprocess
import sys

def main():
    print("Exporting database data for local development...")
    
    # Create export directory if it doesn't exist
    os.makedirs('data_export', exist_ok=True)
    
    # Export all data
    subprocess.run([
        'python', 'manage.py', 'dumpdata',
        '--indent', '4',
        '--exclude', 'auth.permission',
        '--exclude', 'contenttypes',
        '--exclude', 'admin.logentry',
        '--exclude', 'sessions.session',
        '-o', 'data_export/all_data.json'
    ])
    
    # Export specific apps
    for app in ['customer', 'pharmacy']:
        subprocess.run([
            'python', 'manage.py', 'dumpdata',
            app,
            '--indent', '4',
            '-o', f'data_export/{app}_data.json'
        ])
    
    print("\nData export complete. Files are located in the 'data_export' directory.")
    print("\nTo import this data on your local machine, run:")
    print("    python manage.py loaddata data_export/all_data.json")
    print("\nOr for specific apps:")
    print("    python manage.py loaddata data_export/customer_data.json")
    print("    python manage.py loaddata data_export/pharmacy_data.json")

if __name__ == "__main__":
    main()