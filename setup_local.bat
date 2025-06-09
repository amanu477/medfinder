@echo off
echo Ethiopian Pharmacy Platform - Windows Setup
echo =============================================

echo.
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo Error: Python not found! Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
python -m venv pharmacy_env

echo.
echo Activating virtual environment...
call pharmacy_env\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
pip install -r local_requirements.txt

echo.
echo Creating media directories...
mkdir media\medicines 2>nul
mkdir media\prescriptions 2>nul
mkdir media\pharmacy_documents 2>nul
mkdir media\moh_documents 2>nul

echo.
echo Creating .env file...
if not exist .env (
    echo SECRET_KEY=django-insecure-local-development-key-change-in-production > .env
    echo DEBUG=True >> .env
    echo DATABASE_URL=postgresql://pharmacy_user:pharmacy_password@localhost:5432/pharmacy_platform >> .env
)

echo.
echo =============================================
echo Setup completed! Next steps:
echo 1. Install PostgreSQL from postgresql.org
echo 2. Create database (see LOCAL_SETUP_COMPLETE_GUIDE.md)
echo 3. Run: python manage.py makemigrations
echo 4. Run: python manage.py migrate
echo 5. Run: python manage.py createsuperuser
echo 6. Run: python manage.py runserver
echo =============================================
echo.
pause