# Ethiopian Pharmacy Platform - Complete Code Documentation

## 🏥 Understanding Your Digital Pharmacy Code

This document explains every piece of code in your Ethiopian Pharmacy Platform with real examples from your actual codebase. Each section shows you exactly how the code works and why it's written that way.

---

## 🏗️ Project Structure Overview

```
ethiopian-pharmacy/
├── customer/          # Patient and customer functionality
├── pharmacy/         # Pharmacy management system
├── delivery/         # Delivery tracking and management
├── moh/             # Ministry of Health verification
├── platform_admin/  # System administration
├── templates/       # HTML templates
├── static/          # CSS, JavaScript, images
└── pharmacy_finder/ # Main Django settings
```

---

## 👥 CUSTOMER SECTION (`customer/`)

*"The heart of your platform - where patients find medicines and manage prescriptions"*

### 🗄️ Models (`customer/models.py`) - Data Structure

#### Customer Model
```python
class Customer(models.Model):
    """Customer model for storing customer information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.email}"
```

**Code Explanation:**
- `OneToOneField(User)`: Links each customer to Django's built-in user authentication
- `DecimalField` for coordinates: Stores precise GPS location for finding nearby pharmacies
- `auto_now_add=True`: Automatically sets creation time when record is first saved
- `auto_now=True`: Updates timestamp every time the record is modified
- `is_verified`: Tracks email verification status for security

#### Prescription Model
```python
class Prescription(models.Model):
    """Model for storing prescription information"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    prescription_image = models.ImageField(upload_to='prescriptions/')
    pharmacy = models.ForeignKey('pharmacy.Pharmacy', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription by {self.customer_name}"
```

**Code Explanation:**
- `STATUS_CHOICES`: Defines valid status options as tuples (database_value, display_name)
- `ImageField(upload_to='prescriptions/')`: Stores uploaded images in media/prescriptions/ folder
- `ForeignKey('pharmacy.Pharmacy')`: Links to pharmacy model using string reference to avoid import issues
- `class Meta`: Contains model metadata like default ordering (newest first with `-created_at`)

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