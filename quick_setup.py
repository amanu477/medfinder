#!/usr/bin/env python3
"""
Quick Setup Script for Ethiopian Pharmacy Platform
Automates the installation process for local development
"""

import os
import sys
import subprocess
import platform

def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        else:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout}")
        return True
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def check_python():
    """Check if Python is installed"""
    print("🐍 Checking Python installation...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python found: {result.stdout.strip()}")
        return True
    except:
        print("❌ Python not found. Please install Python 3.8+ first.")
        return False

def create_virtual_environment():
    """Create virtual environment"""
    venv_name = "pharmacy_env"
    if os.path.exists(venv_name):
        print(f"📁 Virtual environment '{venv_name}' already exists")
        return True
    
    return run_command(f"{sys.executable} -m venv {venv_name}", "Creating virtual environment")

def get_activation_command():
    """Get the correct activation command for the platform"""
    if platform.system() == "Windows":
        return "pharmacy_env\\Scripts\\activate"
    else:
        return "source pharmacy_env/bin/activate"

def install_dependencies():
    """Install Python dependencies"""
    # Get the correct pip path
    if platform.system() == "Windows":
        pip_path = "pharmacy_env\\Scripts\\pip"
    else:
        pip_path = "pharmacy_env/bin/pip"
    
    dependencies = [
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
    
    print("📦 Installing dependencies...")
    for dep in dependencies:
        if not run_command(f"{pip_path} install {dep}", f"Installing {dep}"):
            return False
    
    return True

def setup_database():
    """Set up the database"""
    # Get the correct python path
    if platform.system() == "Windows":
        python_path = "pharmacy_env\\Scripts\\python"
    else:
        python_path = "pharmacy_env/bin/python"
    
    commands = [
        f"{python_path} manage.py makemigrations",
        f"{python_path} manage.py migrate",
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Running: {cmd}"):
            return False
    
    return True

def create_env_file():
    """Create environment file"""
    env_content = """DEBUG=True
SECRET_KEY=django-insecure-local-development-key-change-in-production
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Environment file created")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def create_media_directories():
    """Create media directories"""
    directories = [
        "media/prescriptions",
        "media/pharmacy_documents", 
        "media/moh_documents",
        "media/cart_prescriptions",
        "media/order_prescriptions",
        "media/medicines"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Media directories created")
    return True

def load_sample_data():
    """Load sample data"""
    # Get the correct python path
    if platform.system() == "Windows":
        python_path = "pharmacy_env\\Scripts\\python"
    else:
        python_path = "pharmacy_env/bin/python"
    
    print("📊 Loading sample data...")
    run_command(f"{python_path} setup_all_logins.py", "Loading test users", check=False)
    run_command(f"{python_path} load_all_data.py", "Loading sample data", check=False)
    
    return True

def main():
    """Main setup function"""
    print("🚀 Ethiopian Pharmacy Platform - Quick Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Create virtual environment", create_virtual_environment),
        ("Install dependencies", install_dependencies),
        ("Create environment file", create_env_file),
        ("Create media directories", create_media_directories),
        ("Set up database", setup_database),
        ("Load sample data", load_sample_data),
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        if not step_function():
            failed_steps.append(step_name)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 Setup Summary")
    print("=" * 50)
    
    if failed_steps:
        print("❌ Some steps failed:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\nPlease check the errors above and run the setup again.")
    else:
        print("✅ All setup steps completed successfully!")
        
        print("\n🚀 Next Steps:")
        print("1. Activate virtual environment:")
        print(f"   {get_activation_command()}")
        print("\n2. Start the development server:")
        if platform.system() == "Windows":
            print("   pharmacy_env\\Scripts\\python manage.py runserver")
        else:
            print("   pharmacy_env/bin/python manage.py runserver")
        print("\n3. Open your browser and go to:")
        print("   http://localhost:8000")
        print("\n4. Try these login credentials:")
        print("   - Admin: admin/admin123")
        print("   - Customer: testcustomer/testpass123")
        print("   - Pharmacy: testpharmacy/testpass123")
        
        print("\n📚 For detailed documentation, see:")
        print("   - COMPLETE_INSTALLATION_GUIDE.md")
        print("   - README.md")

if __name__ == "__main__":
    main()