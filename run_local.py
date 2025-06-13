#!/usr/bin/env python
"""
Quick setup script for Ethiopian Pharmacy Platform
Run this after downloading the project to your local machine
"""

import os
import sys
import subprocess
import shutil

def run_command(command, description, capture_output=False):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return False
            return result.stdout
        else:
            subprocess.run(command, shell=True, check=True)
            print(f"✓ {description} completed successfully")
            return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during {description}: {e}")
        return False

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Error: Python 3.8 or higher is required")
        return False
    print(f"✓ Python {version.major}.{version.minor} detected")
    return True

def create_env_file():
    """Create .env file from example"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✓ Created .env file from example")
        else:
            with open('.env', 'w') as f:
                f.write('DEBUG=True\n')
                f.write('SECRET_KEY=django-insecure-local-development-key\n')
                f.write('ALLOWED_HOSTS=localhost,127.0.0.1\n')
            print("✓ Created basic .env file")

def main():
    print("=" * 60)
    print("Ethiopian Pharmacy Platform - Local Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python():
        return
    
    # Create environment file
    create_env_file()
    
    # Install dependencies
    print("\nInstalling dependencies...")
    dependencies = [
        "Django==5.2",
        "Pillow==10.1.0",
        "psycopg2-binary==2.9.7",
        "django-bootstrap5==23.3",
        "gunicorn==21.2.0",
        "dj-database-url==2.1.0",
        "PyJWT==2.8.0"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"Failed to install {dep}. Continue? (y/n): ", end="")
            if input().lower() != 'y':
                return
    
    # Database setup
    print("\nSetting up database...")
    run_command("python manage.py makemigrations", "Creating migrations")
    run_command("python manage.py migrate", "Running migrations")
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    # Create test data
    print("\nCreating test accounts...")
    run_command("python create_moh_officer.py", "Creating MoH officer account")
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nTo start the server:")
    print("python manage.py runserver")
    print("\nAccess URLs:")
    print("- Main site: http://127.0.0.1:8000/")
    print("- MoH Login: http://127.0.0.1:8000/moh/login/")
    print("- Admin: http://127.0.0.1:8000/admin/")
    print("\nDefault MoH Login:")
    print("Username: moh_admin")
    print("Password: moh123")
    print("=" * 60)

if __name__ == "__main__":
    main()