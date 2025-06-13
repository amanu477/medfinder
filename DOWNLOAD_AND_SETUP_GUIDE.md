# Ethiopian Pharmacy Platform - Download & Setup Instructions

## ✅ Complete Steps to Download and Run Locally

### Step 1: Download Project Files
1. **From Replit**: Click the three dots menu → Download as ZIP
2. **Extract** the ZIP file to your desired folder
3. **Open terminal/command prompt** in the extracted folder

### Step 2: Quick Setup (Automated)
```bash
# Run the automated setup script
python run_local.py
```

### Step 3: Manual Setup (If automated fails)

#### Install Python Dependencies:
```bash
pip install Django==5.2
pip install Pillow==10.1.0
pip install psycopg2-binary==2.9.7
pip install django-bootstrap5==23.3
pip install gunicorn==21.2.0
pip install dj-database-url==2.1.0
pip install PyJWT==2.8.0
```

#### Setup Database:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

#### Create Test Accounts:
```bash
python create_moh_officer.py
python manage.py createsuperuser  # Create admin account
```

### Step 4: Run the Application
```bash
python manage.py runserver
```

## 🌐 Access Your Application

- **Main Website**: http://127.0.0.1:8000/
- **MoH Dashboard**: http://127.0.0.1:8000/moh/login/
- **Pharmacy Portal**: http://127.0.0.1:8000/pharmacy/login/
- **Customer Portal**: http://127.0.0.1:8000/customer/register/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 🔐 Default Login Credentials

### MoH Officer Login
- **Username**: `moh_admin`
- **Password**: `moh123`

### Django Admin
- Use the superuser account you created

## 📋 Current System Status

### ✅ Working Features:
- **MoH Dashboard**: Full pharmacy oversight with 5 registered pharmacies
- **Pharmacy Management**: All pharmacies visible without pagination
- **User Authentication**: Multiple user types (Customer, Pharmacy, MoH, Admin)
- **Database**: PostgreSQL compatible with SQLite fallback
- **File Uploads**: Medicine images and pharmacy documents
- **Search & Filtering**: Location-based medicine search

### 📊 Database Contains:
- **5 MoH Verified Pharmacies**:
  - Bethel Medical Pharmacy
  - Green Cross Pharmacy
  - Hope Medical Center Pharmacy
  - Medhanialem Pharmacy
  - Unity Health Pharmacy
- **9 Registered Pharmacies** in main system
- **Sample medicine inventory**
- **Complete user management system**

## 🛠️ Troubleshooting

### Common Issues:

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Issues**: Run migrations if tables are missing
3. **Static Files**: Run `python manage.py collectstatic --noinput`
4. **Permission Errors**: Check file permissions and run as admin if needed

### File Structure:
```
pharmacy_platform/
├── customer/           # Customer management
├── pharmacy/          # Pharmacy operations
├── moh/              # Ministry of Health system
├── platform_admin/   # System administration
├── templates/        # HTML templates
├── static/          # CSS, JS, images
├── media/           # User uploads
├── manage.py        # Django management
├── run_local.py     # Setup script
└── requirements files
```

## 🔧 System Requirements:
- **Python**: 3.8 or higher
- **Database**: SQLite (included) or PostgreSQL
- **OS**: Windows, macOS, or Linux

## 📱 Platform Features:

### Customer Portal:
- Medicine search with location filtering
- Prescription upload and management
- Order tracking and history
- Profile management

### Pharmacy Portal:
- Inventory management
- Prescription processing
- Order fulfillment
- Document verification

### MoH Dashboard:
- Pharmacy licensing verification
- Compliance monitoring
- Inspection management
- Regulatory oversight

### Platform Admin:
- System-wide management
- User administration
- Analytics and reporting
- Security monitoring

## 🚀 Ready for Production:
- Configure PostgreSQL database
- Set DEBUG=False in settings
- Configure web server (nginx/Apache)
- Set up proper domain and SSL
- Configure email settings

The platform is fully functional and ready to use locally!