#!/usr/bin/env python3
"""
Ethiopian Pharmacy Platform - Local Installation Script
This script will install and set up the platform on your local computer
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"\n⏳ {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0 and check:
            print(f"❌ Error: {result.stderr}")
            return False
        print(f"✅ {description} completed successfully")
        return True
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def check_python():
    """Check if Python is installed"""
    print("🔍 Checking Python installation...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        python_version = result.stdout.strip()
        print(f"✅ Found {python_version}")
        return True
    except Exception as e:
        print(f"❌ Python not found: {e}")
        return False

def create_virtual_environment():
    """Create and activate virtual environment"""
    print("\n🔧 Creating virtual environment...")
    if not run_command(f"{sys.executable} -m venv pharmacy_env", "Creating virtual environment"):
        return False
    
    # Get activation command
    if os.name == 'nt':  # Windows
        activate_cmd = "pharmacy_env\\Scripts\\activate"
        pip_cmd = "pharmacy_env\\Scripts\\pip"
        python_cmd = "pharmacy_env\\Scripts\\python"
    else:  # Unix/Linux/macOS
        activate_cmd = "source pharmacy_env/bin/activate"
        pip_cmd = "pharmacy_env/bin/pip"
        python_cmd = "pharmacy_env/bin/python"
    
    print(f"✅ Virtual environment created!")
    print(f"📝 To activate later, run: {activate_cmd}")
    
    return pip_cmd, python_cmd

def install_dependencies(pip_cmd):
    """Install all required packages"""
    packages = [
        "django==5.2",
        "pillow",
        "django-bootstrap5",
        "dj-database-url",
        "gunicorn",
        "psycopg2-binary",
        "pytesseract",
        "opencv-python",
        "fuzzywuzzy",
        "python-levenshtein",
        "qrcode[pil]",
        "pyjwt",
        "email-validator",
        "numpy",
        "trafilatura"
    ]
    
    print("\n📦 Installing dependencies...")
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    for package in packages:
        if not run_command(f"{pip_cmd} install {package}", f"Installing {package}"):
            return False
    
    return True

def create_env_file():
    """Create environment configuration file"""
    print("\n⚙️ Creating environment configuration...")
    
    env_content = '''DEBUG=True
SECRET_KEY=your-secret-key-for-local-development-12345
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
'''
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment file created (.env)")

def create_media_directories():
    """Create media directories"""
    print("\n📁 Creating media directories...")
    
    directories = [
        'media/prescriptions',
        'media/pharmacy_documents',
        'media/moh_documents',
        'media/cart_prescriptions',
        'media/order_prescriptions',
        'media/medicines'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Media directories created")

def setup_database(python_cmd):
    """Set up the database"""
    print("\n🗄️ Setting up database...")
    
    # Reset database to avoid migration conflicts
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("✅ Removed existing database")
    
    # Remove old migration files
    migration_dirs = [
        'customer/migrations',
        'pharmacy/migrations',
        'moh/migrations',
        'delivery/migrations'
    ]
    
    for migration_dir in migration_dirs:
        if os.path.exists(migration_dir):
            for file in os.listdir(migration_dir):
                if file.endswith('.py') and file != '__init__.py':
                    os.remove(os.path.join(migration_dir, file))
    
    print("✅ Cleaned old migrations")
    
    # Create fresh migrations
    apps = ['customer', 'pharmacy', 'moh', 'delivery']
    for app in apps:
        if not run_command(f"{python_cmd} manage.py makemigrations {app}", f"Creating {app} migrations"):
            return False
    
    # Apply migrations
    if not run_command(f"{python_cmd} manage.py migrate", "Applying migrations"):
        return False
    
    return True

def create_superuser(python_cmd):
    """Create admin user"""
    print("\n👤 Creating admin user...")
    
    # Create superuser automatically
    admin_script = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✅ Admin user created (username: admin, password: admin123)")
else:
    print("✅ Admin user already exists")
'''
    
    with open('create_admin.py', 'w') as f:
        f.write(admin_script)
    
    run_command(f"{python_cmd} create_admin.py", "Creating admin user")
    os.remove('create_admin.py')

def load_sample_data(python_cmd):
    """Load sample data"""
    print("\n📊 Loading sample data...")
    
    if os.path.exists('load_all_data.py'):
        run_command(f"{python_cmd} load_all_data.py", "Loading sample data", check=False)
    elif os.path.exists('setup_all_logins.py'):
        run_command(f"{python_cmd} setup_all_logins.py", "Setting up test users", check=False)
    else:
        print("ℹ️ No sample data scripts found, skipping...")

def main():
    """Main installation function"""
    print("🚀 Ethiopian Pharmacy Platform - Local Installation")
    print("=" * 50)
    
    # Check Python
    if not check_python():
        print("❌ Please install Python 3.8+ first")
        return False
    
    # Create virtual environment
    pip_cmd, python_cmd = create_virtual_environment()
    if not pip_cmd:
        return False
    
    # Install dependencies
    if not install_dependencies(pip_cmd):
        return False
    
    # Create environment file
    create_env_file()
    
    # Create media directories
    create_media_directories()
    
    # Setup database
    if not setup_database(python_cmd):
        return False
    
    # Create admin user
    create_superuser(python_cmd)
    
    # Load sample data
    load_sample_data(python_cmd)
    
    print("\n🎉 Installation completed successfully!")
    print("=" * 50)
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':
        print("   pharmacy_env\\Scripts\\activate")
    else:
        print("   source pharmacy_env/bin/activate")
    
    print("\n2. Start the server:")
    print(f"   {python_cmd} manage.py runserver")
    
    print("\n3. Open your browser to:")
    print("   http://localhost:8000")
    
    print("\n4. Login accounts:")
    print("   Admin: http://localhost:8000/admin/ (admin/admin123)")
    print("   Customer: http://localhost:8000/customer/register/")
    print("   Pharmacy: http://localhost:8000/pharmacy/register/")
    
    print("\n5. For Tesseract OCR (prescription scanning):")
    print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
    print("   macOS: brew install tesseract")
    print("   Linux: sudo apt install tesseract-ocr")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")