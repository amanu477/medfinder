# Ethiopian Pharmacy Platform - Complete Local Setup Guide

## Step-by-Step Installation Instructions

### Prerequisites
1. **Python 3.8+** installed on your computer
2. **Git** (optional, for version control)
3. **Admin privileges** (for installing PostgreSQL if needed)

---

## Step 1: Download the Application

### Option A: Download Project Files
1. Copy all project files to a folder on your computer
2. Name the folder: `pharmacy-platform`
3. Open terminal/command prompt in that folder

### Option B: Using Git (if available)
```bash
git clone [repository-url]
cd pharmacy-platform
```

---

## Step 2: Choose Database Configuration

The application supports both SQLite and PostgreSQL. Database settings are in `pharmacy_finder/settings.py`.

### Current Database Configuration:
```python
# Database configuration supports both SQLite and PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3'
    )
}
```

This means:
- **Default**: SQLite (no setup required)
- **Production**: PostgreSQL (via DATABASE_URL environment variable)

---

## Step 3: Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv pharmacy_env

# Activate virtual environment
# Windows:
pharmacy_env\Scripts\activate
# macOS/Linux:
source pharmacy_env/bin/activate
```

You should see `(pharmacy_env)` in your prompt.

---

## Step 4: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all required packages
pip install django==5.2
pip install pillow
pip install django-bootstrap5
pip install dj-database-url
pip install gunicorn
pip install psycopg2-binary
pip install pytesseract
pip install opencv-python
pip install fuzzywuzzy
pip install python-levenshtein
pip install qrcode[pil]
pip install pyjwt
pip install email-validator
pip install numpy
pip install trafilatura
```

---

## Step 5: Configure Environment Variables

Create a `.env` file in the project root:

### For SQLite (Simple Setup):
```env
DEBUG=True
SECRET_KEY=your-secret-key-here-change-this-in-production
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### For PostgreSQL (Production Setup):
```env
DEBUG=True
SECRET_KEY=your-secret-key-here-change-this-in-production
DATABASE_URL=postgresql://username:password@localhost:5432/pharmacy_db
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Step 6: Create Media Directories

```bash
# Create directories for file uploads
mkdir -p media/prescriptions
mkdir -p media/pharmacy_documents
mkdir -p media/moh_documents
mkdir -p media/cart_prescriptions
mkdir -p media/order_prescriptions
mkdir -p media/medicines
```

---

## Step 7: Database Setup

### Option A: SQLite (Recommended for local development)
```bash
# Remove any existing database
rm -f db.sqlite3

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

### Option B: PostgreSQL Setup
1. **Install PostgreSQL:**
   - **Windows**: Download from https://www.postgresql.org/download/windows/
   - **macOS**: `brew install postgresql && brew services start postgresql`
   - **Linux**: `sudo apt install postgresql postgresql-contrib`

2. **Create database:**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database and user
   CREATE DATABASE pharmacy_db;
   CREATE USER pharmacy_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE pharmacy_db TO pharmacy_user;
   \q
   ```

3. **Update .env file:**
   ```env
   DATABASE_URL=postgresql://pharmacy_user:your_secure_password@localhost:5432/pharmacy_db
   ```

4. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

---

## Step 8: Install Tesseract OCR (For prescription scanning)

### Windows:
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to Windows PATH

### macOS:
```bash
brew install tesseract
```

### Linux:
```bash
sudo apt install tesseract-ocr
```

---

## Step 9: Load Sample Data

```bash
# Load comprehensive test data
python load_all_data.py

# OR create basic test users
python setup_all_logins.py
```

---

## Step 10: Start the Application

```bash
# Start development server
python manage.py runserver

# The application will be available at:
# http://localhost:8000
```

---

## Step 11: Test the Installation

### Access Points:
1. **Main Platform**: http://localhost:8000
2. **Admin Dashboard**: http://localhost:8000/admin/
3. **Customer Registration**: http://localhost:8000/customer/register/
4. **Pharmacy Registration**: http://localhost:8000/pharmacy/register/
5. **MoH Portal**: http://localhost:8000/moh/login/
6. **Delivery Portal**: http://localhost:8000/delivery/login/

### Test Login Accounts:
- **Admin**: admin / admin123
- **Customer**: testcustomer / testpass123
- **Pharmacy**: testpharmacy / testpass123
- **MoH Officer**: testmoh / testpass123
- **Delivery Person**: testdelivery / testpass123

---

## Application Features

### Customer Features:
- Medicine search by location
- Prescription upload with OCR validation
- Shopping cart with bulk prescription verification
- Order placement and tracking
- Payment integration (Chapa + Cash on Delivery)
- QR code payment verification
- Scheduled orders when pharmacies are closed

### Pharmacy Features:
- Medicine inventory management
- Order management and approval
- Prescription verification
- Pharmacy verification process
- Opening hours management
- Real-time pharmacy status display

### Delivery Features:
- Real-time delivery tracking
- GPS location updates
- QR code scanning for payment verification
- Automatic availability management
- Customer notifications

### Administrative Features:
- Platform oversight and management
- Pharmacy verification workflow
- Ministry of Health integration
- Incident reporting system
- System monitoring and analytics

---

## Database Configuration Details

### Settings.py Configuration:
```python
import dj_database_url

# Database configuration
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# For PostgreSQL optimization
if 'postgresql' in DATABASES['default']['ENGINE']:
    DATABASES['default']['OPTIONS'] = {
        'options': '-c default_transaction_isolation=read_committed'
    }
```

### Environment Variables:
- `DATABASE_URL`: Complete database connection string
- `DEBUG`: Development mode (True for local, False for production)
- `SECRET_KEY`: Django secret key for security
- `ALLOWED_HOSTS`: Comma-separated list of allowed domains

---

## Production Deployment

### For production deployment:
1. **Update environment variables:**
   ```env
   DEBUG=False
   SECRET_KEY=generate-a-secure-secret-key
   DATABASE_URL=postgresql://user:password@host:port/database
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

3. **Use production server:**
   ```bash
   gunicorn pharmacy_finder.wsgi:application --bind 0.0.0.0:8000
   ```

---

## Troubleshooting

### Common Issues:

1. **Python not found:**
   - Ensure Python is in PATH
   - Try `python3` instead of `python`

2. **Virtual environment issues:**
   - Ensure virtual environment is activated
   - Recreate if needed: `rm -rf pharmacy_env && python -m venv pharmacy_env`

3. **Database connection errors:**
   - Check DATABASE_URL in .env file
   - Verify database service is running
   - Test database credentials

4. **Migration errors:**
   - Delete migration files (keep `__init__.py`)
   - Run `python manage.py makemigrations` again
   - Apply migrations: `python manage.py migrate`

5. **Missing dependencies:**
   - Ensure virtual environment is activated
   - Reinstall packages: `pip install -r requirements.txt`

6. **Tesseract not found:**
   - Install Tesseract OCR for your operating system
   - Ensure it's in PATH

7. **Permission errors:**
   - Check file permissions on media directories
   - Ensure write access to project directory

---

## File Structure

```
pharmacy-platform/
├── pharmacy_env/          # Virtual environment
├── customer/              # Customer management app
├── pharmacy/              # Pharmacy management app
├── moh/                   # Ministry of Health app
├── delivery/              # Delivery management app
├── media/                 # File uploads
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
├── pharmacy_finder/       # Main Django project
│   ├── settings.py        # Django settings
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI application
├── manage.py              # Django management commands
├── .env                   # Environment variables
├── db.sqlite3            # SQLite database (if using SQLite)
└── requirements.txt       # Python dependencies
```

---

## Next Steps

1. **Explore the platform** using the test accounts
2. **Customize settings** in `pharmacy_finder/settings.py`
3. **Add payment gateway credentials** for Chapa integration
4. **Configure email settings** for notifications
5. **Set up SSL certificate** for production deployment
6. **Configure domain and hosting** for public access

The Ethiopian Pharmacy Platform is now fully installed and ready for use on your local computer!