# Ethiopian Pharmacy Platform - Complete Local Setup Guide

## Prerequisites

### 1. Install Python 3.8+
**Windows:**
- Download Python from https://python.org/downloads/
- During installation, check "Add Python to PATH"
- Verify: Open Command Prompt and run `python --version`

**Mac:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# Install Python
brew install python
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. Install PostgreSQL

**Windows:**
1. Download PostgreSQL from https://postgresql.org/download/windows/
2. Run installer and remember the password you set for 'postgres' user
3. Add PostgreSQL bin directory to PATH:
   - Default location: `C:\Program Files\PostgreSQL\15\bin`
4. Verify: Open Command Prompt and run `psql --version`

**Mac:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux:**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. Install Git
- Download from https://git-scm.com/downloads
- Follow installation instructions for your OS

## Project Setup

### 1. Download Project Files
```bash
# If using git
git clone <your-repository-url>
cd pharmacy-platform

# Or download and extract the ZIP file
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv pharmacy_env
pharmacy_env\Scripts\activate

# Mac/Linux
python3 -m venv pharmacy_env
source pharmacy_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install django==5.2
pip install psycopg2-binary
pip install pillow
pip install django-bootstrap5
pip install gunicorn
pip install dj-database-url
```

### 4. Database Setup

**Create Database:**
```bash
# Windows (Command Prompt)
psql -U postgres
CREATE DATABASE pharmacy_platform;
CREATE USER pharmacy_user WITH PASSWORD 'pharmacy_password';
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;
\q

# Mac/Linux
sudo -u postgres psql
CREATE DATABASE pharmacy_platform;
CREATE USER pharmacy_user WITH PASSWORD 'pharmacy_password';
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;
\q
```

### 5. Environment Configuration

Create `.env` file in project root:
```
DATABASE_URL=postgresql://pharmacy_user:pharmacy_password@localhost:5432/pharmacy_platform
DEBUG=True
SECRET_KEY=your-secret-key-here-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

### 6. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### 8. Load Sample Data
```bash
python manage.py shell
```

In the Django shell, run:
```python
from django.contrib.auth.models import User
from pharmacy.models import Pharmacy, Medicine
from customer.models import Customer

# Create sample pharmacies with proper coordinates
pharmacies_data = [
    {
        'name': '6kilo pharmacy',
        'license_number': '6K001',
        'address': '6kilo Area, Near User Location, Addis Ababa',
        'phone': '+251911000001',
        'email': '6kilo@pharmacy.com',
        'latitude': 9.0240,
        'longitude': 38.7480,
        'opening_time': '08:00:00',
        'closing_time': '21:30:00'
    },
    {
        'name': 'Ambassador Pharmacy',
        'license_number': 'AMB001',
        'address': 'Ambassador Area, Addis Ababa',
        'phone': '+251911000002',
        'email': 'ambassador@pharmacy.com',
        'latitude': 9.0180,
        'longitude': 38.7520,
        'opening_time': '08:00:00',
        'closing_time': '22:00:00'
    },
    {
        'name': '4kilo pharmacy',
        'license_number': '4K001',
        'address': '4kilo Business District, Addis Ababa',
        'phone': '+251911000003',
        'email': '4kilo@pharmacy.com',
        'latitude': 9.0200,
        'longitude': 38.7470,
        'opening_time': '07:30:00',
        'closing_time': '21:00:00'
    }
]

for i, pharmacy_data in enumerate(pharmacies_data, 1):
    # Create user for pharmacy
    username = pharmacy_data['name'].lower().replace(' ', '_')
    user = User.objects.create_user(
        username=username,
        email=pharmacy_data['email'],
        password='pharmacy123'
    )
    
    # Create pharmacy
    pharmacy = Pharmacy.objects.create(
        user=user,
        name=pharmacy_data['name'],
        license_number=pharmacy_data['license_number'],
        address=pharmacy_data['address'],
        phone=pharmacy_data['phone'],
        email=pharmacy_data['email'],
        latitude=pharmacy_data['latitude'],
        longitude=pharmacy_data['longitude'],
        opening_time=pharmacy_data['opening_time'],
        closing_time=pharmacy_data['closing_time'],
        is_active=True
    )
    
    # Add medicines
    Medicine.objects.create(
        name='Panadol',
        description='Pain relief and fever reducer',
        price=25.00,
        stock_quantity=100 + i * 20,
        expiry_date='2025-12-31',
        is_available=True,
        prescription_required=False,
        pharmacy=pharmacy
    )
    
    Medicine.objects.create(
        name='Aspirin',
        description='Pain relief and anti-inflammatory',
        price=15.00,
        stock_quantity=80 + i * 15,
        expiry_date='2025-11-30',
        is_available=True,
        prescription_required=False,
        pharmacy=pharmacy
    )

print("Sample data created successfully!")
exit()
```

### 9. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 10. Run Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

## Testing the Application

### 1. Access the Application
Open your browser and go to: `http://localhost:8000`

### 2. Test Location-Based Search
1. Click "Get My Location for Better Results" (allow location access)
2. Search for "panadol" or "aspirin"
3. Results should be sorted by distance from your location
4. Verify that "6kilo pharmacy" appears first if it's closest

### 3. Test Pharmacy Registration
1. Go to `http://localhost:8000/pharmacy/register/`
2. Fill all required fields
3. Upload business license and pharmacist certificate (mandatory)
4. Verify form validation works for all fields

### 4. Admin Access
1. Go to `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Manage pharmacies, medicines, and orders

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL service
# Windows: Services.msc -> PostgreSQL
# Mac: brew services list
# Linux: sudo systemctl status postgresql
```

### Port Already in Use
```bash
# Change port in manage.py runserver
python manage.py runserver 0.0.0.0:8001
```

### Location Not Working
1. Ensure HTTPS or localhost (location API requirement)
2. Allow location permissions in browser
3. Check browser console for JavaScript errors

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

## Production Deployment Notes

### Environment Variables
```
DEBUG=False
SECRET_KEY=generate-new-secure-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### Additional Security
- Use HTTPS
- Configure CSRF settings
- Set up proper media file serving
- Configure email backend for notifications

## File Structure
```
pharmacy-platform/
├── customer/                 # Customer app
├── pharmacy/                # Pharmacy app
├── pharmacy_finder/         # Main project settings
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS, images)
├── media/                   # Uploaded files
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── README.md              # Project documentation
```

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed correctly
3. Ensure database is running and accessible
4. Check Django logs for specific error messages

The platform includes:
- Medicine search with location-based sorting
- Pharmacy registration with document verification
- Prescription upload system
- Admin dashboard for management
- MoH verification system
- Comprehensive form validation