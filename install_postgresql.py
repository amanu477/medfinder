#!/usr/bin/env python3
"""
Ethiopian Pharmacy Platform - PostgreSQL Installation Script
This script will install and set up the platform with PostgreSQL database
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import secrets
import string

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

def generate_secret_key():
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for _ in range(50))

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

def install_postgresql():
    """Install PostgreSQL based on operating system"""
    print("\n🗄️ Installing PostgreSQL...")
    
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("Installing PostgreSQL on macOS...")
        if not run_command("brew --version", "Checking Homebrew", check=False):
            print("Installing Homebrew first...")
            homebrew_install = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            if not run_command(homebrew_install, "Installing Homebrew"):
                return False
        
        if not run_command("brew install postgresql@14", "Installing PostgreSQL"):
            return False
        if not run_command("brew services start postgresql@14", "Starting PostgreSQL service"):
            return False
            
    elif system == "linux":  # Linux
        print("Installing PostgreSQL on Linux...")
        if not run_command("sudo apt update", "Updating package list"):
            return False
        if not run_command("sudo apt install -y postgresql postgresql-contrib", "Installing PostgreSQL"):
            return False
        if not run_command("sudo systemctl start postgresql", "Starting PostgreSQL service"):
            return False
        if not run_command("sudo systemctl enable postgresql", "Enabling PostgreSQL service"):
            return False
            
    elif system == "windows":  # Windows
        print("❌ Windows users: Please install PostgreSQL manually from:")
        print("   https://www.postgresql.org/download/windows/")
        print("   Then run this script again.")
        return False
        
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False
    
    return True

def setup_postgresql_database():
    """Set up PostgreSQL database and user"""
    print("\n🔧 Setting up PostgreSQL database...")
    
    db_name = "pharmacy_platform_db"
    db_user = "pharmacy_user"
    db_password = generate_secret_key()[:16]  # Use first 16 chars for password
    
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        # Create database and user
        commands = [
            f'psql postgres -c "CREATE DATABASE {db_name};"',
            f'psql postgres -c "CREATE USER {db_user} WITH PASSWORD \'{db_password}\';"',
            f'psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"',
            f'psql postgres -c "ALTER USER {db_user} CREATEDB;"'
        ]
        
        for cmd in commands:
            if not run_command(cmd, f"Executing: {cmd.split('-c')[1]}", check=False):
                print(f"⚠️ Command may have failed, continuing...")
    
    elif system == "linux":  # Linux
        # Create database and user
        commands = [
            f'sudo -u postgres psql -c "CREATE DATABASE {db_name};"',
            f'sudo -u postgres psql -c "CREATE USER {db_user} WITH PASSWORD \'{db_password}\';"',
            f'sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"',
            f'sudo -u postgres psql -c "ALTER USER {db_user} CREATEDB;"'
        ]
        
        for cmd in commands:
            if not run_command(cmd, f"Executing database setup", check=False):
                print(f"⚠️ Command may have failed, continuing...")
    
    print(f"✅ Database setup completed")
    print(f"   Database: {db_name}")
    print(f"   User: {db_user}")
    print(f"   Password: {db_password}")
    
    return db_name, db_user, db_password

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
    """Install all required packages including PostgreSQL adapter"""
    packages = [
        "django==5.2",
        "pillow",
        "django-bootstrap5",
        "dj-database-url",
        "gunicorn",
        "psycopg2-binary",  # PostgreSQL adapter
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

def create_env_file(db_name, db_user, db_password):
    """Create environment configuration file with PostgreSQL"""
    print("\n⚙️ Creating environment configuration...")
    
    secret_key = generate_secret_key()
    database_url = f"postgresql://{db_user}:{db_password}@localhost:5432/{db_name}"
    
    env_content = f'''DEBUG=True
SECRET_KEY={secret_key}
DATABASE_URL={database_url}
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB={db_name}
POSTGRES_USER={db_user}
POSTGRES_PASSWORD={db_password}
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
'''
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment file created (.env)")
    print(f"   Database URL: {database_url}")

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
    """Set up the Django database"""
    print("\n🗄️ Setting up Django database...")
    
    # Clean start
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("✅ Removed any existing SQLite database")
    
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
    User.objects.create_superuser('admin', 'admin@pharmacy.com', 'admin123')
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
        run_command(f"{python_cmd} load_all_data.py", "Loading comprehensive sample data", check=False)
    elif os.path.exists('setup_all_logins.py'):
        run_command(f"{python_cmd} setup_all_logins.py", "Setting up test users", check=False)
    else:
        print("ℹ️ No sample data scripts found, skipping...")

def test_database_connection(python_cmd):
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    test_script = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_finder.settings')
django.setup()

from django.db import connection

try:
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("✅ Database connection successful")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
'''
    
    with open('test_db.py', 'w') as f:
        f.write(test_script)
    
    run_command(f"{python_cmd} test_db.py", "Testing database connection")
    os.remove('test_db.py')

def main():
    """Main installation function"""
    print("🚀 Ethiopian Pharmacy Platform - PostgreSQL Installation")
    print("=" * 55)
    
    # Check Python
    if not check_python():
        print("❌ Please install Python 3.8+ first")
        return False
    
    # Install PostgreSQL
    if not install_postgresql():
        print("❌ PostgreSQL installation failed")
        return False
    
    # Setup PostgreSQL database
    db_name, db_user, db_password = setup_postgresql_database()
    
    # Create virtual environment
    pip_cmd, python_cmd = create_virtual_environment()
    if not pip_cmd:
        return False
    
    # Install dependencies
    if not install_dependencies(pip_cmd):
        return False
    
    # Create environment file
    create_env_file(db_name, db_user, db_password)
    
    # Create media directories
    create_media_directories()
    
    # Setup Django database
    if not setup_database(python_cmd):
        return False
    
    # Test database connection
    test_database_connection(python_cmd)
    
    # Create admin user
    create_superuser(python_cmd)
    
    # Load sample data
    load_sample_data(python_cmd)
    
    print("\n🎉 PostgreSQL Installation completed successfully!")
    print("=" * 55)
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
    
    print("\n📊 Database Information:")
    print(f"   Database: {db_name}")
    print(f"   User: {db_user}")
    print(f"   Password: {db_password}")
    print(f"   Host: localhost")
    print(f"   Port: 5432")
    
    print("\n🔧 PostgreSQL Management:")
    print("   Connect: psql -h localhost -U {db_user} -d {db_name}")
    print("   Backup: pg_dump -h localhost -U {db_user} {db_name} > backup.sql")
    print("   Restore: psql -h localhost -U {db_user} {db_name} < backup.sql")
    
    print("\n📁 Database credentials saved in .env file")
    print("   Keep this file secure and never commit it to version control")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")