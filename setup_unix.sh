#!/bin/bash

echo "Ethiopian Pharmacy Platform - Linux/Mac Setup"
echo "=============================================="

# Function to check command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "ERROR: $1 is not installed"
        return 1
    fi
    return 0
}

# Check Python
echo "Checking Python installation..."
if ! check_command python3; then
    echo "Please install Python 3.8+ first"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "Mac: brew install python"
    exit 1
fi

# Check PostgreSQL
echo "Checking PostgreSQL installation..."
if ! check_command psql; then
    echo "Please install PostgreSQL first"
    echo "Ubuntu/Debian: sudo apt install postgresql postgresql-contrib"
    echo "Mac: brew install postgresql && brew services start postgresql"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv pharmacy_env
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source pharmacy_env/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install Django==5.2
pip install psycopg2-binary==2.9.9
pip install Pillow==10.1.0
pip install django-bootstrap5==23.3
pip install gunicorn==21.2.0
pip install dj-database-url==2.1.0

# Database setup
echo "Setting up database..."
echo "Please enter PostgreSQL password when prompted:"

# For Ubuntu/Debian
if command -v sudo &> /dev/null; then
    sudo -u postgres psql -c "CREATE DATABASE pharmacy_platform;" 2>/dev/null || echo "Database may already exist"
    sudo -u postgres psql -c "CREATE USER pharmacy_user WITH PASSWORD 'pharmacy_password';" 2>/dev/null || echo "User may already exist"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;"
else
    # For Mac
    psql postgres -c "CREATE DATABASE pharmacy_platform;" 2>/dev/null || echo "Database may already exist"
    psql postgres -c "CREATE USER pharmacy_user WITH PASSWORD 'pharmacy_password';" 2>/dev/null || echo "User may already exist"
    psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;"
fi

# Create environment file
echo "Creating environment configuration..."
cat > .env << EOF
DATABASE_URL=postgresql://pharmacy_user:pharmacy_password@localhost:5432/pharmacy_platform
DEBUG=True
SECRET_KEY=your-secret-key-here-change-this
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
EOF

# Database migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "Creating admin account..."
echo "Please create an admin account:"
python manage.py createsuperuser

echo ""
echo "Setup complete!"
echo "==============="
echo "To start the server:"
echo "1. Activate virtual environment: source pharmacy_env/bin/activate"
echo "2. Start server: python manage.py runserver 0.0.0.0:8000"
echo "3. Open http://localhost:8000 in your browser"
echo ""
echo "Admin access: http://localhost:8000/admin/"
echo ""