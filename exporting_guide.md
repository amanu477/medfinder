# Exporting the Pharmacy Connection Platform

This guide will show you how to export your Pharmacy Connection Platform project to run on your local PC.

## Step 1: Export Project Files

1. **Download as ZIP**:
   - Download the project files from your development environment
   - Save the ZIP file to your computer

2. **Extract the ZIP file**:
   - Right-click on the downloaded ZIP file
   - Select "Extract All" (Windows) or use your preferred extraction tool
   - Choose a location to extract the files

## Step 2: Export Database Data

1. **Run the export_data.py script**:
   
   ```bash
   python export_data.py
   ```

   This will create a `data_export` folder containing JSON files with all your database data.

2. **Export media files** (images):

   ```bash
   python export_media.py
   ```

   This will create a ZIP file in the `data_export` folder containing all your media files.

## Step 3: Setting Up Local Environment

1. Follow the instructions in the [Local Setup Guide](local_setup_guide.md) to set up your local environment.

2. **Import data** after completing the local setup:

   ```bash
   # Navigate to your local project directory
   cd path/to/your/project

   # Import the database data
   python manage.py loaddata data_export/all_data.json
   ```

3. **Import media files**:
   - Extract the media files ZIP from `data_export/media_files_*.zip`
   - Copy the extracted files to the `media` directory in your local project

## Step 4: Test Your Local Setup

1. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

2. **Access the application** in your browser:
   - Open http://127.0.0.1:8000/

3. **Test all features** to ensure they work correctly:
   - Pharmacy login and registration
   - Medicine management
   - Customer search functionality
   - Prescription uploads

## Troubleshooting Common Issues

### Missing Dependencies

If you encounter errors about missing modules, make sure you've installed all dependencies:

```bash
pip install django django-bootstrap5 pillow psycopg2-binary dj-database-url gunicorn python-dotenv
```

### Database Errors

If you see database errors:

1. Check your database configuration in settings.py
2. Ensure your database server is running
3. Verify your database credentials

### Media File Issues

If images don't appear:

1. Make sure you've copied all media files to the correct location
2. Check that `MEDIA_URL` and `MEDIA_ROOT` are correctly set in settings.py
3. Ensure the media directories have the correct permissions

### Local vs Replit URLs

You might need to update some URLs that were hardcoded for Replit. Check for:

1. URLs in JavaScript files
2. Absolute URLs in templates

## Optional: Version Control

Consider initializing a Git repository for your local project:

```bash
# Initialize a Git repository
git init

# Add your files
git add .

# Create your first commit
git commit -m "Initial commit"
```

This makes it easier to track changes and collaborate with others.