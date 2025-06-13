# Ethiopian Pharmacy Platform - Complete Local Setup Guide

## System Requirements
- Python 3.8 or higher
- PostgreSQL 12+ (recommended) or SQLite for development
- Git

## Step 1: Download and Extract Project
1. Download the project files from Replit
2. Extract to your desired folder (e.g., `pharmacy_platform`)
3. Open terminal/command prompt in the project folder

## Step 2: Create Virtual Environment
```bash
# Windows
python -m venv pharmacy_env
pharmacy_env\Scripts\activate

# macOS/Linux
python3 -m venv pharmacy_env
source pharmacy_env/bin/activate
```

## Step 3: Install Dependencies
```bash
pip install Django==5.2
pip install Pillow==10.1.0
pip install psycopg2-binary==2.9.7
pip install django-bootstrap5==23.3
pip install gunicorn==21.2.0
pip install dj-database-url==2.1.0
pip install PyJWT==2.8.0
```

## Step 4: Database Setup

### Option A: SQLite (Easiest for Development)
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### Option B: PostgreSQL (Recommended for Production)
1. Install PostgreSQL on your system
2. Create database:
```sql
CREATE DATABASE pharmacy_platform;
CREATE USER pharmacy_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform TO pharmacy_user;
```

3. Create `.env` file in project root:
```env
DATABASE_URL=postgresql://pharmacy_user:your_password@localhost:5432/pharmacy_platform
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

4. Run migrations:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## Step 5: Create Superuser and Test Accounts
```bash
# Create Django superuser
python manage.py createsuperuser

# Create MoH officer account
python create_moh_officer.py
```

## Step 6: Run the Server
```bash
python manage.py runserver
```

## Step 7: Access the Platform
- Main site: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/
- MoH Dashboard: http://127.0.0.1:8000/moh/login/
- Pharmacy Portal: http://127.0.0.1:8000/pharmacy/login/
- Customer Portal: http://127.0.0.1:8000/customer/register/

## Default Test Accounts

### MoH Officer
- Username: `moh_admin`
- Password: `moh123`

### Admin Access
- Use the superuser account you created

## Platform Features

### Customer Portal
- Medicine search with location-based results
- Prescription upload and management
- Order tracking
- Profile management

### Pharmacy Portal
- Inventory management
- Prescription processing
- Order fulfillment
- Document verification

### MoH Dashboard
- Pharmacy licensing and verification
- Compliance monitoring
- Regulatory oversight
- Inspection management

### Platform Admin
- System-wide oversight
- User management
- Analytics and reporting

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify database credentials in `.env`
   - Ensure database exists

2. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Permission Errors**
   - Ensure proper file permissions
   - Run as administrator if needed

4. **Import Errors**
   - Verify all dependencies installed
   - Check Python path

### File Structure
```
pharmacy_platform/
├── customer/           # Customer app
├── pharmacy/          # Pharmacy app  
├── moh/              # Ministry of Health app
├── platform_admin/   # Platform admin app
├── pharmacy_finder/   # Main Django project
├── templates/        # HTML templates
├── static/          # Static files (CSS, JS, images)
├── media/           # User uploaded files
├── manage.py        # Django management script
└── requirements files
```

## Security Notes
- Change SECRET_KEY in production
- Use strong passwords
- Configure proper ALLOWED_HOSTS
- Enable HTTPS in production
- Regular security updates

## Support
For issues or questions:
1. Check Django documentation
2. Verify all dependencies installed
3. Check error logs in terminal
4. Ensure database is accessible

## Production Deployment
- Use PostgreSQL database
- Configure proper web server (nginx/Apache)
- Set DEBUG=False
- Configure email settings
- Set up proper logging
- Use environment variables for secrets