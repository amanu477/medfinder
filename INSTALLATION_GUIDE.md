# Ethiopian Pharmacy Connection Platform - Installation Guide

## Prerequisites
- Python 3.11 or higher
- PostgreSQL database
- Git

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd pharmacy-finder
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` file with your database configuration:
```
DATABASE_URL=postgresql://username:password@host:port/database_name
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser for platform admin
python manage.py createsuperuser

# Create MoH officer account
python create_moh_officer.py

# Load sample MoH data (optional)
python create_test_moh_records.py
```

### 6. Start the Development Server
```bash
python manage.py runserver 0.0.0.0:5000
```

## Access the Platform

### Platform Admin
- URL: http://localhost:5000/admin/
- Login with the superuser credentials you created

### MoH System
- URL: http://localhost:5000/moh/login/
- Default credentials: moh_officer / mohpassword123

### Customer Portal
- URL: http://localhost:5000/
- Register as a new customer

### Pharmacy Registration
- URL: http://localhost:5000/pharmacy/register/
- Register as a new pharmacy

## System Architecture

The platform implements a two-database architecture:

1. **Independent MoH Database**: Contains official pharmacy licenses managed by Ministry of Health
2. **Platform Database**: Contains pharmacy registrations from the platform
3. **Admin Verification**: Platform admins verify pharmacies by checking license matches between both systems

## Key Features

- **Separate Registration Systems**: MoH and platform registrations are completely independent
- **License Verification**: Admin can verify platform pharmacies against MoH records
- **Automatic Approval**: If license number matches MoH registry, pharmacy gets approved
- **Rejection System**: If license not found in MoH registry, pharmacy gets rejected
- **Medicine Search**: Location-based medicine and pharmacy search
- **Prescription Management**: Upload and manage prescriptions
- **Order System**: Place orders with nearby pharmacies

## Default Test Data

### MoH Registry (Independent System)
- License: ETH-PH-001 - Addis Central Pharmacy
- License: ETH-PH-002 - Bole Medical Pharmacy  
- License: ETH-PH-003 - Merkato Health Pharmacy
- License: ETH-PH-004 - Piassa Community Pharmacy
- License: ETH-PH-005 - Bahir Dar General Pharmacy

### Admin Credentials
- Username: admin
- Password: admin123

### MoH Officer Credentials
- Username: moh_officer
- Password: mohpassword123

## Troubleshooting

### Database Connection Issues
Ensure PostgreSQL is running and the DATABASE_URL in `.env` is correct.

### Migration Errors
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files Issues
```bash
python manage.py collectstatic
```

## Production Deployment

For production deployment:
1. Set `DEBUG=False` in `.env`
2. Configure proper `ALLOWED_HOSTS`
3. Use a production WSGI server like Gunicorn
4. Set up proper database with connection pooling
5. Configure static file serving with nginx or CDN

## Support

For issues or questions, refer to the project documentation or contact the development team.