@echo off
echo Ethiopian Pharmacy Platform - Windows Setup
echo ==========================================

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please download Python from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Checking PostgreSQL installation...
psql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PostgreSQL is not installed or not in PATH
    echo Please download PostgreSQL from https://postgresql.org/download/windows/
    echo Add PostgreSQL bin directory to PATH (usually C:\Program Files\PostgreSQL\15\bin)
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv pharmacy_env
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call pharmacy_env\Scripts\activate.bat

echo Installing dependencies...
pip install Django==5.2
pip install psycopg2-binary==2.9.9
pip install Pillow==10.1.0
pip install django-bootstrap5==23.3
pip install gunicorn==21.2.0
pip install dj-database-url==2.1.0

echo Creating database...
echo Please enter PostgreSQL password when prompted:
psql -U postgres -c "CREATE DATABASE pharmacy_platform;"
psql -U postgres -c "CREATE USER pharmacy_user WITH PASSWORD 'pharmacy_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;"

echo Creating environment file...
echo DATABASE_URL=postgresql://pharmacy_user:pharmacy_password@localhost:5432/pharmacy_platform > .env
echo DEBUG=True >> .env
echo SECRET_KEY=your-secret-key-here-change-this >> .env
echo ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0 >> .env

echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

echo Creating superuser...
echo Please create an admin account:
python manage.py createsuperuser

echo Setup complete!
echo To start the server, run: python manage.py runserver 0.0.0.0:8000
echo Then open http://localhost:8000 in your browser
pause