#!/usr/bin/env python
"""
This script fixes the ALLOWED_HOSTS setting in settings.py to include
the Replit-specific domain. Run this when you encounter DisallowedHost errors.
"""

import os
import sys
import re

def main():
    settings_file = 'pharmacy_finder/settings.py'
    
    if not os.path.exists(settings_file):
        print(f"Error: Could not find {settings_file}")
        sys.exit(1)
    
    # Read current settings file
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Get the error message from the command line
    if len(sys.argv) > 1:
        error_msg = sys.argv[1]
        match = re.search(r"Invalid HTTP_HOST header: '([^']+)'", error_msg)
        if match:
            host = match.group(1)
            print(f"Found host in error message: {host}")
        else:
            print("No host found in error message. Please provide the full error message.")
            sys.exit(1)
    else:
        # Use a very permissive ALLOWED_HOSTS setting 
        # and add common Replit domains
        print("No error message provided. Using default settings.")
        pattern = r"ALLOWED_HOSTS\s*=\s*\[([^\]]*)\]"
        replacement = "ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', '.replit.app', '.repl.co', '.janeway.replit.dev']"
        
        new_content = re.sub(pattern, replacement, content)
        
        with open(settings_file, 'w') as f:
            f.write(new_content)
        
        print(f"Updated {settings_file} with permissive ALLOWED_HOSTS setting")
        return
    
    # Check if the host is already in ALLOWED_HOSTS
    pattern = r"ALLOWED_HOSTS\s*=\s*\[([^\]]*)\]"
    match = re.search(pattern, content)
    if not match:
        print(f"Could not find ALLOWED_HOSTS in {settings_file}")
        sys.exit(1)
    
    hosts = match.group(1)
    if f"'{host}'" in hosts:
        print(f"Host {host} is already in ALLOWED_HOSTS")
        return
    
    # Add the host to ALLOWED_HOSTS
    if hosts.strip():
        # There are already some hosts, add to the list
        new_hosts = hosts + f", '{host}'"
    else:
        # Empty list, add as the first item
        new_hosts = f"'{host}'"
    
    new_content = re.sub(pattern, f"ALLOWED_HOSTS = [{new_hosts}]", content)
    
    with open(settings_file, 'w') as f:
        f.write(new_content)
    
    print(f"Updated {settings_file} with new host: {host}")

if __name__ == "__main__":
    main()