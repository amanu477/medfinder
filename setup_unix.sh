#!/bin/bash

echo "========================================"
echo "Ethiopian Pharmacy Platform Setup"
echo "========================================"
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo "Please install Python3 first"
    exit 1
fi

python3 --version
echo

echo "Creating virtual environment..."
python3 -m venv pharmacy_env

echo
echo "Activating virtual environment..."
source pharmacy_env/bin/activate

echo
echo "Upgrading pip..."
python -m pip install --upgrade pip

echo
echo "Installing dependencies..."
pip install -r local_requirements.txt

echo
echo "Creating .env file from example..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit .env file with your database credentials"
else
    echo ".env file already exists"
fi

echo
echo "Running Django migrations..."
python manage.py makemigrations
python manage.py migrate

echo
echo "Creating superuser..."
echo "Please create an admin account:"
python manage.py createsuperuser

echo
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo
echo "Creating test data..."
python create_test_moh_records.py
python create_moh_officer.py
python setup_all_logins.py

echo
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo
echo "To start the server, run:"
echo "  source pharmacy_env/bin/activate"
echo "  python manage.py runserver"
echo
echo "Then visit: http://127.0.0.1:8000/"
echo