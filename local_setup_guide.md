# Pharmacy Connection Platform Local Setup Guide

This guide will help you set up and run the Pharmacy Connection Platform on your local computer without relying on Replit's resources.

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads) (optional, for cloning the repository)
- [PostgreSQL](https://www.postgresql.org/download/) (for the database)

## Step 1: Clone or Download the Project

### Option 1: Download as ZIP
1. Download the project as a ZIP file from Replit
2. Extract the ZIP file to a folder on your computer

### Option 2: Clone with Git
```bash
git clone https://github.com/your-username/pharmacy-finder.git
cd pharmacy-finder
```

## Step 2: Set Up a Virtual Environment

Creating a virtual environment isolates your project dependencies:

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

If you don't have a requirements.txt file, install the packages manually:

```bash
pip install django django-bootstrap5 pillow psycopg2-binary dj-database-url gunicorn
```

## Step 4: Set Up PostgreSQL Database

1. Install PostgreSQL if you haven't already
2. Create a new database for the project:

```sql
CREATE DATABASE pharmacy_db;
CREATE USER pharmacy_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE pharmacy_db TO pharmacy_user;
```

## Step 5: Configure Environment Variables

Create a `.env` file in your project root with the following content:

```
DATABASE_URL=postgres://pharmacy_user:your_password@localhost:5432/pharmacy_db
```

## Step 6: Update Django Settings

Open `pharmacy_finder/settings.py` and make these changes:

1. Update the DATABASES setting to use the environment variable:

```python
import dj_database_url
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}
```

2. Ensure ALLOWED_HOSTS includes 'localhost':

```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

## Step 7: Install python-dotenv

```bash
pip install python-dotenv
```

## Step 8: Migrate the Database

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 9: Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

## Step 10: Run the Development Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser to access the application. The admin interface is at http://127.0.0.1:8000/admin/.

## Project Structure Overview

```
├── customer/               # Customer app (user accounts, prescriptions)
├── pharmacy/               # Pharmacy app (pharmacy accounts, medicines)
├── media/                  # Uploaded files (medicine images, prescriptions)
├── static/                 # Static files (CSS, JS, images)
├── templates/              # HTML templates
├── pharmacy_finder/        # Main project settings
├── manage.py               # Django management script
└── requirements.txt        # Project dependencies
```

## Running Without PostgreSQL (SQLite Alternative)

If you prefer a simpler setup with SQLite:

1. Edit `pharmacy_finder/settings.py` and replace the DATABASES configuration:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

2. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Note: This is recommended for development only, not production.

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Verify database credentials in your .env file
- Check PostgreSQL user permissions

### Media Files Not Displaying
- Ensure MEDIA_URL and MEDIA_ROOT are correctly set in settings.py
- Create the media directories if they don't exist

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Verify STATIC_URL and STATIC_ROOT in settings.py

## Backing Up Your Data

To export your database:

```bash
python manage.py dumpdata > backup.json
```

To import:

```bash
python manage.py loaddata backup.json
```

## Additional Notes

- For production deployment, you would need to configure settings like DEBUG=False, use a production-ready web server like Gunicorn or uWSGI, and set up proper security measures.
- You may need to adjust paths in your templates if you've used absolute URLs pointing to Replit.