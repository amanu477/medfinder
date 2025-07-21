# Ethiopian Pharmacy Platform - Local Setup with PostgreSQL

## Complete Installation Guide for Local Development

This guide will help you set up the Ethiopian Pharmacy Platform on your local computer with PostgreSQL database.

## Prerequisites

Before starting, ensure you have the following installed:

### 1. Install Python 3.11+
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: Use Homebrew: `brew install python@3.11`
- **Linux**: `sudo apt-get install python3.11 python3.11-pip python3.11-venv`

### 2. Install PostgreSQL
- **Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- **macOS**: Use Homebrew: `brew install postgresql`
- **Linux**: `sudo apt-get install postgresql postgresql-contrib`

### 3. Install Git
- Download from [git-scm.com](https://git-scm.com/downloads)

### 4. Install Tesseract OCR (for prescription scanning)
- **Windows**: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

## Step 1: Download the Project

```bash
# Clone or download the project
git clone [YOUR_PROJECT_URL] ethiopian-pharmacy
cd ethiopian-pharmacy

# Or if you have the files already, navigate to the project directory
cd path/to/your/ethiopian-pharmacy-project
```

## Step 2: Set Up PostgreSQL Database

### Create Database and User

1. Start PostgreSQL service:
   - **Windows**: Use pgAdmin or start from Services
   - **macOS/Linux**: `sudo service postgresql start`

2. Access PostgreSQL as superuser:
```bash
sudo -u postgres psql
```

3. Create database and user:
```sql
-- Create the main database
CREATE DATABASE ethiopian_pharmacy_db;

-- Create the MoH database (separate as per architecture)
CREATE DATABASE ethiopian_pharmacy_moh_db;

-- Create a user for the application
CREATE USER pharmacy_user WITH PASSWORD 'your_secure_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ethiopian_pharmacy_db TO pharmacy_user;
GRANT ALL PRIVILEGES ON DATABASE ethiopian_pharmacy_moh_db TO pharmacy_user;

-- Grant connection privileges
ALTER USER pharmacy_user CREATEDB;

-- Exit PostgreSQL
\q
```

## Step 3: Set Up Python Environment

```bash
# Create virtual environment
python -m venv pharmacy_env

# Activate virtual environment
# Windows:
pharmacy_env\Scripts\activate
# macOS/Linux:
source pharmacy_env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

## Step 4: Install Project Dependencies

```bash
# Install required packages
pip install Django==5.2
pip install psycopg2-binary
pip install Pillow
pip install pytesseract
pip install fuzzywuzzy
pip install python-Levenshtein
pip install requests
pip install dj-database-url
pip install python-dotenv

# Or if you have requirements.txt:
pip install -r requirements.txt
```

## Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env  # Linux/macOS
# or create .env file manually on Windows
```

Add the following content to `.env`:

```env
# Database Configuration
DATABASE_URL=postgresql://pharmacy_user:your_secure_password_here@localhost:5432/ethiopian_pharmacy_db
MOH_DATABASE_URL=postgresql://pharmacy_user:your_secure_password_here@localhost:5432/ethiopian_pharmacy_moh_db

# Django Settings
SECRET_KEY=your-very-long-secret-key-here-make-it-random-and-secure
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Chapa Payment Settings (for testing)
CHAPA_SECRET_KEY=CHASECK_TEST-your-test-key
CHAPA_PUBLIC_KEY=CHAPUBK_TEST-your-test-key
SITE_URL=http://localhost:8000

# Session Security
SESSION_SECRET=your-session-secret-key-here

# Tesseract Path (adjust based on your installation)
# Windows example:
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
# macOS/Linux usually auto-detected
```

## Step 6: Update Django Settings for PostgreSQL

The project should already be configured for PostgreSQL, but verify `pharmacy_finder/settings.py`:

```python
import dj_database_url
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL')),
    'moh': dj_database_url.parse(os.environ.get('MOH_DATABASE_URL'))
}

# Make sure these are set
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
```

## Step 7: Initialize Database

```bash
# Make migrations for all apps
python manage.py makemigrations customer
python manage.py makemigrations pharmacy
python manage.py makemigrations delivery
python manage.py makemigrations moh
python manage.py makemigrations platform_admin

# Apply migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

## Step 8: Load Initial Data

```bash
# Load test data (if available)
python manage.py loaddata initial_data.json  # if exists

# Or run custom setup scripts
python setup_complete.py  # if exists
```

## Step 9: Create Test Accounts

Run Python shell to create test accounts:

```bash
python manage.py shell
```

```python
# Create test accounts
from django.contrib.auth.models import User
from customer.models import Customer
from pharmacy.models import Pharmacy
from delivery.models import DeliveryPerson
from moh.models import MoHOfficer

# Create customer
customer_user = User.objects.create_user('customer', 'customer@test.com', 'customer123')
customer = Customer.objects.create(user=customer_user, name='Test Customer', phone='0911234567')

# Create pharmacy
pharmacy_user = User.objects.create_user('pharmacy', 'pharmacy@test.com', 'pharmacy123')
pharmacy = Pharmacy.objects.create(
    user=pharmacy_user, 
    name='Good Health Pharmacy',
    license_number='PH001',
    phone='0911234568',
    address='Addis Ababa, Ethiopia',
    latitude=9.0320,
    longitude=38.7615,
    is_active=True
)

# Create delivery person
delivery_user = User.objects.create_user('abe', 'delivery@test.com', 'testpass123')
delivery_person = DeliveryPerson.objects.create(
    user=delivery_user,
    pharmacy=pharmacy,
    phone='0911234569',
    license_number='DL001',
    is_active=True
)

# Create MoH officer
moh_user = User.objects.create_user('moh_officer', 'moh@test.com', 'moh123')
moh_officer = MoHOfficer.objects.create(
    user=moh_user,
    employee_id='MOH001',
    department='Drug Administration',
    is_active=True
)

print("Test accounts created successfully!")
```

Type `exit()` to leave the shell.

## Step 10: Static Files Setup

```bash
# Collect static files
python manage.py collectstatic --noinput
```

## Step 11: Test the Installation

```bash
# Run the development server
python manage.py runserver 0.0.0.0:8000
```

Visit `http://localhost:8000` in your browser.

### Test Login Credentials:
- **Customer**: `customer` / `customer123`
- **Pharmacy**: `pharmacy` / `pharmacy123`
- **Delivery**: `abe` / `testpass123`
- **MoH Officer**: `moh_officer` / `moh123`
- **Admin**: Use the superuser account you created

## Step 12: Verify All Features

1. **Customer Features**: Register, search medicines, upload prescriptions
2. **Pharmacy Features**: Manage inventory, process prescriptions, handle orders
3. **Delivery Features**: View deliveries, update status, use QR scanner
4. **MoH Features**: Verify pharmacy licenses, monitor compliance
5. **Admin Features**: Platform management

## Troubleshooting

### Database Connection Issues:
```bash
# Test PostgreSQL connection
psql -h localhost -U pharmacy_user -d ethiopian_pharmacy_db
```

### Tesseract Issues:
```bash
# Test Tesseract installation
tesseract --version
```

### Missing Dependencies:
```bash
# Reinstall packages
pip install --upgrade -r requirements.txt
```

### Port Issues:
```bash
# Use different port if 8000 is occupied
python manage.py runserver 0.0.0.0:8080
```

## Production Considerations

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Use strong, unique secret keys
3. Configure proper `ALLOWED_HOSTS`
4. Set up HTTPS/SSL
5. Use environment-specific database settings
6. Configure static file serving (CDN/cloud storage)
7. Set up proper logging
8. Configure backup systems

## Security Notes

1. Never commit `.env` files to version control
2. Use strong passwords for database users
3. Regularly update dependencies
4. Monitor for security vulnerabilities
5. Use HTTPS in production
6. Implement proper backup strategies

## Support

If you encounter issues:
1. Check Django logs for errors
2. Verify PostgreSQL is running
3. Ensure all dependencies are installed
4. Check file permissions
5. Verify environment variables are set correctly

Your Ethiopian Pharmacy Platform should now be running locally with full PostgreSQL support!