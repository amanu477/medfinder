@echo off
echo ========================================
echo Ethiopian Pharmacy Platform Setup
echo ========================================
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
python -m venv pharmacy_env

echo.
echo Activating virtual environment...
call pharmacy_env\Scripts\activate

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
pip install -r local_requirements.txt

echo.
echo Creating .env file from example...
if not exist .env (
    copy .env.example .env
    echo Please edit .env file with your database credentials
) else (
    echo .env file already exists
)

echo.
echo Running Django migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo Creating superuser...
echo Please create an admin account:
python manage.py createsuperuser

echo.
echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo Creating test data...
python create_test_moh_records.py
python create_moh_officer.py
python setup_all_logins.py

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the server, run:
echo   pharmacy_env\Scripts\activate
echo   python manage.py runserver
echo.
echo Then visit: http://127.0.0.1:8000/
echo.
pause