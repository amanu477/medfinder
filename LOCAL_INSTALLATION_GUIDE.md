# Ethiopian Pharmacy Platform - Local Installation Guide

## Prerequisites

Before installing the project, ensure you have the following installed on your PC:

### 1. Python 3.8 or higher
- Download from: https://www.python.org/downloads/
- During installation, make sure to check "Add Python to PATH"

### 2. Git
- Download from: https://git-scm.com/downloads

### 3. PostgreSQL Database
- Download from: https://www.postgresql.org/download/
- Remember the password you set for the postgres user

### 4. Visual Studio Code (Recommended)
- Download from: https://code.visualstudio.com/

## Installation Steps

### Step 1: Clone the Project
Open Command Prompt or PowerShell and run:
```bash
git clone <your-repository-url>
cd pharmacy-platform
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv pharmacy_env

# Activate virtual environment
# On Windows:
pharmacy_env\Scripts\activate

# On macOS/Linux:
source pharmacy_env/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install these packages manually:
```bash
pip install django==5.2
pip install psycopg2-binary
pip install pillow
pip install django-bootstrap5
pip install dj-database-url
pip install gunicorn
pip install openai
pip install trafilatura
pip install pyjwt
pip install oauthlib
pip install flask-dance
pip install flask-login
```

### Step 4: Database Setup

#### Create PostgreSQL Database
1. Open pgAdmin or use psql command line
2. Create a new database:
```sql
CREATE DATABASE pharmacy_platform;
CREATE USER pharmacy_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;
```

#### Create Environment File
Create a `.env` file in the project root directory:
```env
# Database Configuration
DATABASE_URL=postgresql://pharmacy_user:your_password@localhost:5432/pharmacy_platform
PGHOST=localhost
PGPORT=5432
PGDATABASE=pharmacy_platform
PGUSER=pharmacy_user
PGPASSWORD=your_password

# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Payment Gateway (Optional - for testing)
CHAPA_PUBLIC_KEY=your_chapa_public_key
CHAPA_SECRET_KEY=your_chapa_secret_key

# OpenAI API (Optional)
OPENAI_API_KEY=your_openai_api_key
```

### Step 5: Django Setup
```bash
# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 6: Load Sample Data (Optional)
```bash
# Create sample data
python create_test_moh_records.py
python create_moh_officer.py
python setup_all_logins.py
```

### Step 7: Run the Development Server
```bash
python manage.py runserver
```

The application will be available at: http://127.0.0.1:8000/

## VS Code Setup

### Install Recommended Extensions
1. Open VS Code
2. Install these extensions:
   - Python
   - Django
   - PostgreSQL
   - HTML CSS Support
   - JavaScript (ES6) code snippets

### Configure VS Code Settings
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./pharmacy_env/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "emmet.includeLanguages": {
        "django-html": "html"
    },
    "files.associations": {
        "*.html": "django-html"
    }
}

### Step 8: Test Installation

#### Test Database Connection
```bash
python manage.py shell
```
In the shell:
```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
exit()
```

#### Test All Login Systems
1. **Customer Login**: http://127.0.0.1:8000/login/
   - Username: `testcustomer` / Password: `testpass123`

2. **Pharmacy Login**: http://127.0.0.1:8000/pharmacy/login/
   - Register a new pharmacy or use existing credentials

3. **MoH Officer Login**: http://127.0.0.1:8000/moh/
   - Username: `moh_officer` / Password: `mohpass123`

4. **Platform Admin**: http://127.0.0.1:8000/platform-admin/
   - Use the superuser account you created

## Common Issues and Solutions

### Issue 1: PostgreSQL Connection Error
**Solution:**
```bash
# Check if PostgreSQL is running
# Windows:
sc query postgresql-x64-13

# Start PostgreSQL service
net start postgresql-x64-13
```

### Issue 2: Python Module Not Found
**Solution:**
```bash
# Make sure virtual environment is activated
pharmacy_env\Scripts\activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue 3: Static Files Not Loading
**Solution:**
```bash
python manage.py collectstatic --clear
python manage.py collectstatic
```

### Issue 4: Migration Errors
**Solution:**
```bash
# Reset migrations (WARNING: This will delete data)
python manage.py migrate --fake-initial
python manage.py makemigrations
python manage.py migrate
```

## Development Workflow

### Daily Development Commands
```bash
# Activate environment
pharmacy_env\Scripts\activate

# Run development server
python manage.py runserver

# Apply new migrations
python manage.py makemigrations
python manage.py migrate

# Open Django shell
python manage.py shell

# Run tests
python manage.py test
```

### Creating New Features
```bash
# Create new Django app
python manage.py startapp app_name

# Create new model migrations
python manage.py makemigrations app_name

# Apply migrations
python manage.py migrate
```

## Production Deployment Notes

For production deployment:
1. Set `DEBUG=False` in `.env`
2. Configure proper `ALLOWED_HOSTS`
3. Use a production WSGI server like Gunicorn
4. Set up proper static file serving
5. Configure secure database credentials
6. Enable HTTPS

## Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Bootstrap Documentation: https://getbootstrap.com/docs/

## Support

If you encounter issues:
1. Check the error logs in the terminal
2. Verify all dependencies are installed
3. Ensure PostgreSQL is running
4. Check database connection settings
5. Make sure virtual environment is activated

## Project Structure
```
pharmacy-platform/
├── customer/                 # Customer management app
├── pharmacy/                # Pharmacy management app
├── moh/                     # Ministry of Health app
├── platform_admin/         # Platform administration
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
├── media/                   # User uploaded files
├── pharmacy_finder/         # Main Django project
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables
```