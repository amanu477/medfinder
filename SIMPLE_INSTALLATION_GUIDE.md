# Simple Installation Guide - Ethiopian Pharmacy Platform

## What You Need First
1. **Python 3.8+** - Download from python.org
2. **Your computer** - Windows, Mac, or Linux

---

## Step 1: Get Python
- Go to **python.org/downloads**
- Download Python (latest version)
- Install it (check "Add to PATH" on Windows)
- Test: Open terminal and type `python --version`

## Step 2: Download Project
- Create a folder called "pharmacy-platform" on your desktop
- Copy all project files into this folder

## Step 3: Open Terminal
- **Windows**: Open Command Prompt in your project folder
- **Mac**: Open Terminal in your project folder
- **Linux**: Open Terminal in your project folder

## Step 4: Create Virtual Environment
```bash
python -m venv pharmacy_env
```

## Step 5: Activate Environment
**Windows:**
```bash
pharmacy_env\Scripts\activate
```

**Mac/Linux:**
```bash
source pharmacy_env/bin/activate
```

## Step 6: Install Everything
Copy and paste this (one line at a time):
```bash
pip install django pillow django-bootstrap5 dj-database-url gunicorn psycopg2-binary pytesseract opencv-python fuzzywuzzy python-levenshtein qrcode pyjwt email-validator numpy trafilatura
```

## Step 7: Create Settings File
Create a file called `.env` with this content:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
```

## Step 8: Set Up Database
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## Step 9: Create Media Folders
```bash
mkdir media
mkdir media/prescriptions
mkdir media/pharmacy_documents
mkdir media/moh_documents
mkdir media/cart_prescriptions
mkdir media/order_prescriptions
mkdir media/medicines
```

## Step 10: Load Sample Data (Optional)
```bash
python setup_all_logins.py
python load_all_data.py
```

## Step 11: Start Server
```bash
python manage.py runserver
```

## Step 12: Open Browser
Go to: **http://localhost:8000**

---

## That's It!
Your pharmacy platform is now running!

### Test These:
- **Admin**: http://localhost:8000/admin/
- **Customer**: http://localhost:8000/customer/register/
- **Pharmacy**: http://localhost:8000/pharmacy/register/

### Need Help?
- Make sure Python is installed
- Check virtual environment is activated (you see `(pharmacy_env)` in terminal)
- If error, try: `pip install --upgrade pip` first

### To Stop Server:
Press `Ctrl+C` in terminal

### To Start Again:
1. Open terminal in project folder
2. Run: `pharmacy_env\Scripts\activate` (Windows) or `source pharmacy_env/bin/activate` (Mac/Linux)
3. Run: `python manage.py runserver`