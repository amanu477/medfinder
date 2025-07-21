# Ethiopian Pharmacy Platform - Line-by-Line Code Analysis

## 🔍 Complete Code Explanation

This document explains EVERY SINGLE LINE of code in your Ethiopian Pharmacy Platform. Each line is broken down to show exactly what it does and why it exists.

---

## 📁 File Structure Analysis

```
ethiopian-pharmacy/                 # Root project directory
├── customer/                      # App handling patient functionality
│   ├── models.py                  # Database tables for customers
│   ├── views.py                   # Business logic for customer operations
│   ├── forms.py                   # Web forms for customer input
│   ├── urls.py                    # URL routing for customer pages
│   └── templates/                 # HTML templates for customer pages
├── pharmacy/                      # App handling pharmacy operations
├── delivery/                      # App handling delivery operations
├── moh/                          # Ministry of Health verification app
├── platform_admin/              # System administration app
└── manage.py                     # Django command-line utility
```

---

## 👥 CUSTOMER SECTION - Complete Line Analysis (`customer/models.py`)

### Line-by-Line Breakdown of customer/models.py:

```python
# Line 1: Import Django's database models module
from django.db import models
```
**What it does**: Brings in Django's Object-Relational Mapping (ORM) system that lets us create database tables using Python classes instead of raw SQL.

```python
# Line 2: Import Django's built-in User model for authentication
from django.contrib.auth.models import User
```
**What it does**: Gets Django's pre-built User model that handles usernames, passwords, and basic authentication. We'll link our custom models to this.

```python
# Line 3: Import Django's timezone utilities
from django.utils import timezone
```
**What it does**: Provides timezone-aware datetime functions. Essential for handling different time zones properly in a global application.

```python
# Line 4: Import Python's timedelta for date/time calculations
from datetime import timedelta
```
**What it does**: Allows us to add or subtract time periods (like "15 minutes from now" for expiration checks).

```python
# Line 6: Start defining the Customer class that inherits from Model
class Customer(models.Model):
```
**What it does**: Creates a new database table called "customer_customer" with Django's ORM. The `models.Model` gives us all database functionality.

```python
# Line 7: Documentation string describing this model
"""Customer model for storing customer information"""
```
**What it does**: Python docstring that explains what this model is for. Shows up in documentation and IDE help.

```python
# Line 8: Create relationship to Django's User model
user = models.OneToOneField(User, on_delete=models.CASCADE)
```
**What it does**: 
- `OneToOneField`: Each customer connects to exactly one User account
- `on_delete=models.CASCADE`: If User is deleted, delete this Customer too
- This links our custom customer info to Django's built-in login system

```python
# Line 9: Customer's full name field
name = models.CharField(max_length=100)
```
**What it does**: 
- `CharField`: Text field for short strings
- `max_length=100`: Database will store maximum 100 characters
- This stores the customer's full name like "Abebe Kebede"

```python
# Line 10: Customer's email address field
email = models.EmailField()
```
**What it does**: 
- `EmailField`: Special text field that validates email format
- Django automatically checks if email looks like "user@domain.com"
- Stored as text but validated for proper email format

```python
# Line 11: Customer's phone number field
phone = models.CharField(max_length=20)
```
**What it does**: 
- Stores phone numbers as text (not numbers) because phone numbers can have "+", "-", spaces
- `max_length=20`: Handles Ethiopian numbers like "+251911234567"

```python
# Line 12: Customer's address field
address = models.TextField()
```
**What it does**: 
- `TextField`: For longer text without character limits
- Stores full addresses like "Bole, Addis Ababa, Ethiopia"
- Unlike CharField, can store paragraphs of text

```python
# Line 13: GPS latitude coordinate
latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
```
**What it does**: 
- `DecimalField`: Stores precise decimal numbers (not floating point)
- `max_digits=10`: Total of 10 digits (like 12.34567890)
- `decimal_places=8`: 8 digits after decimal point for GPS precision
- `null=True`: Database can store NULL (empty) values
- `blank=True`: Forms can submit empty values
- Stores precise GPS location like 9.03141269

```python
# Line 14: GPS longitude coordinate
longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
```
**What it does**: 
- Same as latitude but with 11 total digits (longitude can be -180 to +180)
- Stores precise GPS location like 38.76151109
- Both coordinates together pinpoint exact location on Earth

```python
# Line 15: When customer record was created
created_at = models.DateTimeField(auto_now_add=True)
```
**What it does**: 
- `DateTimeField`: Stores both date and time
- `auto_now_add=True`: Django automatically sets this to current time when record is first created
- Never changes after creation - permanent timestamp of when customer joined

```python
# Line 16: When customer record was last updated
updated_at = models.DateTimeField(auto_now=True)
```
**What it does**: 
- `auto_now=True`: Django automatically updates this to current time every time record is saved
- Changes every time customer updates their profile
- Tracks last modification time

```python
# Line 17: Email verification status with comment
is_verified = models.BooleanField(default=False)  # Email verification status
```
**What it does**: 
- `BooleanField`: Stores True or False only
- `default=False`: New customers start as unverified
- Security feature - customer must verify email before full access
- Comment explains what this field tracks

```python
# Line 19-20: String representation method
def __str__(self):
    return f"{self.name} - {self.email}"
```
**What it does**: 
- `__str__`: Special Python method that returns human-readable text representation
- `f"{self.name} - {self.email}"`: F-string formatting to combine name and email
- When you print a Customer object, it shows "John Doe - john@example.com"
- Used in Django admin interface and debugging

### EmailVerification Model - Line by Line:

```python
# Line 22: Start EmailVerification class
class EmailVerification(models.Model):
```
**What it does**: Creates database table for storing email verification codes sent to users.

```python
# Line 23: Documentation for verification model
"""Model for storing email verification codes"""
```
**What it does**: Explains this model handles email verification system.

```python
# Line 24: Email address to be verified
email = models.EmailField()
```
**What it does**: Stores email that needs verification, validates email format.

```python
# Line 25: 6-digit verification code
verification_code = models.CharField(max_length=6)
```
**What it does**: Stores random 6-digit code like "123456" sent to user's email.

```python
# Line 26-29: User type choices
user_type = models.CharField(max_length=20, choices=[
    ('customer', 'Customer'),
    ('pharmacy', 'Pharmacy')
])
```
**What it does**: 
- Tracks whether verification is for customer or pharmacy registration
- `choices=[...]`: Database stores 'customer' or 'pharmacy', forms show 'Customer' or 'Pharmacy'

```python
# Line 30: When verification code was created
created_at = models.DateTimeField(auto_now_add=True)
```
**What it does**: Records when verification code was generated - used for expiration.

```python
# Line 31: Whether code has been used
used = models.BooleanField(default=False)
```
**What it does**: Tracks if verification code was already used - prevents reuse.

```python
# Line 33-34: Metadata class
class Meta:
    ordering = ['-created_at']
```
**What it does**: 
- `ordering = ['-created_at']`: Shows newest verification codes first
- Minus sign means descending order (newest to oldest)

```python
# Line 36-37: String representation
def __str__(self):
    return f"Verification for {self.email} - {self.verification_code}"
```
**What it does**: Shows "Verification for john@email.com - 123456" when printing object.

```python
# Line 39-41: Expiration check method
def is_expired(self):
    """Check if verification code has expired (15 minutes)"""
    return timezone.now() > self.created_at + timedelta(minutes=15)
```
**What it does**: 
- Custom method to check if code is older than 15 minutes
- `timezone.now()`: Current time
- `self.created_at + timedelta(minutes=15)`: Code creation time plus 15 minutes
- Returns True if current time is past expiration time

```python
# Line 43-45: Validity check method
def is_valid(self):
    """Check if verification code is valid"""
    return not self.used and not self.is_expired()
```
**What it does**: 
- Checks if code can still be used
- `not self.used`: Code hasn't been used yet
- `not self.is_expired()`: Code hasn't expired
- Returns True only if both conditions are met

### Prescription Model - Line by Line:

```python
# Line 48: Start Prescription class
class Prescription(models.Model):
```
**What it does**: Creates table for storing prescription uploads from customers.

```python
# Line 49: Documentation
"""Model for storing prescription information"""
```
**What it does**: Explains this model handles prescription image uploads.

```python
# Line 50-55: Status choices tuple
STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('completed', 'Completed'),
)
```
**What it does**: 
- Defines all possible prescription statuses
- Tuple format: (database_value, human_readable_display)
- Database stores 'pending', users see 'Pending'

```python
# Line 57: Customer name field
customer_name = models.CharField(max_length=100)
```
**What it does**: Stores full name of person submitting prescription.

```python
# Line 58: Customer email field
customer_email = models.EmailField()
```
**What it does**: Email of person submitting prescription - for notifications.

```python
# Line 59: Customer phone field
customer_phone = models.CharField(max_length=20)
```
**What it does**: Phone number for prescription-related communication.

```python
# Line 60: Prescription image upload
prescription_image = models.ImageField(upload_to='prescriptions/')
```
**What it does**: 
- `ImageField`: Special field for image uploads
- `upload_to='prescriptions/'`: Saves images to media/prescriptions/ folder
- Handles image validation and storage automatically

```python
# Line 61: Link to pharmacy
pharmacy = models.ForeignKey('pharmacy.Pharmacy', on_delete=models.CASCADE, null=True, blank=True)
```
**What it does**: 
- `ForeignKey`: Links prescription to pharmacy that will process it
- `'pharmacy.Pharmacy'`: String reference to avoid import problems
- `on_delete=models.CASCADE`: Delete prescription if pharmacy is deleted
- `null=True, blank=True`: Prescription can exist without assigned pharmacy initially

```python
# Line 62: Status field with choices
status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
```
**What it does**: 
- Uses STATUS_CHOICES from above
- `default='pending'`: New prescriptions start as pending
- Creates dropdown in forms with defined choices

```python
# Line 63-64: Timestamp fields
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```
**What it does**: Same as Customer model - tracks creation and modification times.

```python
# Line 66-67: Metadata
class Meta:
    ordering = ['-created_at']
```
**What it does**: Show newest prescriptions first in lists.

```python
# Line 69-70: String representation
def __str__(self):
    return f"Prescription by {self.customer_name}"
```
**What it does**: Shows "Prescription by John Doe" when printing object.

---

## 👥 CUSTOMER VIEWS - Complete Line Analysis (`customer/views.py`)

### Import Section - Line by Line:

```python
# Line 1: Import Django shortcuts for common operations
from django.shortcuts import render, redirect, get_object_or_404
```
**What it does**:
- `render`: Combines template with data to create HTML response
- `redirect`: Sends user to different URL/page
- `get_object_or_404`: Gets database object or shows 404 error if not found

```python
# Line 2: Import HTTP response classes
from django.http import JsonResponse, HttpResponse
```
**What it does**:
- `JsonResponse`: Returns JSON data (for AJAX/API responses)
- `HttpResponse`: Returns basic HTTP response with custom content

```python
# Line 3: Import database query tools
from django.db.models import Q
```
**What it does**:
- `Q`: Builds complex database queries with AND, OR conditions
- Example: `Q(name__contains='medicine') | Q(description__contains='medicine')`

```python
# Line 4: Import timezone utilities
from django.utils import timezone
```
**What it does**: Get current time with proper timezone handling for timestamps.

```python
# Line 5: Import messaging system
from django.contrib import messages
```
**What it does**: Show success/error/info messages to users after form submissions.

```python
# Line 6: Import authentication functions
from django.contrib.auth import login, authenticate, logout
```
**What it does**:
- `login`: Log user into Django session
- `authenticate`: Check username/password validity
- `logout`: Remove user from session

```python
# Line 7: Import login requirement decorator
from django.contrib.auth.decorators import login_required
```
**What it does**: `@login_required` decorator forces users to login before accessing views.

```python
# Line 8: Import User model
from django.contrib.auth.models import User
```
**What it does**: Django's built-in User model for authentication system.

```python
# Line 9: Import database transaction handling
from django.db import transaction
```
**What it does**: Wrap multiple database operations to ensure all succeed or all fail together.

```python
# Line 10-11: Import security decorators
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
```
**What it does**:
- `csrf_exempt`: Disable CSRF protection for specific views (dangerous, use carefully)
- `require_http_methods`: Restrict view to specific HTTP methods (GET, POST, etc.)

```python
# Line 12: Import JSON handling
import json
```
**What it does**: Parse and generate JSON data for API responses.

```python
# Line 13: Import all customer models
from .models import Customer, Prescription, Order, OrderItem, Cart, CartItem, IncidentReport, AdminNotification, Payment
```
**What it does**: Import all database models from customer app - the dot means "from this same app".

```python
# Line 14-16: Import custom services
from .chapa_service import ChapaService
from .ocr_service import PrescriptionOCRService
from .qr_utils import generate_qr_code_image, generate_payment_qr_data
```
**What it does**:
- `ChapaService`: Ethiopian payment processing
- `PrescriptionOCRService`: AI text extraction from prescription images
- QR utilities: Generate QR codes for deliveries and payments

```python
# Line 17-18: Import models from other apps
from pharmacy.models import Pharmacy, Medicine
from moh.models import MoHOfficer
```
**What it does**: Import models from pharmacy and Ministry of Health apps.

```python
# Line 19: Import forms
from .forms import PrescriptionForm, CustomerRegistrationForm, OrderForm, QuickIncidentForm
```
**What it does**: Import HTML forms for user input validation.

```python
# Line 20-23: Import system utilities
import tempfile
import os
import base64
import logging
```
**What it does**:
- `tempfile`: Create temporary files for image processing
- `os`: Operating system operations like file paths
- `base64`: Encode binary data (images) for web transmission
- `logging`: Record errors and debug information

```python
# Line 25-26: Configure logging
logger = logging.getLogger(__name__)
```
**What it does**: Create logger instance for this specific file to record errors and debug info.

### Home View - Line by Line:

```python
# Line 28-29: Define home page function
def home(request):
    """Home page view with search functionality"""
```
**What it does**: Function that handles requests to the home page, includes docstring explaining purpose.

```python
# Line 30-31: Check if user is logged in
if request.user.is_authenticated:
```
**What it does**: 
- `request.user`: Current user making the request
- `is_authenticated`: True if user is logged in, False if anonymous
- Only execute following code block if user is logged in

```python
# Line 32-35: Try to find delivery person
try:
    from delivery.models import DeliveryPerson
    delivery_person = DeliveryPerson.objects.get(user=request.user, is_active=True)
    return redirect('delivery_dashboard')
```
**What it does**:
- `try:`: Start error handling block
- Import DeliveryPerson model only when needed (avoids circular imports)
- `DeliveryPerson.objects.get()`: Find delivery person record for current user
- `is_active=True`: Only active delivery personnel
- `redirect('delivery_dashboard')`: Send delivery people directly to work dashboard

```python
# Line 36-37: Handle case where user is not delivery person
except DeliveryPerson.DoesNotExist:
    pass
```
**What it does**:
- `except DeliveryPerson.DoesNotExist:`: Catch error when user is not a delivery person
- `pass`: Do nothing - continue to regular home page

```python
# Line 39-42: Prepare template context
context = {
    'suppress_moh_notifications': True,
}
```
**What it does**:
- `context`: Dictionary of data passed to HTML template
- `'suppress_moh_notifications': True`: Tell template not to show government notifications on home page

```python
# Line 43: Render home page template
return render(request, 'home.html', context)
```
**What it does**:
- `render()`: Combine 'home.html' template with context data
- Returns HTML response to user's browser

### Medicine Search View - Line by Line:

```python
# Line 49-53: Get search parameters
def search_medicines(request):
    """Search medicines and return results sorted by proximity"""
    query = request.GET.get('query', '')
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lon')
```
**What it does**:
- `request.GET.get('query', '')`: Get search term from URL, default to empty string
- `user_lat`, `user_lon`: Get GPS coordinates from URL parameters
- These come from the search form and location detection JavaScript

```python
# Line 55-56: Handle empty search
if not query:
    return render(request, 'search_results.html', {'query': query, 'medicines': []})
```
**What it does**:
- `if not query:`: Check if search term is empty
- Return empty results page if no search term provided

```python
# Line 58-65: Build database query
medicines = Medicine.objects.filter(
    Q(name__icontains=query) | Q(description__icontains=query),
    is_available=True,
    pharmacy__is_active=True,
    stock_quantity__gt=0,
    expiry_date__gt=timezone.now().date()
).select_related('pharmacy')
```
**What it does**:
- `Medicine.objects.filter()`: Query medicine database table
- `Q(name__icontains=query) | Q(description__icontains=query)`: Search in name OR description
- `__icontains`: Case-insensitive partial match (finds "Para" in "Paracetamol")
- `|`: OR operator for combining conditions
- `is_available=True`: Only medicines marked as available
- `pharmacy__is_active=True`: Only from active pharmacies (double underscore accesses related model)
- `stock_quantity__gt=0`: Only medicines with stock greater than 0
- `expiry_date__gt=timezone.now().date()`: Only non-expired medicines
- `select_related('pharmacy')`: Join pharmacy data to avoid extra database queries

```python
# Line 67-68: Check if user provided location
if user_lat and user_lon:
```
**What it does**: Only calculate distances if user shared their GPS location.

```python
# Line 69-75: Import distance calculator and set up logging
try:
    from .utils import haversine_distance
    import logging
    logger = logging.getLogger(__name__)
    
    user_lat = float(user_lat)
    user_lon = float(user_lon)
```
**What it does**:
- Import haversine distance formula (calculates distance between GPS points)
- Convert GPS coordinates from text to numbers with `float()`
- Set up error logging

```python
# Line 77-91: Calculate distances to each pharmacy
medicines_with_distance = []
for medicine in medicines:
    pharmacy = medicine.pharmacy
    if pharmacy.latitude and pharmacy.longitude:
        distance = haversine_distance(
            user_lat, user_lon,
            float(pharmacy.latitude), float(pharmacy.longitude)
        )
        medicine.distance = round(distance, 1)
        medicines_with_distance.append((medicine, distance))
        logger.info(f"Medicine: {medicine.name}, Pharmacy: {pharmacy.name}, Distance: {distance:.2f} km")
    else:
        medicine.distance = None
        medicines_with_distance.append((medicine, float('inf')))
```
**What it does**:
- `medicines_with_distance = []`: Empty list to store results
- `for medicine in medicines:`: Loop through each medicine found
- `pharmacy = medicine.pharmacy`: Get pharmacy for this medicine
- `if pharmacy.latitude and pharmacy.longitude:`: Only calculate if pharmacy has GPS coordinates
- `haversine_distance()`: Calculate real-world distance using GPS coordinates
- `round(distance, 1)`: Round to 1 decimal place (like 2.3 km)
- `medicine.distance = ...`: Add distance property to medicine object
- `medicines_with_distance.append((medicine, distance))`: Store medicine and its distance as tuple
- `logger.info()`: Record calculation in log file for debugging
- `float('inf')`: Assign infinite distance to pharmacies without GPS coordinates

```python
# Line 93-95: Sort by distance
medicines_with_distance.sort(key=lambda x: x[1])
medicines = [medicine for medicine, distance in medicines_with_distance]
```
**What it does**:
- `sort(key=lambda x: x[1])`: Sort tuples by second element (distance)
- `lambda x: x[1]`: Anonymous function that returns distance from tuple
- List comprehension extracts just the medicine objects in distance order

```python
# Line 97-100: Handle errors in distance calculation
except (ValueError, TypeError) as e:
    logger.error(f"Error calculating distances: {e}")
    # Continue without distance sorting
    pass
```
**What it does**:
- `except (ValueError, TypeError)`: Catch errors from invalid GPS coordinates
- `logger.error()`: Record error in log file
- `pass`: Continue without distance sorting if GPS calculation fails

```python
class Order(models.Model):
    # The shopping experience digitized
    customer = ForeignKey(Customer)  # Who's buying
    pharmacy = ForeignKey('pharmacy.Pharmacy')  # From which pharmacy
    status = CharField()  # pending, confirmed, preparing, ready, completed
    total_amount = DecimalField()  # Total cost in Ethiopian Birr
    payment_method = CharField()  # online, cash_on_delivery
    delivery_address = TextField()  # Where to deliver
    qr_code = CharField()  # Unique delivery confirmation code
```

**What it does**: Manages the entire purchase journey from cart to delivery.

### 🎯 Views (`customer/views.py`) - Business Logic

#### Home Page Logic
```python
def home(request):
    """Home page view with search functionality"""
    # Redirect delivery personnel directly to their dashboard
    if request.user.is_authenticated:
        try:
            from delivery.models import DeliveryPerson
            delivery_person = DeliveryPerson.objects.get(user=request.user, is_active=True)
            return redirect('delivery_dashboard')
        except DeliveryPerson.DoesNotExist:
            pass
    
    # Ensure no MoH notifications appear on main homepage
    context = {
        'suppress_moh_notifications': True,
    }
    return render(request, 'home.html', context)
```

**Code Explanation:**
- `request.user.is_authenticated`: Checks if user is logged in
- `try/except DeliveryPerson.DoesNotExist`: Safe way to check if user is delivery person
- `redirect('delivery_dashboard')`: Sends delivery staff directly to work area
- `context = {...}`: Passes data to template to control what displays
- Import inside function: Avoids circular import issues between apps

#### Medicine Search System
```python
def search_medicines(request):
    """Search medicines and return results sorted by proximity"""
    query = request.GET.get('query', '')
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lon')
    
    if not query:
        return render(request, 'search_results.html', {'query': query, 'medicines': []})
    
    # Search for medicines that match the query and are available
    medicines = Medicine.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_available=True,
        pharmacy__is_active=True,
        stock_quantity__gt=0,
        expiry_date__gt=timezone.now().date()
    ).select_related('pharmacy')
    
    # If user location is provided, sort by proximity
    if user_lat and user_lon:
        try:
            from .utils import haversine_distance
            
            user_lat = float(user_lat)
            user_lon = float(user_lon)
            
            medicines_with_distance = []
            for medicine in medicines:
                pharmacy = medicine.pharmacy
                if pharmacy.latitude and pharmacy.longitude:
                    distance = haversine_distance(
                        user_lat, user_lon,
                        float(pharmacy.latitude), float(pharmacy.longitude)
                    )
                    medicine.distance = round(distance, 1)
                    medicines_with_distance.append((medicine, distance))
                else:
                    medicine.distance = None
                    medicines_with_distance.append((medicine, float('inf')))
            
            # Sort by distance (closest first)
            medicines_with_distance.sort(key=lambda x: x[1])
            medicines = [medicine for medicine, distance in medicines_with_distance]
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating distances: {e}")
            pass
```

**Code Explanation:**
- `Q(name__icontains=query) | Q(description__icontains=query)`: Searches both name and description fields
- `__icontains`: Case-insensitive search that matches partial strings
- `stock_quantity__gt=0`: Only medicines with stock greater than 0
- `select_related('pharmacy')`: Joins pharmacy data to avoid additional database queries
- `haversine_distance()`: Calculates real-world distance between GPS coordinates
- `float('inf')`: Assigns infinite distance to pharmacies without GPS coordinates
- `lambda x: x[1]`: Sorts tuples by second element (distance)

#### OCR Prescription Magic
```python
def upload_prescription(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.customer = request.user.customer
            
            # AI-powered text extraction
            ocr_service = PrescriptionOCRService()
            ocr_result = ocr_service.extract_text(prescription.image.path)
            
            prescription.ocr_text = ocr_result['text']
            prescription.ocr_confidence = ocr_result['confidence']
            prescription.save()
```

**What it does**: Uses AI to read prescriptions and extract medicine names automatically.

### 🧠 Services (`customer/ocr_service.py`)
The AI brain that reads prescriptions:

```python
class PrescriptionOCRService:
    def extract_text(self, image_path):
        # Load image and enhance for better reading
        image = Image.open(image_path)
        enhanced_image = self.preprocess_image(image)
        
        # Use Tesseract AI to extract text
        text = pytesseract.image_to_string(enhanced_image)
        confidence = pytesseract.image_to_data(enhanced_image)
        
        # Find medicine names using fuzzy matching
        medicine_matches = self.find_medicine_matches(text)
        
        return {
            'text': text,
            'confidence': self.calculate_confidence(confidence),
            'medicines': medicine_matches
        }
```

**What it does**: Acts like a digital pharmacist that can read handwritten prescriptions.

---

## 🏪 PHARMACY SECTION (`pharmacy/`)

*"The digital pharmacy management system - where medicine inventory meets technology"*

### 🗄️ Models (`pharmacy/models.py`) - Pharmacy Data Structure

#### MoH Pharmacy Record (Government Registry)
```python
class MoHPharmacyRecord(models.Model):
    """Ministry of Health pharmacy registry - pre-registered legitimate pharmacies"""
    REGION_CHOICES = [
        ('addis_ababa', 'Addis Ababa'),
        ('oromia', 'Oromia'),
        ('amhara', 'Amhara'),
        ('tigray', 'Tigray'),
        # ... more Ethiopian regions
    ]
    
    LICENSE_TYPE_CHOICES = [
        ('retail', 'Retail Pharmacy'),
        ('hospital', 'Hospital Pharmacy'),
        ('wholesale', 'Wholesale Pharmacy'),
        ('manufacturing', 'Manufacturing Pharmacy'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    # Basic Information
    pharmacy_name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=50, unique=True)
    owner_name = models.CharField(max_length=100)
    pharmacist_name = models.CharField(max_length=100)
    pharmacist_license = models.CharField(max_length=50)
    
    # Location Information
    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    city = models.CharField(max_length=100)
    woreda = models.CharField(max_length=100)
    kebele = models.CharField(max_length=100)
    address_detail = models.TextField()
    
    # Document Uploads
    business_license_document = models.FileField(upload_to='moh_documents/business_licenses/', blank=True, null=True)
    pharmacist_certificate_document = models.FileField(upload_to='moh_documents/pharmacist_certificates/', blank=True, null=True)
    
    class Meta:
        ordering = ['-registration_date']
        verbose_name = "Ministry of Health Pharmacy Record"
```

**Code Explanation:**
- `choices=REGION_CHOICES`: Creates dropdown with predefined Ethiopian regions
- `unique=True`: Ensures no duplicate license numbers in database
- `FileField(upload_to='moh_documents/')`: Stores uploaded documents in organized folders
- `blank=True, null=True`: Makes fields optional (can be empty)
- `verbose_name`: Human-readable name for Django admin interface
- `ordering = ['-registration_date']`: Default sort by newest registrations first

```python
class Medicine(models.Model):
    # The digital medicine cabinet
    pharmacy = ForeignKey(Pharmacy)  # Which pharmacy owns this
    name = CharField(max_length=200)  # "Paracetamol 500mg"
    generic_name = CharField()  # Scientific name
    manufacturer = CharField()  # Who made it
    description = TextField()  # What it treats
    price = DecimalField()  # Cost in Ethiopian Birr
    stock_quantity = IntegerField()  # How many in stock
    expiry_date = DateField()  # When it expires
    requires_prescription = BooleanField()  # Need doctor's note?
    is_available = BooleanField()  # Currently selling?
```

**What it does**: Digital inventory system that tracks every medicine with prices and availability.

### 🎯 Views (`pharmacy/views.py`)

#### Pharmacy Dashboard Command Center
```python
def pharmacy_dashboard(request):
    pharmacy = request.user.pharmacy
    
    # Dashboard statistics
    stats = {
        'total_medicines': Medicine.objects.filter(pharmacy=pharmacy).count(),
        'pending_orders': Order.objects.filter(pharmacy=pharmacy, status='pending').count(),
        'low_stock': Medicine.objects.filter(pharmacy=pharmacy, stock_quantity__lt=10).count(),
        'expiring_soon': Medicine.objects.filter(
            pharmacy=pharmacy, 
            expiry_date__lte=timezone.now().date() + timedelta(days=30)
        ).count()
    }
    
    return render(request, 'pharmacy/dashboard.html', {'stats': stats})
```

**What it does**: Creates a mission control center showing all important pharmacy metrics.

#### Prescription Review System
```python
def prescription_review_detail(request, review_id):
    review = get_object_or_404(PrescriptionReview, id=review_id)
    
    # SAFETY FIRST: Only approve if OCR confidence is 100%
    if review.prescription.ocr_confidence < 100:
        messages.error(request, 'Cannot approve - OCR confidence below 100%')
        return redirect('prescription_review_list')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            review.status = 'approved'
            review.approved_by = request.user
            review.save()
            messages.success(request, 'Prescription approved successfully!')
        elif action == 'reject':
            review.status = 'rejected'
            review.rejection_reason = request.POST.get('rejection_reason')
            review.save()
```

**What it does**: Ensures safety by requiring perfect OCR reading before prescription approval.

---

## 🚚 DELIVERY SECTION (`delivery/`)

*"The delivery management system - where logistics meets real-time tracking"*

### 🗄️ Models (`delivery/models.py`) - Delivery System Structure

#### DeliveryPerson Model
```python
class DeliveryPerson(models.Model):
    """Delivery personnel model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='delivery_staff')
    employee_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    national_id = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=50, choices=[
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('car', 'Car'),
        ('on_foot', 'On Foot'),
    ], default='motorcycle')
    vehicle_plate = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    current_location_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    current_location_lon = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    total_deliveries = models.IntegerField(default=0)

    def update_location(self, lat, lon):
        """Update delivery person's current location"""
        self.current_location_lat = lat
        self.current_location_lon = lon
        self.last_location_update = timezone.now()
        self.save()
    
    def has_active_deliveries(self):
        """Check if delivery person has any active deliveries"""
        active_statuses = ['assigned', 'picked_up', 'in_transit', 'arrived']
        return self.delivery_set.filter(status__in=active_statuses).exists()
    
    def get_active_deliveries_count(self):
        """Get count of active deliveries"""
        active_statuses = ['assigned', 'picked_up', 'in_transit', 'arrived']
        return self.delivery_set.filter(status__in=active_statuses).count()
```

**Code Explanation:**
- `related_name='delivery_staff'`: Allows pharmacy.delivery_staff.all() to get all delivery people
- `max_digits=10, decimal_places=8`: High precision GPS coordinates (8 decimal places ≈ 1mm accuracy)
- `default=5.00`: New delivery people start with perfect rating
- Custom methods like `update_location()`: Encapsulate common operations
- `self.delivery_set`: Django reverse relationship to access related deliveries
- `filter(status__in=active_statuses)`: Filters by multiple status values at once

```python
class Delivery(models.Model):
    # The delivery mission details
    order = OneToOneField('customer.Order')  # Which order to deliver
    delivery_person = ForeignKey(DeliveryPerson)  # Who's delivering
    pickup_time = DateTimeField()  # When picked up from pharmacy
    delivery_time = DateTimeField()  # When delivered to customer
    status = CharField()  # assigned, picked_up, in_transit, delivered
    delivery_notes = TextField()  # Special instructions
    customer_rating = IntegerField()  # How did we do? (1-5 stars)
```

**What it does**: Tracks every delivery mission from start to customer satisfaction.

### 🎯 Views (`delivery/views.py`)

#### Delivery Dashboard
```python
def delivery_dashboard(request):
    delivery_person = request.user.deliveryperson
    
    # Get current active deliveries
    active_deliveries = Delivery.objects.filter(
        delivery_person=delivery_person,
        status__in=['assigned', 'picked_up', 'in_transit']
    )
    
    # Calculate performance stats
    stats = {
        'total_deliveries': Delivery.objects.filter(delivery_person=delivery_person).count(),
        'current_active': active_deliveries.count(),
        'rating': delivery_person.get_average_rating(),
        'completed_today': Delivery.objects.filter(
            delivery_person=delivery_person,
            status='delivered',
            delivery_time__date=timezone.now().date()
        ).count()
    }
```

**What it does**: Creates a delivery command center showing all missions and performance.

#### QR Code Scanner System
```python
def qr_scanner(request):
    """QR code scanner for delivery confirmation"""
    delivery_person = request.user.deliveryperson
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'scan_qr':
            qr_data = request.POST.get('qr_data', '').strip()
            
            if qr_data:
                try:
                    # Try to find order by QR code (priority method)
                    order = Order.objects.select_related('customer').get(qr_code=qr_data)
                    
                    if order.status in ['ready_for_pickup', 'picked_up', 'in_transit']:
                        # Process delivery confirmation
                        delivery = order.delivery
                        if delivery.delivery_person == delivery_person:
                            
                            # For cash orders, redirect to payment confirmation
                            if order.payment_method == 'cash_on_delivery' and order.status != 'completed':
                                return redirect('confirm_cash_payment', order_id=order.id)
                            
                            # Complete the delivery
                            order.status = 'completed'
                            delivery.status = 'delivered'
                            delivery.delivery_time = timezone.now()
                            
                            order.save()
                            delivery.save()
                            
                            messages.success(request, f'✅ Delivery completed successfully! Order #{order.id}')
                            return redirect('delivery_dashboard')
                        else:
                            messages.error(request, '❌ This delivery is assigned to another delivery person.')
                    else:
                        messages.error(request, f'❌ Invalid order status: {order.get_status_display()}')
                        
                except Order.DoesNotExist:
                    messages.error(request, '❌ Invalid QR code. Order not found.')
                except Exception as e:
                    messages.error(request, f'❌ Error processing QR code: {str(e)}')
            else:
                messages.error(request, '❌ No QR code data provided.')
        
        elif action == 'manual_entry':
            # Fallback manual code entry
            delivery_code = request.POST.get('delivery_code', '').strip()
            # ... similar logic for manual entry
```

**Code Explanation:**
- `select_related('customer')`: Joins customer data to avoid extra database queries
- `qr_data.strip()`: Removes whitespace from scanned QR codes
- `order.get_status_display()`: Gets human-readable status text instead of database code
- `timezone.now()`: Uses Django's timezone-aware datetime
- Multiple try/except blocks: Handle different error scenarios gracefully
- `redirect('delivery_dashboard')`: Sends user back to main dashboard after completion

#### Cash Collection Workflow
```python
def confirm_cash_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        amount_received = request.POST.get('amount_received')
        
        if Decimal(amount_received) == order.total_amount:
            # Create payment record
            Payment.objects.create(
                order=order,
                amount=order.total_amount,
                payment_method='cash',
                status='completed',
                delivery_person=request.user.deliveryperson
            )
            
            order.status = 'completed'
            order.save()
            
            messages.success(request, f'Cash payment confirmed: {amount_received} ETB')
```

**What it does**: Handles cash-on-delivery payments with proper verification and record-keeping.

---

## 🏛️ MINISTRY OF HEALTH SECTION (`moh/`)

*"The government guardians - where regulation meets healthcare!"*

### 🏠 Models (`moh/models.py`)

```python
class MoHOfficer(models.Model):
    # Government official profile
    user = OneToOneField(User)  # Their secure government login
    employee_id = CharField(unique=True)  # Official ID number
    department = CharField()  # Which MoH department
    clearance_level = CharField()  # security clearance
    is_active = BooleanField(default=True)  # Currently employed?
```

```python
class PharmacyLicense(models.Model):
    # Official pharmacy records (separate from platform)
    license_number = CharField(unique=True)  # Official license
    pharmacy_name = CharField()  # Registered name
    owner_name = CharField()  # License holder
    address = TextField()  # Registered address
    issue_date = DateField()  # When issued
    expiry_date = DateField()  # When expires
    status = CharField()  # active, suspended, expired, revoked
    license_type = CharField()  # retail, wholesale, hospital
```

**What it does**: Maintains the official government database separate from the platform.

### 🎯 Views (`moh/views.py`)

#### License Verification System
```python
def verify_pharmacy_license(request, pharmacy_id):
    platform_pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
    
    # Cross-reference with official MoH records
    try:
        official_license = PharmacyLicense.objects.get(
            license_number=platform_pharmacy.license_number,
            status='active'
        )
        
        # Verify details match
        if official_license.pharmacy_name.lower() in platform_pharmacy.name.lower():
            platform_pharmacy.is_active = True
            platform_pharmacy.save()
            
            # Create verification record
            VerificationRecord.objects.create(
                pharmacy=platform_pharmacy,
                verified_by=request.user.mohofficer,
                verification_date=timezone.now(),
                status='approved'
            )
            
            messages.success(request, 'Pharmacy license verified successfully!')
        else:
            messages.error(request, 'Pharmacy details do not match official records.')
    
    except PharmacyLicense.DoesNotExist:
        messages.error(request, 'License not found in official records.')
```

**What it does**: Cross-checks platform pharmacies against official government records.

---

## 🔧 PLATFORM ADMIN SECTION (`platform_admin/`)

*"The system overlords - where administration meets omnipotence!"*

### 🎯 Views (`platform_admin/views.py`)

#### System Dashboard
```python
def admin_dashboard(request):
    # Platform-wide statistics
    stats = {
        'total_users': User.objects.count(),
        'active_pharmacies': Pharmacy.objects.filter(is_active=True).count(),
        'total_orders': Order.objects.count(),
        'pending_verifications': Pharmacy.objects.filter(is_active=False).count(),
        'system_health': check_system_health()
    }
    
    # Recent activity
    recent_orders = Order.objects.order_by('-created_at')[:10]
    recent_registrations = User.objects.order_by('-date_joined')[:10]
```

**What it does**: Provides a bird's-eye view of the entire platform's health and activity.

#### User Management
```python
def manage_users(request):
    users = User.objects.select_related(
        'customer', 'pharmacy', 'deliveryperson', 'mohofficer'
    ).annotate(
        user_type=Case(
            When(customer__isnull=False, then=Value('Customer')),
            When(pharmacy__isnull=False, then=Value('Pharmacy')),
            When(deliveryperson__isnull=False, then=Value('Delivery')),
            When(mohofficer__isnull=False, then=Value('MoH Officer')),
            default=Value('Admin'),
            output_field=CharField()
        )
    )
```

**What it does**: Provides comprehensive user management across all user types.

---

## 🔧 CORE UTILITIES

### 🌍 Location Services (`customer/utils.py`)
```python
def haversine_distance(lat1, lon1, lat2, lon2):
    # Calculate distance between two points on Earth
    R = 6371  # Earth's radius in kilometers
    
    # Convert coordinates to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    return R * c  # Distance in kilometers
```

**What it does**: Calculates real-world distances to show nearest pharmacies first.

### 💰 Ethiopian Payment Integration (`customer/chapa_service.py`)

```python
class ChapaService:
    """Chapa Payment Gateway Integration for Ethiopia"""
    
    def __init__(self):
        self.secret_key = settings.CHAPA_SECRET_KEY
        self.public_key = settings.CHAPA_PUBLIC_KEY
        self.base_url = "https://api.chapa.co/v1"
        
    def initialize_payment(self, order, return_url=None, callback_url=None):
        """Initialize payment with Chapa"""
        try:
            # Create unique transaction reference
            tx_ref = f"ORDER-{order.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            
            payload = {
                'amount': str(order.total_amount),
                'currency': 'ETB',
                'email': order.customer.user.email,
                'first_name': order.customer.name.split()[0] if order.customer.name else order.customer.user.first_name,
                'last_name': order.customer.name.split()[-1] if len(order.customer.name.split()) > 1 else order.customer.user.last_name,
                'phone_number': order.customer.phone,
                'tx_ref': tx_ref,
                'callback_url': callback_url or f"{settings.SITE_URL}/payment/callback/",
                'return_url': return_url or f"{settings.SITE_URL}/payment/success/{order.id}/",
                'description': f'Medicine order from {order.pharmacy.name}',
            }
            
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json',
            }
            
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    # Store transaction reference for verification
                    order.transaction_ref = tx_ref
                    order.save()
                    
                    return {
                        'status': 'success',
                        'checkout_url': result['data']['checkout_url'],
                        'tx_ref': tx_ref
                    }
                else:
                    return {
                        'status': 'error',
                        'message': result.get('message', 'Payment initialization failed')
                    }
            else:
                return {
                    'status': 'error',
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
                
        except requests.RequestException as e:
            logger.error(f"Chapa payment initialization error: {e}")
            return {
                'status': 'error',
                'message': 'Network error occurred. Please try again.'
            }
        except Exception as e:
            logger.error(f"Unexpected error in payment initialization: {e}")
            return {
                'status': 'error',
                'message': 'An unexpected error occurred.'
            }
    
    def verify_payment(self, tx_ref):
        """Verify payment status with Chapa"""
        try:
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
            }
            
            response = requests.get(
                f"{self.base_url}/transaction/verify/{tx_ref}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                return {'status': 'error', 'message': 'Verification failed'}
                
        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            return {'status': 'error', 'message': str(e)}
```

**Code Explanation:**
- `timezone.now().strftime('%Y%m%d%H%M%S')`: Creates timestamp in YYYYMMDDHHMMSS format
- `order.customer.name.split()[0]`: Extracts first name from full name string
- `timeout=30`: Sets 30-second timeout for API requests to prevent hanging
- `requests.RequestException`: Catches all network-related errors
- `logger.error()`: Records errors for debugging without breaking user experience
- `order.transaction_ref = tx_ref`: Stores reference for later verification
- Ethiopian Birr (ETB) currency integration for local payment processing

### 📱 QR Code Generation (`customer/qr_utils.py`)
```python
def generate_qr_code_image(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for display
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

def generate_delivery_code():
    # Create unique delivery codes like "DEL20250721051241a9ee1f"
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"DEL{timestamp}{random_suffix}"
```

**What it does**: Creates unique QR codes for secure delivery verification.

---

## 🎨 FRONTEND MAGIC

### 🎯 JavaScript Location Services
```javascript
// Automatic location detection
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            // Store location for medicine searches
            document.getElementById('search-lat').value = lat;
            document.getElementById('search-lon').value = lon;
            
            updateLocationStatus('Location detected! Showing nearest pharmacies.');
        });
    }
}

// QR Code Scanner Integration
function initializeQRScanner() {
    const video = document.createElement('video');
    const canvas = document.createElement('canvas');
    
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            video.srcObject = stream;
            video.play();
            
            // Scan for QR codes continuously
            setInterval(function() {
                scanFrame(video, canvas);
            }, 100);
        });
}
```

**What it does**: Provides seamless location detection and QR scanning capabilities.

### 🎨 CSS Theme System
```css
/* Customer Theme - Friendly blues and greens */
.customer-theme {
    --primary-color: #3b82f6;
    --secondary-color: #10b981;
    --accent-color: #f59e0b;
}

/* Pharmacy Theme - Professional medical colors */
.pharmacy-theme {
    --primary-color: #dc2626;
    --secondary-color: #059669;
    --accent-color: #7c3aed;
}

/* Delivery Theme - Energetic orange */
.delivery-theme {
    --primary-color: #ea580c;
    --secondary-color: #f97316;
    --accent-color: #eab308;
}
```

**What it does**: Creates distinct visual experiences for each user type.

---

## 🔐 SECURITY FEATURES

### Authentication & Authorization
- **Multi-level user system**: Customers, Pharmacies, Delivery, MoH, Admins
- **Role-based access control**: Each user sees only what they should
- **Secure password handling**: Django's built-in password hashing
- **Session management**: Secure login sessions with timeout

### Data Protection
- **CSRF protection**: Prevents cross-site request forgery
- **SQL injection prevention**: Django ORM parameterized queries
- **File upload validation**: Only safe image files allowed
- **Input sanitization**: All user inputs cleaned and validated

### API Security
- **Rate limiting**: Prevents API abuse
- **Authentication tokens**: Secure API access
- **HTTPS enforcement**: All communications encrypted
- **Environment variables**: Sensitive data never hard-coded

---

## 📊 DATABASE DESIGN

### Relationships Map
```
User (Django) 1:1 → Customer
              1:1 → Pharmacy  
              1:1 → DeliveryPerson
              1:1 → MoHOfficer

Customer 1:Many → Prescriptions
         1:Many → Orders
         
Pharmacy 1:Many → Medicines
         1:Many → Orders
         1:Many → DeliveryPersons
         
Order 1:1 → Delivery
      1:Many → OrderItems
      
Prescription 1:1 → PrescriptionReview
```

### Data Flow
1. **Customer uploads prescription** → OCR extracts text → Pharmacy reviews
2. **Customer searches medicines** → Location-based results → Add to cart
3. **Customer places order** → Payment processing → Delivery assignment
4. **Delivery person scans QR** → Order completion → Payment confirmation

---

## 🚀 DEPLOYMENT ARCHITECTURE

### Development Environment
- **SQLite database**: Simple file-based storage
- **Django development server**: Built-in testing server
- **Local file storage**: Images stored locally
- **Environment variables**: `.env` file configuration

### Production Environment
- **PostgreSQL database**: Robust production database
- **Gunicorn/uWSGI**: Production WSGI servers
- **Nginx**: Reverse proxy and static file serving
- **Cloud storage**: AWS S3 or similar for media files
- **Redis**: Caching and session storage
- **SSL/HTTPS**: Secure communications

---

## 🎉 CONGRATULATIONS!

You now have a complete understanding of your Ethiopian Pharmacy Platform! This system represents a modern, comprehensive solution that:

- **Connects patients with medicines** through intelligent search
- **Digitizes prescription workflows** with AI-powered OCR
- **Ensures medication safety** through government integration
- **Streamlines delivery logistics** with real-time tracking
- **Maintains regulatory compliance** through MoH oversight
- **Provides secure payments** through local integration

Your platform is more than just code - it's a digital healthcare revolution for Ethiopia! 🇪🇹

Each section works together like organs in a body, creating a living, breathing healthcare ecosystem that serves patients, supports pharmacies, empowers delivery heroes, and maintains government oversight.

Welcome to the future of Ethiopian healthcare technology! 🌟