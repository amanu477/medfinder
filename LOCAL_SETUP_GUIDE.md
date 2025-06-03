# Local Setup Guide - Pharmacy Connection Platform

This guide will help you download and run the pharmacy connection platform on your local PC.

## Prerequisites

Before starting, ensure you have the following installed on your PC:

### 1. Python 3.8 or higher
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"
- Verify installation: Open Command Prompt and run `python --version`

### 2. Git (Optional but recommended)
- Download from: https://git-scm.com/downloads
- This allows you to easily download and update the code

### 3. PostgreSQL Database
- Download from: https://www.postgresql.org/download/
- During installation, remember the password you set for the 'postgres' user
- Note the port number (default is 5432)

## Step-by-Step Setup

### Step 1: Download the Code

#### Option A: Using Git (Recommended)
1. Open Command Prompt or Terminal
2. Navigate to where you want to store the project:
   ```
   cd C:\Users\YourUsername\Documents
   ```
3. Clone the repository (if available) or download the files manually

#### Option B: Manual Download
1. Download all the project files from your current workspace
2. Extract them to a folder like `C:\Users\YourUsername\Documents\pharmacy-platform`

### Step 2: Set Up Virtual Environment

1. Open Command Prompt and navigate to your project folder:
   ```
   cd C:\Users\YourUsername\Documents\pharmacy-platform
   ```

2. Create a virtual environment:
   ```
   python -m venv pharmacy_env
   ```

3. Activate the virtual environment:
   ```
   # On Windows
   pharmacy_env\Scripts\activate
   
   # On Mac/Linux
   source pharmacy_env/bin/activate
   ```

   You should see `(pharmacy_env)` at the beginning of your command prompt.

### Step 3: Install Required Packages

1. Create a requirements.txt file with the following content:
   ```
   Django==5.2
   psycopg2-binary==2.9.9
   django-bootstrap5==24.2
   Pillow==10.4.0
   gunicorn==23.0.0
   dj-database-url==2.2.0
   ```

2. Install the packages:
   ```
   pip install -r requirements.txt
   ```

### Step 4: Set Up PostgreSQL Database

1. Open pgAdmin or use Command Prompt to connect to PostgreSQL:
   ```
   psql -U postgres
   ```

2. Create a new database:
   ```sql
   CREATE DATABASE pharmacy_db;
   ```

3. Create a user (optional but recommended):
   ```sql
   CREATE USER pharmacy_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE pharmacy_db TO pharmacy_user;
   ```

### Step 5: Configure Environment Variables

1. Create a `.env` file in your project root directory:
   ```
   DATABASE_URL=postgresql://pharmacy_user:your_password@localhost:5432/pharmacy_db
   SECRET_KEY=your-secret-key-here-make-it-long-and-random
   DEBUG=True
   ```

2. If you prefer not to use environment variables, update `pharmacy_finder/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'pharmacy_db',
           'USER': 'pharmacy_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   
   SECRET_KEY = 'your-secret-key-here-make-it-long-and-random'
   DEBUG = True
   ```

### Step 6: Run Database Migrations

1. Make sure you're in the project directory with virtual environment activated
2. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

### Step 7: Create a Superuser (Admin Account)

```
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

### Step 8: Collect Static Files

```
python manage.py collectstatic
```

### Step 9: Run the Development Server

```
python manage.py runserver
```

The application will be available at: http://127.0.0.1:8000/

## File Structure After Setup

```
pharmacy-platform/
├── pharmacy_env/          # Virtual environment (don't commit)
├── customer/              # Customer app
├── pharmacy/              # Pharmacy app
├── pharmacy_finder/       # Main project settings
├── templates/             # HTML templates
├── static/               # CSS, JS files
├── media/                # Uploaded files (created automatically)
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (don't commit)
└── README.md            # Project documentation
```

## Testing the Application

### 1. Access the Admin Panel
- Go to: http://127.0.0.1:8000/admin/
- Login with your superuser credentials
- You can add sample data here

### 2. Test Customer Registration
- Go to: http://127.0.0.1:8000/
- Click on customer registration
- Create a test customer account

### 3. Test Pharmacy Registration
- Go to: http://127.0.0.1:8000/pharmacy/register/
- Create a test pharmacy account
- Add some medicines to test the system

## Troubleshooting

### Common Issues and Solutions

#### 1. "psycopg2" Installation Error
If you get an error installing psycopg2:
```
pip install psycopg2-binary
```

#### 2. Database Connection Error
- Check if PostgreSQL is running
- Verify database credentials in settings
- Ensure the database exists

#### 3. "Port already in use" Error
If port 8000 is busy, use a different port:
```
python manage.py runserver 8080
```

#### 4. Static Files Not Loading
Run:
```
python manage.py collectstatic --clear
```

#### 5. Permission Errors on Windows
Run Command Prompt as Administrator if you encounter permission issues.

### 6. Media Files Directory
Create these directories if they don't exist:
```
mkdir media
mkdir media/medicines
mkdir media/prescriptions
```

## Development Tips

### 1. Database Reset
If you need to reset the database:
```
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

### 2. Adding Sample Data
You can create sample pharmacies and medicines through the admin panel or by creating a Django management command.

### 3. Debugging
- Set `DEBUG = True` in settings.py for development
- Check the terminal output for error messages
- Use Django's built-in error pages for debugging

### 4. Code Changes
The development server automatically reloads when you make changes to Python files. For template changes, refresh your browser.

## Production Deployment

For production deployment, you'll need to:

1. Set `DEBUG = False`
2. Configure proper database settings
3. Set up a web server (Apache/Nginx)
4. Use a WSGI server like Gunicorn
5. Configure static file serving
6. Set up SSL certificates
7. Configure proper backup procedures

## Security Notes

1. Never commit your `.env` file or sensitive credentials
2. Use strong, unique SECRET_KEY for production
3. Keep Django and dependencies updated
4. Use HTTPS in production
5. Regularly backup your database

## Support

If you encounter issues:
1. Check the error messages in the terminal
2. Verify all prerequisites are installed correctly
3. Ensure database is running and accessible
4. Check file permissions
5. Refer to Django documentation for specific errors

The platform includes comprehensive error handling, but proper setup is essential for smooth operation.