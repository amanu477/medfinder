# Ethiopian Pharmacy Platform - Complete Local Setup Guide

## Prerequisites

### 1. Install Python 3.11+
**Windows:**
- Download from https://python.org/downloads/
- During installation, check "Add Python to PATH"
- Verify: Open Command Prompt and run `python --version`

**macOS:**
- Install using Homebrew: `brew install python@3.11`
- Or download from python.org

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

### 2. Install PostgreSQL
**Windows:**
- Download from https://www.postgresql.org/download/windows/
- During installation, remember the password you set for 'postgres' user
- Default port: 5432

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
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

### Step 1: Download Project Files
1. Create a project directory:
```bash
mkdir pharmacy-platform
cd pharmacy-platform
```

2. If you have the project files, extract them to this directory
3. If using Git, clone the repository:
```bash
git clone <repository-url> .
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv pharmacy_env

# Activate virtual environment
# Windows:
pharmacy_env\Scripts\activate
# macOS/Linux:
source pharmacy_env/bin/activate
```

### Step 3: Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install django==5.2
pip install psycopg2-binary
pip install pillow
pip install django-bootstrap5
pip install dj-database-url
pip install gunicorn
```

### Step 4: Database Setup

#### Create PostgreSQL Database
```bash
# Connect to PostgreSQL
# Windows (if added to PATH):
psql -U postgres

# Create database
CREATE DATABASE pharmacy_platform;
CREATE USER pharmacy_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;
\q
```

#### Configure Database Settings
Create `.env` file in project root:
```env
DATABASE_URL=postgresql://pharmacy_user:your_secure_password@localhost:5432/pharmacy_platform
SECRET_KEY=your-secret-key-here
DEBUG=True
```

Update `pharmacy_finder/settings.py`:
```python
import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://pharmacy_user:your_secure_password@localhost:5432/pharmacy_platform'
    )
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Step 5: Run Database Migrations
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

### Step 6: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 7: Create Media Directories
```bash
# Windows:
mkdir media\medicines media\prescriptions media\pharmacy_documents media\moh_documents

# macOS/Linux:
mkdir -p media/medicines media/prescriptions media/pharmacy_documents media/moh_documents
```

### Step 8: Load Sample Data (Optional)
If you have the data export files:
```bash
python manage.py loaddata data_export/all_data.json
```

### Step 9: Run the Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```

## Access the Platform

### URLs:
- **Homepage**: http://127.0.0.1:8000/
- **Customer Registration**: http://127.0.0.1:8000/customer/register/
- **Pharmacy Registration**: http://127.0.0.1:8000/pharmacy/register/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Customer Admin**: http://127.0.0.1:8000/customer/admin/login/
- **MoH Dashboard**: http://127.0.0.1:8000/moh/

### Test Accounts:
If you loaded sample data, you may have existing accounts. Otherwise, create test accounts:

1. **Admin Account**: Created with `createsuperuser` command
2. **Customer Account**: Register at `/customer/register/`
3. **Pharmacy Account**: Register at `/pharmacy/register/`

## Project Structure
```
pharmacy-platform/
├── customer/                 # Customer app
├── pharmacy/                # Pharmacy app
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS)
├── media/                   # Uploaded files
├── pharmacy_finder/         # Main project settings
├── manage.py               # Django management script
└── requirements.txt        # Dependencies (create this)
```

## Create Requirements File
```bash
pip freeze > requirements.txt
```

## Troubleshooting

### Common Issues:

1. **Database Connection Error**:
   - Verify PostgreSQL is running
   - Check database credentials in settings.py
   - Ensure database exists

2. **Migration Errors**:
   ```bash
   python manage.py makemigrations customer
   python manage.py makemigrations pharmacy
   python manage.py migrate
   ```

3. **Static Files Not Loading**:
   ```bash
   python manage.py collectstatic --clear --noinput
   ```

4. **Permission Denied (Media Files)**:
   - Ensure media directory is writable
   - Check file permissions

### Development Tips:

1. **View Database**:
   - Use pgAdmin or other PostgreSQL GUI tools
   - Or use Django admin at `/admin/`

2. **Debug Mode**:
   - Keep `DEBUG = True` for development
   - Error pages will show detailed information

3. **Log Files**:
   - Check Django console output for errors
   - Add logging to views for debugging

## Environment Variables

Create `.env` file for sensitive settings:
```env
SECRET_KEY=your-django-secret-key
DATABASE_URL=postgresql://pharmacy_user:password@localhost:5432/pharmacy_platform
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Production Considerations

When ready for production:
1. Set `DEBUG = False`
2. Update `ALLOWED_HOSTS`
3. Use environment variables for secrets
4. Configure proper web server (Nginx + Gunicorn)
5. Set up SSL certificates
6. Configure database backups

## Next Steps

1. **Test Basic Functionality**:
   - Register as customer and pharmacy
   - Upload medicine inventory
   - Test medicine search
   - Place test orders

2. **Customize for Your Needs**:
   - Modify templates and styling
   - Add additional features
   - Configure email settings
   - Set up payment processing

3. **Deploy to Production**:
   - Choose hosting provider
   - Configure domain name
   - Set up SSL certificates
   - Configure monitoring

## Support

If you encounter issues:
1. Check Django documentation
2. Verify all dependencies are installed
3. Ensure PostgreSQL is running
4. Check file permissions
5. Review error messages carefully

The platform is now ready for local development and testing!