#!/bin/bash

echo "🏥 Ethiopian Pharmacy Platform - Linux/macOS Setup"
echo "=================================================="

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.8+"
    exit 1
fi

python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv pharmacy_env

# Activate virtual environment
echo "Activating virtual environment..."
source pharmacy_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r local_requirements.txt

# Create media directories
echo "Creating media directories..."
mkdir -p media/medicines
mkdir -p media/prescriptions
mkdir -p media/pharmacy_documents
mkdir -p media/moh_documents

# Create .env file
echo "Creating .env file..."
if [ ! -f .env ]; then
    cat > .env << EOL
SECRET_KEY=django-insecure-local-development-key-change-in-production
DEBUG=True
DATABASE_URL=postgresql://pharmacy_user:pharmacy_password@localhost:5432/pharmacy_platform
EOL
fi

echo ""
echo "🎉 Setup completed! Next steps:"
echo "1. Install PostgreSQL"
echo "2. Create database (see LOCAL_SETUP_COMPLETE_GUIDE.md)"
echo "3. Run: python manage.py makemigrations"
echo "4. Run: python manage.py migrate"
echo "5. Run: python manage.py createsuperuser"
echo "6. Run: python manage.py runserver"
echo ""
echo "📖 For detailed instructions, see LOCAL_SETUP_COMPLETE_GUIDE.md"