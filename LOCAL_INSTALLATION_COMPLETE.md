# Ethiopian Pharmacy Platform - Complete Local Installation Guide

## Quick Start (For experienced users)

```bash
# 1. Download project files to your computer
# 2. Open terminal/command prompt in project folder
# 3. Run the installation script:
python install_on_local.py
```

That's it! The script will handle everything automatically.

---

## Manual Installation (Step-by-Step)

### Step 1: Install Python
- **Windows**: Download from https://python.org/downloads/ (Check "Add Python to PATH")
- **macOS**: `brew install python@3.11`
- **Linux**: `sudo apt install python3.11 python3.11-venv python3-pip`

### Step 2: Create Project Folder
```bash
mkdir pharmacy-platform
cd pharmacy-platform
# Copy all project files here
```

### Step 3: Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv pharmacy_env

# Activate it
# Windows:
pharmacy_env\Scripts\activate
# macOS/Linux:
source pharmacy_env/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install --upgrade pip
pip install django==5.2 pillow django-bootstrap5 dj-database-url gunicorn
pip install psycopg2-binary pytesseract opencv-python fuzzywuzzy
pip install python-levenshtein qrcode[pil] pyjwt email-validator
pip install numpy trafilatura
```

### Step 5: Create Environment File
Create `.env` file in project root:
```
DEBUG=True
SECRET_KEY=your-secret-key-for-local-development
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 6: Create Media Directories
```bash
mkdir -p media/prescriptions media/pharmacy_documents media/moh_documents
mkdir -p media/cart_prescriptions media/order_prescriptions media/medicines
```

### Step 7: Set Up Database
```bash
# Clean start (if needed)
rm -f db.sqlite3

# Create migrations
python manage.py makemigrations customer
python manage.py makemigrations pharmacy
python manage.py makemigrations moh
python manage.py makemigrations delivery

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

### Step 8: Load Sample Data (Optional)
```bash
# Load comprehensive test data
python load_all_data.py

# OR create basic test users
python setup_all_logins.py
```

### Step 9: Install Tesseract OCR (For prescription scanning)
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt install tesseract-ocr`

### Step 10: Run the Application
```bash
python manage.py runserver
```

Open browser to: **http://localhost:8000**

---

## Test Login Accounts

### Admin Dashboard
- URL: http://localhost:8000/admin/
- Username: admin
- Password: admin123

### Customer Portal
- URL: http://localhost:8000/customer/login/
- Username: testcustomer
- Password: testpass123

### Pharmacy Portal
- URL: http://localhost:8000/pharmacy/login/
- Username: testpharmacy
- Password: testpass123

### Ministry of Health
- URL: http://localhost:8000/moh/login/
- Username: testmoh
- Password: testpass123

### Delivery Personnel
- URL: http://localhost:8000/delivery/login/
- Username: testdelivery
- Password: testpass123

---

## Platform Features

### Customer Features
- Medicine search by location
- Prescription upload with OCR validation
- Shopping cart with bulk prescription verification
- Order placement and tracking
- Payment integration (Chapa + Cash on Delivery)
- QR code payment verification
- Scheduled orders when pharmacies are closed

### Pharmacy Features
- Medicine inventory management
- Order management and approval
- Prescription verification
- Pharmacy verification process
- Opening hours management
- Automatic scheduling system

### Delivery Features
- Real-time delivery tracking
- GPS location updates
- QR code scanning for payment verification
- Automatic availability management
- Customer notifications

### Administrative Features
- Platform oversight
- Pharmacy verification
- Ministry of Health integration
- Incident reporting
- System monitoring

---

## File Structure

```
pharmacy-platform/
├── customer/              # Customer management
├── pharmacy/              # Pharmacy management
├── moh/                   # Ministry of Health
├── delivery/              # Delivery system
├── media/                 # File uploads
├── static/                # Static files
├── templates/             # HTML templates
├── pharmacy_finder/       # Main Django project
├── manage.py              # Django management
├── .env                   # Environment variables
├── db.sqlite3            # Database
└── install_on_local.py   # Installation script
```

---

## Troubleshooting

### Common Issues

1. **Python not found**
   - Ensure Python is in PATH
   - Try `python3` instead of `python`

2. **Permission denied**
   - Use virtual environment (recommended)
   - On Linux/macOS: add `sudo` for system installs

3. **Database errors**
   - Delete `db.sqlite3` and re-run migrations
   - Check database credentials in `.env`

4. **Missing packages**
   - Activate virtual environment first
   - Reinstall: `pip install -r requirements.txt`

5. **Tesseract not found**
   - Install Tesseract OCR for your OS
   - Add to PATH or configure in settings

6. **Migration conflicts**
   - Delete migration files (keep `__init__.py`)
   - Run `python manage.py makemigrations` again

### Getting Help

If you encounter issues:
1. Check Django error logs
2. Verify virtual environment is active
3. Ensure all dependencies are installed
4. Try fresh installation with new virtual environment

---

## Next Steps

1. **Configure Payment Gateway**: Add Chapa credentials for Ethiopian payment processing
2. **Set up Email**: Configure email settings for notifications
3. **Customize Settings**: Modify `pharmacy_finder/settings.py` for your needs
4. **Add SSL**: For production deployment
5. **Domain Setup**: Configure your domain and hosting

---

## Production Deployment

For production use:
1. Set `DEBUG=False` in `.env`
2. Use PostgreSQL instead of SQLite
3. Configure proper domain in `ALLOWED_HOSTS`
4. Set up SSL certificate
5. Use Gunicorn: `gunicorn pharmacy_finder.wsgi:application`

---

The Ethiopian Pharmacy Platform is now ready for use! You can explore all features including medicine search, prescription validation, order management, delivery tracking, and payment processing.