# Pharmacy Connection Platform

A comprehensive platform that connects customers with nearby pharmacies, enabling seamless prescription management and medicine procurement through an intuitive interface.

## Project Overview

This pharmacy platform bridges the gap between customers seeking medications and pharmacies that provide them. Key features include:

- **For Customers:**
  - Search for medicines based on name
  - Find nearby pharmacies using geolocation
  - Upload prescriptions directly to pharmacies
  - View medicine details including price and availability

- **For Pharmacies:**
  - Create and manage pharmacy profile
  - Add, edit, and delete medicines
  - Specify if medicines require prescriptions
  - Manage incoming prescription requests
  - Track inventory and expiry dates

## Tech Stack

- **Backend:** Django (Python web framework)
- **Frontend:** HTML, CSS (Bootstrap 5), JavaScript
- **Database:** PostgreSQL
- **Image Handling:** Pillow
- **Geolocation:** Browser's Geolocation API + JavaScript
- **Authentication:** Django's built-in auth system

## Local Development Setup

For detailed setup instructions, see the [Local Setup Guide](local_setup_guide.md).

Quick start:

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment
4. Install dependencies: `pip install -r requirements.txt`
5. Create a PostgreSQL database or use SQLite (see local_settings.py)
6. Apply migrations: `python manage.py migrate`
7. Create superuser: `python manage.py createsuperuser`
8. Run the server: `python manage.py runserver`

## Project Structure

- `customer/` - Customer-related models, views, and functionality
- `pharmacy/` - Pharmacy-related models, views, and functionality
- `pharmacy_finder/` - Project settings and main configuration
- `templates/` - HTML templates
- `static/` - Static assets (CSS, JS, images)
- `media/` - User-uploaded content (medicine images, prescriptions)

## Exporting Data

To export data for local use, run:
```
python export_data.py
python export_media.py
```

This will create a `data_export` directory containing:
- JSON files with database data
- A zip file with media files

## License

This project is open-source and available for educational purposes.

## Authors

Created as a demonstration project for a comprehensive Django web application."# medfinder" 
