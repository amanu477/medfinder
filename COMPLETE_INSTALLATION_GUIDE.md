# Complete Installation Guide - Ethiopian Pharmacy Platform

## Step-by-Step Installation Instructions

### Prerequisites
Before starting, ensure you have the following installed on your computer:

1. **Python 3.8 or higher** (recommended: Python 3.11)
2. **Git** (for downloading the project)
3. **PostgreSQL** (optional but recommended for production)

---

## Step 1: Install Python

### For Windows:
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 (latest stable version)
3. During installation, **check "Add Python to PATH"**
4. Install for all users
5. Verify installation by opening Command Prompt and typing:
   ```
   python --version
   ```

### For macOS:
1. Install Homebrew if you haven't already:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```
   brew install python@3.11
   ```

### For Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip
```

---

## Step 2: Install Git

### For Windows:
1. Download Git from https://git-scm.com/download/win
2. Install with default settings
3. Verify installation:
   ```
   git --version
   ```

### For macOS:
```bash
brew install git
```

### For Linux:
```bash
sudo apt install git
```

---

## Step 3: Download the Project

1. **Create a project directory:**
   ```bash
   mkdir pharmacy-platform
   cd pharmacy-platform
   ```

2. **Download the project files:**
   Since you have the project files, copy all files from your current directory to the new folder, or use git if available:
   ```bash
   git clone <your-repository-url>
   cd <project-folder>
   ```

---

## Step 4: Set Up Virtual Environment

1. **Create virtual environment:**
   ```bash
   python -m venv pharmacy_env
   ```

2. **Activate virtual environment:**
   
   **Windows:**
   ```bash
   pharmacy_env\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source pharmacy_env/bin/activate
   ```

3. **Verify activation** (you should see `(pharmacy_env)` in your terminal prompt)

---

## Step 5: Install Project Dependencies

1. **Upgrade pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install required packages:**
   ```bash
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

## Step 6: Database Setup

### Option A: SQLite (Easier, for development)
1. **Create environment file:**
   ```bash
   # Create .env file in project root
   echo "DEBUG=True" > .env
   echo "SECRET_KEY=your-secret-key-here" >> .env
   echo "DATABASE_URL=sqlite:///db.sqlite3" >> .env
   ```

### Option B: PostgreSQL (Recommended for production)
1. **Install PostgreSQL:**
   
   **Windows:** Download from https://www.postgresql.org/download/windows/
   
   **macOS:** 
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

2. **Create database:**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE pharmacy_db;
   CREATE USER pharmacy_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE pharmacy_db TO pharmacy_user;
   \q
   ```

3. **Create environment file:**
   ```bash
   echo "DEBUG=True" > .env
   echo "SECRET_KEY=your-secret-key-here" >> .env
   echo "DATABASE_URL=postgresql://pharmacy_user:your_password@localhost:5432/pharmacy_db" >> .env
   ```

---

## Step 7: Set Up the Database

1. **Apply database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create superuser (admin account):**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin account.

---

## Step 8: Create Media Directories

```bash
mkdir -p media/prescriptions
mkdir -p media/pharmacy_documents
mkdir -p media/moh_documents
mkdir -p media/cart_prescriptions
mkdir -p media/order_prescriptions
mkdir -p media/medicines
```

---

## Step 9: Load Sample Data (Optional)

1. **Load test data:**
   ```bash
   python load_all_data.py
   ```

2. **Or create basic test users:**
   ```bash
   python setup_all_logins.py
   ```

---

## Step 10: Install Tesseract OCR (For prescription scanning)

### Windows:
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR`
3. Add to PATH or update settings.py with path

### macOS:
```bash
brew install tesseract
```

### Linux:
```bash
sudo apt install tesseract-ocr
```

---

## Step 11: Test the Installation

1. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

2. **Open your browser and go to:**
   ```
   http://localhost:8000
   ```

3. **Test login with created accounts:**
   - Admin: http://localhost:8000/admin/
   - Customer registration: http://localhost:8000/customer/register/
   - Pharmacy registration: http://localhost:8000/pharmacy/register/

---

## Step 12: Production Setup (Optional)

### For production deployment:

1. **Install production server:**
   ```bash
   pip install gunicorn
   ```

2. **Update settings for production:**
   ```bash
   echo "DEBUG=False" >> .env
   echo "ALLOWED_HOSTS=your-domain.com,localhost" >> .env
   ```

3. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

4. **Run with Gunicorn:**
   ```bash
   gunicorn pharmacy_finder.wsgi:application
   ```

---

## Troubleshooting

### Common Issues:

1. **Python not found:**
   - Ensure Python is added to PATH
   - Try `python3` instead of `python`

2. **Permission denied:**
   - Use `sudo` on Linux/macOS for system-wide installations
   - Or use virtual environment (recommended)

3. **Database connection errors:**
   - Verify PostgreSQL is running
   - Check database credentials in .env file

4. **Missing modules:**
   - Ensure virtual environment is activated
   - Reinstall requirements: `pip install -r requirements.txt`

5. **Tesseract not found:**
   - Install Tesseract OCR for your operating system
   - Add to PATH or configure in settings.py

---

## Directory Structure After Installation

```
pharmacy-platform/
├── pharmacy_env/          # Virtual environment
├── customer/              # Customer app
├── pharmacy/              # Pharmacy app
├── moh/                   # Ministry of Health app
├── delivery/              # Delivery management
├── media/                 # Uploaded files
├── static/                # Static files
├── templates/             # HTML templates
├── pharmacy_finder/       # Main Django project
├── manage.py              # Django management
├── .env                   # Environment variables
└── db.sqlite3            # Database (if using SQLite)
```

---

## Next Steps

1. **Customize settings** in `pharmacy_finder/settings.py`
2. **Add your payment gateway credentials** (Chapa)
3. **Configure email settings** if needed
4. **Set up SSL certificate** for production
5. **Configure domain and hosting**

---

## Support

If you encounter issues:

1. Check the Django logs for error messages
2. Verify all dependencies are installed
3. Ensure database is properly configured
4. Test with a fresh virtual environment

The platform is now ready for use! You can register as different user types and explore all features.