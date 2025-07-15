#!/usr/bin/env python3
"""
Ethiopian Pharmacy Platform - Complete Setup Script
Run this script to install everything automatically
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import secrets
import string

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_step(step, text):
    """Print a formatted step"""
    print(f"\n[{step}] {text}")

def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"   → {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0 and check:
            print(f"   ✗ Error: {result.stderr}")
            return False
        print(f"   ✓ {description} completed")
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def check_python():
    """Check Python installation"""
    print_step("1", "Checking Python installation")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"   ✓ Found {version}")
        return True
    except:
        print("   ✗ Python not found")
        return False

def choose_database():
    """Let user choose database type"""
    print_step("2", "Choose Database Type")
    print("   1. SQLite (Recommended for beginners)")
    print("      - No setup required")
    print("      - Single file database")
    print("      - Perfect for development")
    print()
    print("   2. PostgreSQL (Recommended for production)")
    print("      - Requires PostgreSQL installation")
    print("      - Better performance")
    print("      - Production ready")
    print()
    
    while True:
        choice = input("   Choose database (1 or 2): ").strip()
        if choice in ['1', '2']:
            return choice
        print("   Please enter 1 or 2")

def setup_virtual_environment():
    """Create virtual environment"""
    print_step("3", "Setting up virtual environment")
    
    if not run_command(f"{sys.executable} -m venv pharmacy_env", "Creating virtual environment"):
        return False
    
    # Get commands for this platform
    if platform.system() == "Windows":
        activate_cmd = "pharmacy_env\\Scripts\\activate"
        pip_cmd = "pharmacy_env\\Scripts\\pip"
        python_cmd = "pharmacy_env\\Scripts\\python"
    else:
        activate_cmd = "source pharmacy_env/bin/activate"
        pip_cmd = "pharmacy_env/bin/pip"
        python_cmd = "pharmacy_env/bin/python"
    
    print(f"   ✓ Virtual environment created")
    print(f"   ✓ To activate later: {activate_cmd}")
    return pip_cmd, python_cmd

def install_dependencies(pip_cmd):
    """Install Python dependencies"""
    print_step("4", "Installing Python dependencies")
    
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
    
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    for package in packages:
        if not run_command(f"{pip_cmd} install {package}", f"Installing {package}"):
            return False
    
    return True

def create_env_file(db_choice):
    """Create environment configuration file"""
    print_step("5", "Creating environment configuration")
    
    secret_key = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*(-_=+)') for _ in range(50))
    
    if db_choice == "1":  # SQLite
        database_url = "sqlite:///db.sqlite3"
        print("   ✓ Configured for SQLite database")
    else:  # PostgreSQL
        database_url = "postgresql://pharmacy_user:secure_password@localhost:5432/pharmacy_db"
        print("   ✓ Configured for PostgreSQL database")
        print("   ⚠ You need to set up PostgreSQL database manually")
    
    env_content = f"""DEBUG=True
SECRET_KEY={secret_key}
DATABASE_URL={database_url}
ALLOWED_HOSTS=localhost,127.0.0.1
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("   ✓ Environment file created (.env)")
    return database_url

def create_directories():
    """Create media directories"""
    print_step("6", "Creating media directories")
    
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
    
    print("   ✓ Media directories created")

def setup_database(python_cmd, db_choice):
    """Set up database"""
    print_step("7", "Setting up database")
    
    # Clean start
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("   ✓ Removed existing SQLite database")
    
    # Clean old migrations
    migration_dirs = ['customer/migrations', 'pharmacy/migrations', 'moh/migrations', 'delivery/migrations']
    for migration_dir in migration_dirs:
        if os.path.exists(migration_dir):
            for file in os.listdir(migration_dir):
                if file.endswith('.py') and file != '__init__.py':
                    os.remove(os.path.join(migration_dir, file))
    
    print("   ✓ Cleaned old migrations")
    
    # Create fresh migrations
    apps = ['customer', 'pharmacy', 'moh', 'delivery']
    for app in apps:
        if not run_command(f"{python_cmd} manage.py makemigrations {app}", f"Creating {app} migrations"):
            return False
    
    # Apply migrations
    if not run_command(f"{python_cmd} manage.py migrate", "Applying database migrations"):
        return False
    
    return True

def create_admin_user(python_cmd):
    """Create admin user"""
    print_step("8", "Creating admin user")
    
    admin_script = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@pharmacy.com', 'admin123')
    print("Admin user created successfully")
else:
    print("Admin user already exists")
'''
    
    with open('create_admin_temp.py', 'w') as f:
        f.write(admin_script)
    
    run_command(f"{python_cmd} create_admin_temp.py", "Creating admin user")
    os.remove('create_admin_temp.py')
    
    print("   ✓ Admin user: admin / admin123")

def load_sample_data(python_cmd):
    """Load sample data"""
    print_step("9", "Loading sample data")
    
    if os.path.exists('load_all_data.py'):
        run_command(f"{python_cmd} load_all_data.py", "Loading comprehensive sample data", check=False)
    elif os.path.exists('setup_all_logins.py'):
        run_command(f"{python_cmd} setup_all_logins.py", "Creating test user accounts", check=False)
    else:
        print("   ℹ Sample data scripts not found, skipping")

def show_instructions(python_cmd, database_url, db_choice):
    """Show final instructions"""
    print_header("Installation Complete!")
    
    print("\n🎉 Ethiopian Pharmacy Platform is ready!")
    print("\n📋 Next Steps:")
    print("   1. Start the server:")
    print(f"      {python_cmd} manage.py runserver")
    print("\n   2. Open your browser:")
    print("      http://localhost:8000")
    
    print("\n🔑 Login Accounts:")
    print("   • Admin Dashboard: http://localhost:8000/admin/")
    print("     Username: admin, Password: admin123")
    print("   • Customer Portal: http://localhost:8000/customer/register/")
    print("   • Pharmacy Portal: http://localhost:8000/pharmacy/register/")
    print("   • MoH Portal: http://localhost:8000/moh/login/")
    print("   • Delivery Portal: http://localhost:8000/delivery/login/")
    
    print("\n💾 Database Information:")
    if db_choice == "1":
        print("   • Type: SQLite")
        print("   • Location: db.sqlite3")
        print("   • Backup: Copy db.sqlite3 file")
    else:
        print("   • Type: PostgreSQL")
        print("   • URL: postgresql://pharmacy_user:secure_password@localhost:5432/pharmacy_db")
        print("   • Setup Required: Create database manually")
    
    print("\n🔧 Optional: Install Tesseract OCR for prescription scanning")
    print("   • Windows: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   • macOS: brew install tesseract")
    print("   • Linux: sudo apt install tesseract-ocr")
    
    print("\n📁 Project Structure:")
    print("   • Virtual Environment: pharmacy_env/")
    print("   • Database: db.sqlite3 (if SQLite)")
    print("   • Media Files: media/")
    print("   • Configuration: .env")
    
    print("\n✨ Platform Features:")
    print("   • Medicine search and ordering")
    print("   • Prescription OCR validation")
    print("   • Shopping cart and checkout")
    print("   • Payment integration (Chapa + Cash)")
    print("   • Delivery tracking with QR codes")
    print("   • Multi-user management system")
    print("   • Ethiopian timezone support")
    
    print("\n🚀 The platform is ready for use!")

def main():
    """Main installation function"""
    print_header("Ethiopian Pharmacy Platform - Complete Setup")
    print("Welcome! This script will install everything automatically.")
    
    # Check Python
    if not check_python():
        print("❌ Please install Python 3.8+ first")
        return False
    
    # Choose database
    db_choice = choose_database()
    
    # Setup virtual environment
    result = setup_virtual_environment()
    if not result:
        return False
    pip_cmd, python_cmd = result
    
    # Install dependencies
    if not install_dependencies(pip_cmd):
        return False
    
    # Create environment file
    database_url = create_env_file(db_choice)
    
    # Create directories
    create_directories()
    
    # Setup database
    if not setup_database(python_cmd, db_choice):
        return False
    
    # Create admin user
    create_admin_user(python_cmd)
    
    # Load sample data
    load_sample_data(python_cmd)
    
    # Show instructions
    show_instructions(python_cmd, database_url, db_choice)
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        print("Please check the error and try again")