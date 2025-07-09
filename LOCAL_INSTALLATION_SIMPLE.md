# Ethiopian Pharmacy Platform - Simple Local Installation Guide

## Quick Installation (3 Steps)

### Step 1: Install Required Software

**Install Python 3.11+ and PostgreSQL:**

**Windows:**
1. Download Python from https://python.org/downloads/ (Check "Add Python to PATH")
2. Download PostgreSQL from https://www.postgresql.org/download/windows/
3. During PostgreSQL installation, remember the password for 'postgres' user

**macOS:**
```bash
# Install Homebrew first if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and PostgreSQL
brew install python@3.11 postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 2: Download and Setup Project

1. **Create project folder:**
```bash
mkdir ethiopian-pharmacy
cd ethiopian-pharmacy
```

2. **Copy all project files** to this folder (extract if from zip)

3. **Run the automatic setup script:**
```bash
python run_local.py
```

### Step 3: Create Database and Run

1. **Create PostgreSQL database:**
```bash
# Connect to PostgreSQL (Windows: use pgAdmin or psql)
psql -U postgres

# Create database (type these commands in psql)
CREATE DATABASE pharmacy_platform;
CREATE USER pharmacy_user WITH PASSWORD 'pharmacy123';
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;
\q
```

2. **Update database settings:**
Create `.env` file in project root:
```env
DATABASE_URL=postgresql://pharmacy_user:pharmacy123@localhost:5432/pharmacy_platform
SECRET_KEY=your-secret-key-here
DEBUG=True
```

3. **Run migrations and start server:**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Access Your Platform

Visit: http://127.0.0.1:8000/

**Admin Panel:** http://127.0.0.1:8000/admin/
**Customer Registration:** http://127.0.0.1:8000/customer/register/
**Pharmacy Registration:** http://127.0.0.1:8000/pharmacy/register/

## Features Available

✓ **Shopping Cart System** - Add multiple medicines to cart
✓ **Bulk OCR Verification** - Upload one prescription to validate all cart items
✓ **Medicine Search** - Location-based pharmacy search
✓ **Order Management** - Complete order tracking
✓ **Multi-user System** - Customer, Pharmacy, MoH, Admin accounts
✓ **Payment Integration** - Chapa payment gateway (Ethiopian Birr)

## Test the Features

1. **Register as Customer:** Create account at `/customer/register/`
2. **Search Medicines:** Use homepage search
3. **Add to Cart:** Click "Add to Cart" on search results
4. **Bulk OCR:** Go to cart → "Verify All Prescriptions"
5. **Checkout:** Complete order process

## Troubleshooting

**Database Connection Error:**
- Verify PostgreSQL is running
- Check database credentials in `.env` file

**Missing Dependencies:**
```bash
pip install Django==5.2 Pillow psycopg2-binary django-bootstrap5 dj-database-url gunicorn PyJWT pytesseract opencv-python fuzzywuzzy python-levenshtein
```

**Static Files Not Loading:**
```bash
python manage.py collectstatic --noinput
```

## Quick Commands

**Start Server:**
```bash
python manage.py runserver
```

**Create Admin User:**
```bash
python manage.py createsuperuser
```

**Reset Database:**
```bash
python manage.py flush
python manage.py migrate
```

**Load Sample Data:**
```bash
python load_all_data.py
```

That's it! Your Ethiopian Pharmacy Platform is now running locally with full shopping cart and OCR functionality.