#!/usr/bin/env python3
"""
Ethiopian Pharmacy Platform - One-Click Local Installation
Run this script to automatically set up the platform on your local computer
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class PharmacyInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.project_dir = Path.cwd()
        self.errors = []
        
    def print_step(self, step, message):
        print(f"\n{'='*60}")
        print(f"STEP {step}: {message}")
        print(f"{'='*60}")
        
    def run_command(self, command, description, critical=True):
        """Run a command and handle errors"""
        print(f"\n🔄 {description}...")
        try:
            result = subprocess.run(command, shell=True, check=True, 
                                 capture_output=True, text=True)
            print(f"✅ {description} completed successfully")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ Error during {description}: {e.stderr}"
            print(error_msg)
            self.errors.append(error_msg)
            if critical:
                return False, None
            return True, None
            
    def check_python(self):
        """Check Python version"""
        self.print_step(1, "Checking Python Installation")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8+ is required")
            print("Please install Python 3.8 or higher from https://python.org/downloads/")
            return False
            
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
        
    def check_postgresql(self):
        """Check PostgreSQL installation"""
        self.print_step(2, "Checking PostgreSQL Installation")
        
        success, _ = self.run_command("psql --version", "Checking PostgreSQL", critical=False)
        if not success:
            print("❌ PostgreSQL not found")
            print("\nPlease install PostgreSQL:")
            if self.system == "windows":
                print("- Download from: https://www.postgresql.org/download/windows/")
            elif self.system == "darwin":
                print("- Run: brew install postgresql@15")
            else:
                print("- Run: sudo apt install postgresql postgresql-contrib")
            return False
            
        print("✅ PostgreSQL is installed")
        return True
        
    def create_virtual_environment(self):
        """Create and activate virtual environment"""
        self.print_step(3, "Setting up Virtual Environment")
        
        venv_path = self.project_dir / "venv"
        if venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
            
        success, _ = self.run_command(f"python -m venv {venv_path}", 
                                    "Creating virtual environment")
        return success
        
    def install_dependencies(self):
        """Install Python dependencies"""
        self.print_step(4, "Installing Dependencies")
        
        # Activate virtual environment
        if self.system == "windows":
            pip_cmd = "venv\\Scripts\\pip"
        else:
            pip_cmd = "venv/bin/pip"
            
        # Upgrade pip
        self.run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
        
        # Install from local requirements
        if (self.project_dir / "local_requirements.txt").exists():
            success, _ = self.run_command(
                f"{pip_cmd} install -r local_requirements.txt",
                "Installing dependencies from local_requirements.txt"
            )
            if success:
                return True
                
        # Fallback to individual packages
        packages = [
            "Django==5.2",
            "Pillow",
            "psycopg2-binary",
            "django-bootstrap5",
            "dj-database-url",
            "gunicorn",
            "PyJWT",
            "pytesseract",
            "opencv-python",
            "fuzzywuzzy",
            "python-levenshtein"
        ]
        
        for package in packages:
            self.run_command(f"{pip_cmd} install {package}", 
                           f"Installing {package}", critical=False)
        
        return True
        
    def setup_database(self):
        """Set up database configuration"""
        self.print_step(5, "Database Configuration")
        
        # Create .env file
        env_path = self.project_dir / ".env"
        if not env_path.exists():
            env_content = """# Database Configuration
DATABASE_URL=postgresql://pharmacy_user:pharmacy123@localhost:5432/pharmacy_platform

# Security
SECRET_KEY=django-insecure-local-development-key-change-in-production
DEBUG=True

# Allowed Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
"""
            with open(env_path, 'w') as f:
                f.write(env_content)
            print("✅ Created .env configuration file")
        
        print("\n📋 Database Setup Instructions:")
        print("1. Open PostgreSQL command line (psql)")
        print("2. Run these commands:")
        print("   CREATE DATABASE pharmacy_platform;")
        print("   CREATE USER pharmacy_user WITH PASSWORD 'pharmacy123';")
        print("   GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;")
        print("   \\q")
        
        response = input("\nHave you completed the database setup? (y/n): ").strip().lower()
        return response == 'y'
        
    def run_migrations(self):
        """Run Django migrations"""
        self.print_step(6, "Setting up Database Tables")
        
        if self.system == "windows":
            python_cmd = "venv\\Scripts\\python"
        else:
            python_cmd = "venv/bin/python"
            
        # Run migrations
        commands = [
            (f"{python_cmd} manage.py makemigrations", "Creating migrations"),
            (f"{python_cmd} manage.py migrate", "Running migrations"),
            (f"{python_cmd} manage.py collectstatic --noinput", "Collecting static files")
        ]
        
        for cmd, desc in commands:
            success, _ = self.run_command(cmd, desc)
            if not success:
                return False
                
        return True
        
    def create_admin_user(self):
        """Create admin user"""
        self.print_step(7, "Creating Admin User")
        
        print("📝 Create an admin user to access the platform:")
        if self.system == "windows":
            python_cmd = "venv\\Scripts\\python"
        else:
            python_cmd = "venv/bin/python"
            
        os.system(f"{python_cmd} manage.py createsuperuser")
        
    def create_media_directories(self):
        """Create media directories"""
        self.print_step(8, "Creating Media Directories")
        
        media_dirs = [
            "media/medicines",
            "media/prescriptions", 
            "media/pharmacy_documents",
            "media/moh_documents",
            "media/order_prescriptions"
        ]
        
        for dir_path in media_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            
        print("✅ Created media directories")
        
    def load_sample_data(self):
        """Load sample data"""
        self.print_step(9, "Loading Sample Data")
        
        if self.system == "windows":
            python_cmd = "venv\\Scripts\\python"
        else:
            python_cmd = "venv/bin/python"
            
        # Load sample data if available
        if (self.project_dir / "load_all_data.py").exists():
            self.run_command(f"{python_cmd} load_all_data.py", 
                           "Loading sample data", critical=False)
            
    def final_instructions(self):
        """Display final instructions"""
        self.print_step(10, "Installation Complete!")
        
        print("🎉 Ethiopian Pharmacy Platform is now installed!")
        print("\n🚀 To start the server:")
        
        if self.system == "windows":
            print("   venv\\Scripts\\python manage.py runserver")
        else:
            print("   venv/bin/python manage.py runserver")
            
        print("\n🌐 Access URLs:")
        print("   Homepage: http://127.0.0.1:8000/")
        print("   Admin Panel: http://127.0.0.1:8000/admin/")
        print("   Customer Register: http://127.0.0.1:8000/customer/register/")
        print("   Pharmacy Register: http://127.0.0.1:8000/pharmacy/register/")
        
        print("\n✨ New Features Available:")
        print("   ✓ Shopping Cart System")
        print("   ✓ Bulk OCR Prescription Verification")
        print("   ✓ Multi-medicine Ordering")
        print("   ✓ Location-based Pharmacy Search")
        
        if self.errors:
            print("\n⚠️  Warnings/Errors encountered:")
            for error in self.errors:
                print(f"   - {error}")
                
    def install(self):
        """Main installation process"""
        print("🏥 Ethiopian Pharmacy Platform - Local Installation")
        print("This script will set up the complete platform on your computer")
        
        steps = [
            self.check_python,
            self.check_postgresql, 
            self.create_virtual_environment,
            self.install_dependencies,
            self.setup_database,
            self.run_migrations,
            self.create_admin_user,
            self.create_media_directories,
            self.load_sample_data,
            self.final_instructions
        ]
        
        for step in steps:
            if not step():
                print("❌ Installation failed. Please check the errors above.")
                return False
                
        return True

def main():
    installer = PharmacyInstaller()
    success = installer.install()
    
    if success:
        print("\n🎉 Installation completed successfully!")
    else:
        print("\n❌ Installation failed. Please check the errors and try again.")
        
if __name__ == "__main__":
    main()