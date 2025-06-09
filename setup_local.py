#!/usr/bin/env python3
"""
Local setup script for Ethiopian Pharmacy Platform
Run this script to set up the project on your local machine
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor} detected")
        return True
    else:
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False

def create_env_file():
    """Create .env file with default settings"""
    env_content = """# Django Settings
SECRET_KEY=django-insecure-local-development-key-change-in-production
DEBUG=True

# Database Settings
DATABASE_URL=postgresql://pharmacy_user:pharmacy_password@localhost:5432/pharmacy_platform

# Email Settings (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with default settings")
    else:
        print("ℹ️  .env file already exists")

def setup_database():
    """Provide database setup instructions"""
    print("\n📊 Database Setup Instructions:")
    print("1. Install PostgreSQL from https://www.postgresql.org/download/")
    print("2. Create database and user:")
    print("   psql -U postgres")
    print("   CREATE DATABASE pharmacy_platform;")
    print("   CREATE USER pharmacy_user WITH PASSWORD 'pharmacy_password';")
    print("   GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;")
    print("   \\q")

def main():
    """Main setup function"""
    print("🏥 Ethiopian Pharmacy Platform - Local Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not sys.base_prefix != sys.prefix:
        print("\n⚠️  Virtual environment not detected!")
        print("Please create and activate a virtual environment:")
        if platform.system() == "Windows":
            print("  python -m venv pharmacy_env")
            print("  pharmacy_env\\Scripts\\activate")
        else:
            print("  python -m venv pharmacy_env")
            print("  source pharmacy_env/bin/activate")
        print("Then run this script again.")
        return False
    
    print("✅ Virtual environment detected")
    
    # Install dependencies
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command("pip install -r local_requirements.txt", "Installing dependencies"):
        return False
    
    # Create .env file
    create_env_file()
    
    # Create media directories
    media_dirs = ['media/medicines', 'media/prescriptions', 
                  'media/pharmacy_documents', 'media/moh_documents']
    
    for directory in media_dirs:
        os.makedirs(directory, exist_ok=True)
    print("✅ Created media directories")
    
    # Database setup instructions
    setup_database()
    
    print("\n🎉 Setup completed! Next steps:")
    print("1. Set up PostgreSQL database (see instructions above)")
    print("2. Update .env file with your database credentials")
    print("3. Run database migrations:")
    print("   python manage.py makemigrations")
    print("   python manage.py migrate")
    print("4. Create superuser:")
    print("   python manage.py createsuperuser")
    print("5. Start the development server:")
    print("   python manage.py runserver")
    print("\n📖 For detailed instructions, see LOCAL_SETUP_COMPLETE_GUIDE.md")

if __name__ == "__main__":
    main()