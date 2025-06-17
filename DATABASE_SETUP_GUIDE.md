# Database Setup Guide - PostgreSQL Configuration

## Step 1: Install PostgreSQL

### For Windows:
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer and follow these settings:
   - Port: 5432 (default)
   - Create a password for the `postgres` user (remember this!)
   - Install pgAdmin (database management tool)

### For Mac:
```bash
# Using Homebrew
brew install postgresql
brew services start postgresql
```

### For Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Step 2: Create Database and User

### Method 1: Using pgAdmin (Graphical Interface)
1. Open pgAdmin
2. Connect to PostgreSQL server using your postgres password
3. Right-click "Databases" → Create → Database
4. Name: `pharmacy_platform`
5. Right-click "Login/Group Roles" → Create → Login/Group Role
6. Name: `pharmacy_user`
7. Set password: `your_secure_password`
8. Give privileges to the database

### Method 2: Using Command Line

**Windows (Command Prompt):**
```cmd
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE pharmacy_platform;

# Create user
CREATE USER pharmacy_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;

# Exit
\q
```

**Mac/Linux (Terminal):**
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE pharmacy_platform;

# Create user
CREATE USER pharmacy_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;

# Exit
\q
```

## Step 3: Create .env File

Create a file named `.env` in your project root directory (same folder as manage.py):

```env
# Database Configuration
DATABASE_URL=postgresql://pharmacy_user:your_secure_password@localhost:5432/pharmacy_platform
PGHOST=localhost
PGPORT=5432
PGDATABASE=pharmacy_platform
PGUSER=pharmacy_user
PGPASSWORD=your_secure_password

# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key-here-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Payment Gateway (Optional for testing)
CHAPA_PUBLIC_KEY=CHASECK_TEST-your-test-key
CHAPA_SECRET_KEY=CHASECK_TEST-your-secret-key

# OpenAI API (Optional)
OPENAI_API_KEY=your-openai-api-key-if-needed
```

## Step 4: Test Database Connection

Run this command to test if Django can connect to your database:

```bash
# Activate your virtual environment first
pharmacy_env\Scripts\activate  # Windows
# or
source pharmacy_env/bin/activate  # Mac/Linux

# Test database connection
python manage.py dbshell
```

If successful, you'll see the PostgreSQL prompt. Type `\q` to exit.

## Common Issues and Solutions

### Issue 1: "psql: FATAL: password authentication failed"
**Solution:**
```bash
# Reset postgres user password (Windows)
psql -U postgres
ALTER USER postgres PASSWORD 'newpassword';

# For Mac/Linux
sudo -u postgres psql
ALTER USER postgres PASSWORD 'newpassword';
```

### Issue 2: "psql: could not connect to server"
**Solution:**
```bash
# Check if PostgreSQL is running
# Windows:
sc query postgresql-x64-13
net start postgresql-x64-13

# Mac:
brew services start postgresql

# Linux:
sudo systemctl start postgresql
sudo systemctl status postgresql
```

### Issue 3: "database does not exist"
**Solution:**
Make sure you created the database with the exact same name as in your .env file.

### Issue 4: Connection refused on port 5432
**Solution:**
1. Check if PostgreSQL is running
2. Verify port number in .env matches PostgreSQL configuration
3. Check firewall settings

## Environment Variables Explained

- **DATABASE_URL**: Complete connection string for Django
- **PGHOST**: Database server address (localhost for local installation)
- **PGPORT**: PostgreSQL port (default 5432)
- **PGDATABASE**: Name of your database
- **PGUSER**: Database username you created
- **PGPASSWORD**: Password for the database user
- **DEBUG**: Keep True for development, False for production
- **SECRET_KEY**: Django security key (generate a new one for production)
- **ALLOWED_HOSTS**: Domains allowed to access your app

## Security Notes

1. **Never commit .env file to version control** (it contains passwords)
2. Use strong passwords for database users
3. Change SECRET_KEY for production
4. Set DEBUG=False in production
5. Use environment-specific .env files

## Alternative: SQLite for Testing

If you want to test without PostgreSQL setup, you can temporarily use SQLite:

```env
# Simple SQLite setup (for testing only)
DATABASE_URL=sqlite:///db.sqlite3
DEBUG=True
SECRET_KEY=django-insecure-test-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

However, PostgreSQL is recommended for the full features of this platform.

## Verification Steps

After setup, verify everything works:

```bash
# 1. Test database connection
python manage.py dbshell

# 2. Run migrations
python manage.py makemigrations
python manage.py migrate

# 3. Create admin user
python manage.py createsuperuser

# 4. Test the application
python manage.py runserver
```

Visit http://127.0.0.1:8000/admin/ to verify admin access works.