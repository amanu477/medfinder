# How to Download and Run the Pharmacy Platform on Your PC

## Quick Start Summary

1. **Download**: Copy all files from this workspace to your PC
2. **Install Python 3.8+** and **PostgreSQL**
3. **Set up virtual environment** and **install dependencies**
4. **Configure database** and **run migrations**
5. **Start the server** with `python manage.py runserver`

---

## Step-by-Step Instructions

### Step 1: Download the Code

**Method 1: Manual Download (Easiest)**
1. Right-click on each folder/file in the file explorer on the left
2. Download the entire project structure:
   ```
   pharmacy-platform/
   ├── customer/
   ├── pharmacy/
   ├── pharmacy_finder/
   ├── templates/
   ├── static/
   ├── manage.py
   ├── local_requirements.txt
   ├── LOCAL_SETUP_GUIDE.md
   └── FUNCTIONALITY_GUIDE.md
   ```

**Method 2: Use Export Script (if available)**
- Look for any export or download options in your workspace

### Step 2: Install Prerequisites

**Install Python 3.8+:**
- Download from https://python.org/downloads/
- During installation, check "Add Python to PATH"
- Verify: Open Command Prompt, type `python --version`

**Install PostgreSQL:**
- Download from https://postgresql.org/download/
- Remember the password you set during installation
- Default port is 5432

### Step 3: Set Up the Project

1. **Open Command Prompt** and navigate to your project folder:
   ```cmd
   cd C:\Users\YourName\Documents\pharmacy-platform
   ```

2. **Create virtual environment:**
   ```cmd
   python -m venv pharmacy_env
   ```

3. **Activate virtual environment:**
   ```cmd
   pharmacy_env\Scripts\activate
   ```

4. **Install dependencies:**
   ```cmd
   pip install -r local_requirements.txt
   ```

### Step 4: Set Up Database

1. **Create PostgreSQL database:**
   ```sql
   CREATE DATABASE pharmacy_db;
   CREATE USER pharmacy_user WITH PASSWORD 'yourpassword123';
   GRANT ALL PRIVILEGES ON DATABASE pharmacy_db TO pharmacy_user;
   ```

2. **Configure database settings** in `pharmacy_finder/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'pharmacy_db',
           'USER': 'pharmacy_user',
           'PASSWORD': 'yourpassword123',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

### Step 5: Initialize the Application

1. **Run database migrations:**
   ```cmd
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create admin user:**
   ```cmd
   python manage.py createsuperuser
   ```

3. **Create media directories:**
   ```cmd
   mkdir media
   mkdir media\medicines
   mkdir media\prescriptions
   ```

### Step 6: Start the Server

```cmd
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## File Structure You Need

```
pharmacy-platform/
├── customer/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── pharmacy/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── pharmacy_finder/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/
│   ├── customer/
│   ├── pharmacy/
│   ├── base.html
│   ├── home.html
│   ├── prescription_success.html
│   ├── prescription_upload.html
│   └── search_results.html
├── static/
│   ├── css/
│   └── js/
├── media/ (create this)
│   ├── medicines/ (create this)
│   └── prescriptions/ (create this)
├── manage.py
├── local_requirements.txt
├── LOCAL_SETUP_GUIDE.md
├── FUNCTIONALITY_GUIDE.md
└── DOWNLOAD_INSTRUCTIONS.md
```

---

## Testing the Application

### 1. Admin Panel
- Go to: http://127.0.0.1:8000/admin/
- Login with your superuser account
- Add sample pharmacies and medicines

### 2. Customer Flow
- Visit: http://127.0.0.1:8000/
- Register as a customer
- Search for medicines
- Place orders

### 3. Pharmacy Flow
- Visit: http://127.0.0.1:8000/pharmacy/register/
- Register as a pharmacy
- Add medicines to inventory
- Manage customer orders

---

## Key Features

- **Location-based search** using Haversine formula
- **Order management** with approval workflow
- **Prescription upload** system
- **Real-time stock tracking**
- **Ethiopian Birr (ETB)** currency
- **Responsive design** with Bootstrap

---

## Troubleshooting

**Database connection error:**
- Check if PostgreSQL is running
- Verify database name and credentials

**Package installation error:**
- Try: `pip install --upgrade pip`
- For psycopg2 issues: `pip install psycopg2-binary`

**Static files not loading:**
- Run: `python manage.py collectstatic`

**Port 8000 in use:**
- Use different port: `python manage.py runserver 8080`

---

## Next Steps

1. Download all files to your PC
2. Follow the setup instructions above
3. Test the application thoroughly
4. Customize as needed for your specific requirements

The application is production-ready with comprehensive error handling, security features, and a clean, professional interface designed for the Ethiopian market.