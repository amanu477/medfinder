# Step 4: Database Setup for Ethiopian Pharmacy Platform

## Option A: PostgreSQL Setup (Recommended for Production)

### 1. Create PostgreSQL Database

#### Windows:
```bash
# Open Command Prompt as Administrator
# Connect to PostgreSQL (enter password when prompted)
psql -U postgres

# Create database and user
CREATE DATABASE pharmacy_platform;
CREATE USER pharmacy_user WITH PASSWORD 'pharmacy123';
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;
\q
```

#### macOS/Linux:
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE pharmacy_platform;
CREATE USER pharmacy_user WITH PASSWORD 'pharmacy123';
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;
\q
```

### 2. Create Environment File
Create a `.env` file in your project root directory:

```env
DATABASE_URL=postgresql://pharmacy_user:pharmacy123@localhost:5432/pharmacy_platform
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

### 3. Run Database Migrations
```bash
# Make sure your virtual environment is activated
# Windows: pharmacy_env\Scripts\activate
# macOS/Linux: source pharmacy_env/bin/activate

# Create migration files
python manage.py makemigrations

# Apply migrations to create database tables
python manage.py migrate

# Create admin user (follow prompts)
python manage.py createsuperuser
```

### 4. Load Sample Data
```bash
# Load comprehensive test data
python load_all_data.py

# Alternative: Load basic test data
python load_test_data.py
```

## Option B: SQLite Setup (Easy for Development)

### 1. Simple SQLite Setup
```bash
# No database creation needed - SQLite creates automatically
# Just run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Load sample data
python load_all_data.py
```

### 2. SQLite Configuration
The project is already configured to use SQLite by default if PostgreSQL isn't available.

## Option C: Automatic Database Setup

### Use the Automatic Setup Script
```bash
# Run the automatic installer
python install_local.py
```

This will:
- Detect your system
- Check if PostgreSQL is installed
- Create database automatically
- Run all migrations
- Create admin user
- Load sample data

## Verification Steps

### 1. Check Database Connection
```bash
python manage.py shell
```

In the Python shell:
```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT 1")
print("Database connection successful!")
exit()
```

### 2. Check Tables Created
```bash
python manage.py dbshell
```

In the database shell:
```sql
-- PostgreSQL
\dt

-- SQLite
.tables
```

### 3. Verify Sample Data
```bash
python manage.py shell
```

```python
from customer.models import Customer
from pharmacy.models import Pharmacy
from delivery.models import DeliveryPerson

print(f"Customers: {Customer.objects.count()}")
print(f"Pharmacies: {Pharmacy.objects.count()}")
print(f"Delivery Personnel: {DeliveryPerson.objects.count()}")
```

## Test Accounts Created

After loading sample data, you'll have:

### Customer Accounts:
- Username: `testcustomer`, Password: `customer123`
- Username: `customer`, Password: `customer123`

### Pharmacy Accounts:
- Username: `pharmacy`, Password: `pharmacy123`
- Username: `pharmacy2`, Password: `pharmacy123`

### Delivery Personnel:
- Username: `jj`, Password: `delivery123`

### Admin Account:
- Created during `createsuperuser` step

## Troubleshooting

### PostgreSQL Connection Issues:
```bash
# Check if PostgreSQL is running
# Windows: Check Services
# macOS: brew services list
# Linux: sudo systemctl status postgresql
```

### Permission Issues:
```bash
# PostgreSQL permissions
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pharmacy_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pharmacy_user;
```

### Reset Database (if needed):
```bash
# Drop and recreate database
DROP DATABASE IF EXISTS pharmacy_platform;
CREATE DATABASE pharmacy_platform;
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;
```

## Next Steps

After completing database setup:
1. Start the development server: `python manage.py runserver`
2. Access the site: `http://localhost:8000/`
3. Access admin panel: `http://localhost:8000/admin/`
4. Test different user types with the provided accounts

The database is now ready for the Ethiopian Pharmacy Platform!