"""
Management command to set up the separate MoH database
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    help = 'Set up the separate MoH database and create tables'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up MoH database...'))
        
        # Get the MoH models
        from moh.models import MoHPharmacyRegistry, MoHOfficer
        
        # Create tables using raw SQL for the moh_db
        from django.db import connections
        moh_db = connections['moh_db']
        
        with moh_db.cursor() as cursor:
            # Create MoHOfficer table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS moh_mohofficer (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL,
                    officer_id VARCHAR(50) UNIQUE NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    region VARCHAR(20) NOT NULL,
                    phone VARCHAR(20),
                    office_address TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Create MoHPharmacyRegistry table  
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS moh_mohpharmacyrecord (
                    id SERIAL PRIMARY KEY,
                    pharmacy_id INTEGER,
                    pharmacy_name VARCHAR(200) NOT NULL,
                    license_number VARCHAR(50) UNIQUE NOT NULL,
                    owner_name VARCHAR(100) NOT NULL,
                    pharmacist_name VARCHAR(100) NOT NULL,
                    pharmacist_license VARCHAR(50) NOT NULL,
                    region VARCHAR(20) NOT NULL DEFAULT 'addis_ababa',
                    city VARCHAR(100) NOT NULL DEFAULT 'Addis Ababa',
                    address_detail TEXT NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    email VARCHAR(254),
                    license_type VARCHAR(20) NOT NULL DEFAULT 'retail',
                    license_status VARCHAR(20) NOT NULL DEFAULT 'active',
                    issue_date DATE NOT NULL,
                    expiry_date DATE NOT NULL,
                    compliance_score INTEGER DEFAULT 0,
                    moh_officer VARCHAR(100),
                    inspection_notes TEXT,
                    business_license_document VARCHAR(100),
                    pharmacist_certificate_document VARCHAR(100),
                    pharmacy_permit_document VARCHAR(100),
                    inspection_report VARCHAR(100),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
        self.stdout.write(self.style.SUCCESS('MoH database tables created successfully!'))