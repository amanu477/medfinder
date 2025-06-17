# Database Setup on Your PC - Simple Guide

## Step 1: Download PostgreSQL

1. Go to: https://www.postgresql.org/download/windows/
2. Click "Download the installer"
3. Download the latest version for Windows
4. Run the installer

**During Installation:**
- Keep all default settings
- When asked for password, enter: `postgres123` (write this down!)
- Port: 5432
- Install pgAdmin when offered

## Step 2: Create Databases

**Option A - Using pgAdmin (Easier):**

1. Open pgAdmin from Start Menu
2. Enter password: `postgres123`
3. Right-click "Databases" → Create → Database...
4. Name: `pharmacy_platform` → Save
5. Right-click "Databases" → Create → Database...
6. Name: `pharmacy_platform_moh` → Save
7. Right-click "Login/Group Roles" → Create → Login/Group Role...
8. Name: `pharmacy_user`
9. Go to "Definition" tab → Password: `mypassword123`
10. Go to "Privileges" tab → Check "Can login?"
11. Save

**Option B - Command Line:**

1. Press Windows Key + R
2. Type `cmd` and press Enter
3. Type these commands:

```cmd
psql -U postgres
```
Enter password: `postgres123`

```sql
CREATE DATABASE pharmacy_platform;
CREATE DATABASE pharmacy_platform_moh;
CREATE USER pharmacy_user WITH PASSWORD 'mypassword123';
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform_moh TO pharmacy_user;
\q
```

## Step 3: Update Your Project Settings

1. Open your project folder
2. Open `pharmacy_finder/settings.py` in a text editor
3. Find the `DATABASES` section (around line 110-130)
4. Change this line:
```python
'PASSWORD': 'your_database_password',
```
To:
```python
'PASSWORD': 'mypassword123',
```

Save the file.

## Step 4: Test Your Setup

1. Open Command Prompt in your project folder
2. Activate your virtual environment:
```cmd
pharmacy_env\Scripts\activate
```

3. Test database connection:
```cmd
python manage.py dbshell
```

If you see `pharmacy_platform=#` then it worked! Type `\q` to exit.

4. Run Django setup:
```cmd
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. Start the server:
```cmd
python manage.py runserver
```

## If You Get Errors:

**"psql: could not connect":**
- Check if PostgreSQL is running
- Go to Services (Windows Key + R, type `services.msc`)
- Find "postgresql" service and start it

**"password authentication failed":**
- Double-check you used the correct passwords
- Make sure you created the `pharmacy_user` with the right password

**"database does not exist":**
- Make sure you created both databases with exact names:
  - `pharmacy_platform`
  - `pharmacy_platform_moh`

## Summary of What You Need:

1. **PostgreSQL installed** with password: `postgres123`
2. **Two databases created:**
   - pharmacy_platform
   - pharmacy_platform_moh
3. **User created:** pharmacy_user with password: `mypassword123`
4. **Settings.py updated** with the password `mypassword123`

That's it! Your database is ready to use.