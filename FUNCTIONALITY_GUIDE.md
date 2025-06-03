# Pharmacy Connection Platform - Functionality Guide

## Overview
A comprehensive pharmacy connection platform that enables seamless prescription management and medicine procurement by linking customers with nearby pharmacies through location-based search and order management.

## Key Technologies
- **Backend**: Django web framework with Python
- **Database**: PostgreSQL with Django ORM
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Authentication**: Django's built-in authentication system
- **Currency**: Ethiopian Birr (ETB)
- **Location Services**: Browser Geolocation API with Haversine formula

---

## Core Functionality

### 1. User Authentication System

#### Implementation:
- **Unified Registration**: Single registration form with dropdown selection for account type (Customer/Pharmacy)
- **Separate Login Flows**: Dedicated login pages for customers and pharmacies
- **User Models**: 
  - `Customer` model linked to Django User model (OneToOne relationship)
  - `Pharmacy` model linked to Django User model (OneToOne relationship)

#### Files:
- `customer/forms.py` - CustomerRegistrationForm, CustomerProfileForm
- `pharmacy/forms.py` - PharmacyRegistrationForm, PharmacyUserForm
- `customer/views.py` - customer_login, customer_register
- `pharmacy/views.py` - pharmacy_login, register

### 2. Location-Based Medicine Search

#### Implementation:
The platform uses the **Haversine formula** to calculate distances between customers and pharmacies, enabling location-based search results.

#### Haversine Formula Implementation:
Located in `customer/utils.py`:

```python
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r
```

#### How Location Search Works:

1. **Location Detection**: 
   - Browser Geolocation API automatically detects user location
   - Fallback manual location button available
   - Location stored in customer profile (latitude/longitude)

2. **Search Process**:
   - User searches for medicine by name
   - System finds all medicines matching search query
   - Calculates distance from user to each pharmacy using Haversine formula
   - Returns results sorted by proximity (nearest first)

3. **Distance Calculation**:
   - Uses spherical law of cosines for accurate earth surface distances
   - Accounts for earth's curvature (6371 km radius)
   - Returns distance in kilometers with 2 decimal precision

#### Files:
- `customer/utils.py` - Haversine distance calculation
- `static/js/location.js` - Browser geolocation handling
- `customer/views.py` - search_medicines view
- `templates/search_results.html` - Location indicator display

### 3. Medicine Management (Pharmacy Side)

#### Implementation:
- **CRUD Operations**: Full Create, Read, Update, Delete for medicines
- **Image Upload**: Medicine images stored in `media/medicines/`
- **Stock Management**: Real-time stock tracking with validation
- **Expiry Tracking**: Automatic detection of expiring medicines (30-day warning)

#### Features:
- Prescription requirement flag
- Stock quantity validation during order placement
- Expired medicine filtering
- Image upload with validation

#### Files:
- `pharmacy/models.py` - Medicine model
- `pharmacy/forms.py` - MedicineForm
- `pharmacy/views.py` - Medicine CRUD operations
- `templates/pharmacy/medicine_*.html` - Medicine management templates

### 4. Order Management System

#### Implementation:
Multi-step order workflow with status tracking:

1. **Order Placement** (Customer):
   - Select medicine and quantity
   - Stock validation before placement
   - Automatic total calculation in ETB
   - Order created with 'pending' status

2. **Order Review** (Pharmacy):
   - View pending orders with customer details
   - Approve or reject orders
   - Stock deduction on approval
   - Email notifications (configurable)

3. **Order Completion**:
   - Mark as completed when customer picks up
   - Order history tracking
   - Status updates with timestamps

#### Order Status Flow:
- `pending` → `approved`/`rejected`
- `approved` → `completed`
- `cancelled` (customer can cancel pending orders)

#### Files:
- `customer/models.py` - Order, OrderItem models
- `customer/views.py` - Order placement and management
- `pharmacy/views.py` - Order approval workflow
- `templates/customer/order_*.html` - Customer order views
- `templates/pharmacy/order_*.html` - Pharmacy order management

### 5. Prescription Management

#### Implementation:
- **Upload System**: Customers upload prescription images
- **Assignment**: Automatic or manual pharmacy assignment
- **Status Tracking**: pending → approved → rejected → completed
- **Image Storage**: Prescriptions stored in `media/prescriptions/`

#### Workflow:
1. Customer uploads prescription with contact details
2. Prescription appears in pharmacy dashboard
3. Pharmacy reviews and updates status
4. Customer receives status updates

#### Files:
- `customer/models.py` - Prescription model
- `customer/forms.py` - PrescriptionForm
- `customer/views.py` - upload_prescription
- `pharmacy/views.py` - prescription_list, update_prescription_status

### 6. Dashboard Systems

#### Customer Dashboard:
- Recent orders display
- Order status notifications
- Quick action buttons
- Recent prescriptions
- Order history access

#### Pharmacy Dashboard:
- Statistics overview (total medicines, orders, etc.)
- Recent prescriptions table
- Expiring medicines alert
- Recent customer orders
- Order management shortcuts

#### Files:
- `customer/views.py` - customer_dashboard
- `pharmacy/views.py` - dashboard
- `templates/customer/dashboard.html`
- `templates/pharmacy/dashboard.html`

---

## Technical Implementation Details

### Database Models

#### Customer Model:
```python
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
```

#### Pharmacy Model:
```python
class Pharmacy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
```

#### Medicine Model:
```python
class Medicine(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    prescription_required = models.BooleanField(default=True)
```

### Security Features

1. **CSRF Protection**: All forms include CSRF tokens
2. **Authentication Required**: Protected views with login decorators
3. **Input Validation**: Form validation for all user inputs
4. **Stock Validation**: Prevents over-ordering
5. **Expired Medicine Filter**: Automatic filtering of expired items

### Performance Optimizations

1. **Efficient Queries**: Uses select_related and prefetch_related for database optimization
2. **Distance Calculation**: Optimized Haversine formula implementation
3. **Image Optimization**: Proper image handling and storage
4. **Caching**: Static file serving with proper headers

---

## Location System Deep Dive

### Why Haversine Formula?

The Haversine formula was chosen because:
1. **Accuracy**: Accounts for Earth's spherical shape
2. **No API Dependencies**: Works without external mapping services
3. **Performance**: Fast calculation for sorting results
4. **Reliability**: Works offline and doesn't require API keys

### Location Detection Flow:

1. **Automatic Detection**:
   ```javascript
   navigator.geolocation.getCurrentPosition(function(position) {
       const lat = position.coords.latitude;
       const lon = position.coords.longitude;
       // Store in form and submit
   });
   ```

2. **Manual Override**: 
   - "Detect My Location" button for re-detection
   - Falls back gracefully if geolocation fails

3. **Distance Sorting**:
   ```python
   def get_nearby_pharmacies_with_medicine(user_lat, user_lon, medicine_query):
       # Find medicines matching query
       # Calculate distances using Haversine
       # Sort by distance (ascending)
       # Return sorted results
   ```

### Search Result Enhancements:

- **Location Indicator**: Shows when results are sorted by proximity
- **Distance Display**: Shows distance to each pharmacy
- **Fallback Ordering**: Alphabetical if no location available

---

## Currency Implementation (ETB)

All pricing throughout the application displays in Ethiopian Birr (ETB):

- Order totals and item prices
- Medicine pricing in pharmacy dashboard
- Order history displays
- JavaScript calculations (price × quantity)
- Database storage in decimal format for precision

### Implementation:
```html
<!-- Instead of ${{ price }} -->
{{ price }} ETB

<!-- JavaScript calculations -->
document.getElementById('total-amount').textContent = total.toFixed(2) + ' ETB';
```

---

## File Structure

```
├── customer/                 # Customer app
│   ├── models.py            # Customer, Order, Prescription models
│   ├── views.py             # Customer functionality
│   ├── forms.py             # Customer forms
│   └── utils.py             # Haversine formula & distance utils
├── pharmacy/                 # Pharmacy app
│   ├── models.py            # Pharmacy, Medicine models
│   ├── views.py             # Pharmacy functionality
│   └── forms.py             # Pharmacy forms
├── templates/               # HTML templates
│   ├── customer/            # Customer templates
│   ├── pharmacy/            # Pharmacy templates
│   └── base.html           # Base template
├── static/                  # Static files
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript files
└── media/                   # Uploaded files
    ├── medicines/          # Medicine images
    └── prescriptions/      # Prescription uploads
```

---

## Future Enhancement Opportunities

1. **Real-time Notifications**: WebSocket integration for instant updates
2. **Payment Integration**: Online payment processing
3. **Advanced Search**: Filters by price, pharmacy rating, etc.
4. **Mobile App**: React Native or Flutter mobile application
5. **Analytics Dashboard**: Business intelligence for pharmacies
6. **Multi-language Support**: Internationalization for local languages

---

This platform successfully combines location-based services, comprehensive order management, and user-friendly interfaces to create a complete pharmacy connection solution for the Ethiopian market.