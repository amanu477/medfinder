# Ethiopian Pharmacy Platform - Database Installation Guide

## Choose Your Installation Method

### Option 1: SQLite (Recommended for beginners)
```bash
python install_on_local.py
```
**Best for:** Development, testing, learning, quick setup

### Option 2: PostgreSQL (Recommended for production)
```bash
python install_postgresql.py
```
**Best for:** Production use, team development, scalability

---

## Comparison Table

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| **Setup Complexity** | Very Easy | Moderate |
| **Installation Time** | 5-10 minutes | 15-30 minutes |
| **Database Server** | None required | PostgreSQL server required |
| **File Storage** | Single file (db.sqlite3) | Server-based |
| **Performance** | Good for development | Excellent for production |
| **Concurrent Users** | Limited | Unlimited |
| **Backup** | Copy single file | pg_dump/pg_restore |
| **Team Development** | File conflicts possible | Centralized database |
| **Production Ready** | No | Yes |
| **Memory Usage** | Low | Higher |
| **Features** | Basic SQL | Advanced SQL features |

---

## SQLite Installation (Simple)

### What it does:
- ✅ Creates virtual environment
- ✅ Installs all dependencies
- ✅ Sets up SQLite database (single file)
- ✅ Creates admin user
- ✅ Loads sample data
- ✅ Ready to use immediately

### Requirements:
- Python 3.8+
- 500MB disk space
- No additional software needed

### Run:
```bash
python install_on_local.py
```

### Perfect for:
- Learning the platform
- Local development
- Testing features
- Quick demonstrations
- Single-user scenarios

---

## PostgreSQL Installation (Production-Ready)

### What it does:
- ✅ Installs PostgreSQL server
- ✅ Creates database and user
- ✅ Generates secure passwords
- ✅ Sets up virtual environment
- ✅ Installs all dependencies
- ✅ Configures Django for PostgreSQL
- ✅ Creates admin user
- ✅ Loads sample data
- ✅ Tests database connection

### Requirements:
- Python 3.8+
- 1GB disk space
- Admin privileges (for PostgreSQL installation)

### Operating System Support:
- **macOS**: Automatic installation via Homebrew
- **Linux**: Automatic installation via apt
- **Windows**: Manual PostgreSQL installation required

### Run:
```bash
python install_postgresql.py
```

### Perfect for:
- Production deployment
- Team development
- Multiple concurrent users
- Data integrity requirements
- Advanced database features

---

## Detailed PostgreSQL Installation Steps

### Automatic Process:
1. **Checks Python** installation
2. **Installs PostgreSQL** server (macOS/Linux)
3. **Creates database** `pharmacy_platform_db`
4. **Creates user** `pharmacy_user`
5. **Generates secure password** (saved in .env)
6. **Sets up virtual environment**
7. **Installs dependencies** including PostgreSQL adapter
8. **Configures Django** for PostgreSQL
9. **Creates migrations** and applies them
10. **Tests database connection**
11. **Creates admin user** (admin/admin123)
12. **Loads sample data**

### Generated Files:
- `.env` - Database credentials and configuration
- `pharmacy_env/` - Virtual environment
- `media/` - File upload directories
- Database tables in PostgreSQL

### Database Credentials:
After installation, you'll get:
- Database: `pharmacy_platform_db`
- User: `pharmacy_user`
- Password: `[randomly generated]`
- Host: `localhost`
- Port: `5432`

---

## Windows Users - PostgreSQL Setup

**Windows users need to install PostgreSQL manually first:**

1. **Download PostgreSQL:**
   - Visit: https://www.postgresql.org/download/windows/
   - Download PostgreSQL 14 or later
   - Install with default settings
   - Remember the postgres user password

2. **Add PostgreSQL to PATH:**
   - Find PostgreSQL bin directory (usually `C:\Program Files\PostgreSQL\14\bin`)
   - Add to system PATH environment variable

3. **Create database manually:**
   ```cmd
   psql -U postgres
   CREATE DATABASE pharmacy_platform_db;
   CREATE USER pharmacy_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE pharmacy_platform_db TO pharmacy_user;
   \q
   ```

4. **Update .env file:**
   ```
   DATABASE_URL=postgresql://pharmacy_user:your_secure_password@localhost:5432/pharmacy_platform_db
   ```

5. **Run installation:**
   ```cmd
   python install_postgresql.py
   ```

---

## After Installation

### Both installations provide:
- **Admin Dashboard**: http://localhost:8000/admin/ (admin/admin123)
- **Customer Portal**: http://localhost:8000/customer/register/
- **Pharmacy Portal**: http://localhost:8000/pharmacy/register/
- **MoH Portal**: http://localhost:8000/moh/login/
- **Delivery Portal**: http://localhost:8000/delivery/login/

### Start the server:
```bash
# Activate virtual environment first
source pharmacy_env/bin/activate  # Linux/macOS
# or
pharmacy_env\Scripts\activate     # Windows

# Start server
python manage.py runserver
```

---

## Database Management

### SQLite Management:
```bash
# View database
sqlite3 db.sqlite3
.tables
.exit

# Backup
cp db.sqlite3 backup.sqlite3

# Restore
cp backup.sqlite3 db.sqlite3
```

### PostgreSQL Management:
```bash
# Connect to database
psql -h localhost -U pharmacy_user -d pharmacy_platform_db

# Backup
pg_dump -h localhost -U pharmacy_user pharmacy_platform_db > backup.sql

# Restore
psql -h localhost -U pharmacy_user pharmacy_platform_db < backup.sql

# View connections
psql -U postgres -c "SELECT * FROM pg_stat_activity;"
```

---

## Migration Between Databases

### SQLite to PostgreSQL:
1. Export data: `python manage.py dumpdata > data.json`
2. Install PostgreSQL version
3. Import data: `python manage.py loaddata data.json`

### PostgreSQL to SQLite:
1. Export data: `python manage.py dumpdata > data.json`
2. Install SQLite version
3. Import data: `python manage.py loaddata data.json`

---

## Troubleshooting

### Common SQLite Issues:
- **Database locked**: Close all connections, restart server
- **Permissions**: Ensure write access to project directory
- **Corrupted database**: Delete db.sqlite3, run migrations again

### Common PostgreSQL Issues:
- **Connection refused**: Check PostgreSQL service is running
- **Authentication failed**: Verify credentials in .env file
- **Permission denied**: Ensure user has proper database privileges
- **Port in use**: Check if PostgreSQL is running on correct port

### General Solutions:
1. **Check virtual environment**: Ensure it's activated
2. **Verify dependencies**: `pip list` to see installed packages
3. **Check logs**: Django error messages in terminal
4. **Fresh installation**: Delete virtual environment and reinstall

---

## Recommendation

**For beginners**: Start with SQLite installation (`python install_on_local.py`)
- Easier to set up
- No database server management
- Perfect for learning

**For production**: Use PostgreSQL installation (`python install_postgresql.py`)
- Better performance
- Suitable for multiple users
- Production-ready features

**For team development**: PostgreSQL with shared database server
- Centralized data
- No file conflicts
- Better collaboration

Choose based on your needs, and you can always migrate later!