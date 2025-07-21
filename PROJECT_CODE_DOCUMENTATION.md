# Ethiopian Pharmacy Platform - Complete Code Documentation

## 🏥 Welcome to Your Digital Pharmacy Empire!

This document breaks down every section of your Ethiopian Pharmacy Platform in simple, enjoyable terms. Think of it as a guided tour through your digital healthcare marketplace!

---

## 🏗️ Project Architecture Overview

Your platform is built like a modern city with different districts, each serving specific residents:

- **Customer District** - Where patients find medicines and upload prescriptions
- **Pharmacy District** - Where pharmacies manage inventory and process orders
- **Delivery District** - Where delivery heroes track and complete deliveries
- **Ministry of Health District** - Where government officials monitor and verify
- **Platform Admin District** - Where system administrators manage everything

---

## 👥 CUSTOMER SECTION (`customer/`)

*"The heart of your platform - where patients become digital health seekers!"*

### 🏠 Models (`customer/models.py`)
Your customer data architecture:

```python
class Customer(models.Model):
    # The digital identity of each patient
    user = OneToOneField(User)  # Links to Django's built-in user system
    name = CharField(max_length=100)  # Patient's full name
    phone = CharField(max_length=15)  # Ethiopian phone number
    address = TextField()  # Where they live
    date_of_birth = DateField()  # Age verification
    created_at = DateTimeField(auto_now_add=True)  # When they joined
```

**What it does**: Creates a complete profile for each patient, storing their personal information safely.

```python
class Prescription(models.Model):
    # Digital prescription storage
    customer = ForeignKey(Customer)  # Who owns this prescription
    pharmacy = ForeignKey('pharmacy.Pharmacy')  # Which pharmacy to send to
    image = ImageField()  # The prescription photo
    status = CharField()  # pending, approved, rejected, completed
    ocr_text = TextField()  # What our AI read from the image
    ocr_confidence = DecimalField()  # How confident the AI is (0-100%)
```

**What it does**: Transforms paper prescriptions into digital format with AI-powered text extraction.

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

### 🎯 Views (`customer/views.py`)
The brain operations that make everything work:

#### Home Page Magic
```python
def home(request):
    # Redirect delivery personnel to their dashboard
    if request.user.is_authenticated:
        try:
            delivery_person = DeliveryPerson.objects.get(user=request.user)
            return redirect('delivery_dashboard')  # No home access for delivery
        except DeliveryPerson.DoesNotExist:
            pass
    # Show beautiful homepage with medicine search
    return render(request, 'home.html')
```

**What it does**: Creates different experiences - delivery people go straight to work, everyone else sees the beautiful search page.

#### Medicine Search Intelligence
```python
def search_medicines(request):
    query = request.GET.get('query', '')
    user_lat = request.GET.get('lat')  # Customer's location
    user_lon = request.GET.get('lon')
    
    # Find medicines matching the search
    medicines = Medicine.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_available=True,  # Only available medicines
        stock_quantity__gt=0,  # Only in-stock items
        expiry_date__gt=timezone.now().date()  # Not expired
    )
    
    # Sort by distance if location provided
    if user_lat and user_lon:
        medicines = sort_by_distance(medicines, user_lat, user_lon)
```

**What it does**: Smart search that finds medicines and shows the closest pharmacies first.

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

*"The digital pharmacy counter - where medicine meets technology!"*

### 🏠 Models (`pharmacy/models.py`)

```python
class Pharmacy(models.Model):
    # The digital pharmacy identity
    user = OneToOneField(User)  # Pharmacy owner's account
    name = CharField(max_length=200)  # "Bethel Pharmacy", "Hayat Pharmacy"
    license_number = CharField(unique=True)  # Government license
    phone = CharField(max_length=15)  # Ethiopian phone
    address = TextField()  # Physical location
    latitude = DecimalField()  # GPS coordinates for map
    longitude = DecimalField()
    is_active = BooleanField(default=False)  # MoH verification status
    operating_hours = JSONField()  # When they're open
```

**What it does**: Creates a complete digital identity for each pharmacy with location tracking.

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

*"The highway heroes - where logistics meets care!"*

### 🏠 Models (`delivery/models.py`)

```python
class DeliveryPerson(models.Model):
    # The delivery hero profile
    user = OneToOneField(User)  # Their login account
    pharmacy = ForeignKey('pharmacy.Pharmacy')  # Which pharmacy they work for
    phone = CharField(max_length=15)  # Contact number
    license_number = CharField()  # Delivery license
    vehicle_type = CharField()  # motorcycle, bicycle, car
    is_available = BooleanField(default=True)  # Ready for deliveries?
    current_latitude = DecimalField()  # Live GPS location
    current_longitude = DecimalField()
    last_location_update = DateTimeField()  # When location was updated
```

**What it does**: Creates profiles for delivery heroes with real-time location tracking.

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

#### QR Code Scanner Magic
```python
def qr_scanner(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'scan':
            # Process QR code scanning
            delivery_code = request.POST.get('delivery_code')
            
            # Priority: QR scanning over manual entry
            if delivery_code:
                order = Order.objects.filter(qr_code=delivery_code).first()
                if order:
                    # Automatically confirm delivery
                    order.status = 'completed'
                    order.save()
                    
                    # For cash payments, confirm payment received
                    if order.payment_method == 'cash_on_delivery':
                        return confirm_cash_payment(request, order.id)
```

**What it does**: Enables instant delivery confirmation with QR codes and handles cash collection.

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

### 💰 Payment Integration (`customer/chapa_service.py`)
```python
class ChapaService:
    def __init__(self):
        self.secret_key = settings.CHAPA_SECRET_KEY
        self.base_url = "https://api.chapa.co/v1"
    
    def initialize_payment(self, order):
        payload = {
            'amount': str(order.total_amount),
            'currency': 'ETB',
            'email': order.customer.user.email,
            'first_name': order.customer.name.split()[0],
            'tx_ref': f'ORDER-{order.id}-{timezone.now().timestamp()}',
            'callback_url': f"{settings.SITE_URL}/payment/callback/",
            'return_url': f"{settings.SITE_URL}/payment/success/",
        }
        
        response = requests.post(
            f"{self.base_url}/transaction/initialize",
            json=payload,
            headers={'Authorization': f'Bearer {self.secret_key}'}
        )
```

**What it does**: Integrates with Ethiopian payment systems for secure online transactions.

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