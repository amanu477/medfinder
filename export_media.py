#!/usr/bin/env python
"""
Script to export media files for local development.
Creates a zip file containing all media files.
"""

import os
import shutil
import datetime

def main():
    print("Exporting media files for local development...")
    
    # Get current date for the filename
    today = datetime.datetime.now().strftime("%Y%m%d")
    
    # Create export directory if it doesn't exist
    os.makedirs('data_export', exist_ok=True)
    
    # Path to the media directory
    media_dir = 'media'
    
    # Check if media directory exists
    if not os.path.exists(media_dir):
        print(f"Error: Media directory '{media_dir}' not found.")
        return
    
    # Name of the zip file
    zip_filename = f'data_export/media_files_{today}'
    
    # Create zip file containing media directory
    print(f"Creating zip file: {zip_filename}.zip")
    shutil.make_archive(zip_filename, 'zip', media_dir)
    
    print("\nMedia export complete.")
    print(f"Zip file is located at: {zip_filename}.zip")
    print("\nTo use these files on your local machine:")
    print("1. Extract the zip file")
    print("2. Copy the extracted files to your local 'media' directory")

if __name__ == "__main__":
    main()