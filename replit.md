# Ethiopian Pharmacy Connection Platform

## Overview

This is a comprehensive digital pharmacy ecosystem for Ethiopian users that revolutionizes medicine procurement and healthcare access. The platform creates a seamless connection between customers seeking medications and pharmacies providing them, with integrated Ministry of Health verification and platform administration systems.

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

## Recent Changes

### Cash Payment Workflow Enhancement (July 11, 2025)
- **Completed**: Fixed cash payment workflow to prevent duplicate payment creation
- **Status Display**: Customer order detail now shows "Payment on Cash" instead of "Approved" when cash payment is selected
- **Pharmacy Interface**: Pharmacy management shows "Pay on Cash" status with "Complete" button for cash payments
- **Workflow**: Customer selects "Pay on Cash" → Status shows "Payment on Cash" → Pharmacy sees cash status → Complete button activates delivery system
- **Error Handling**: Fixed OneToOne relationship constraint errors by checking existing payments before creation
- **Test Orders**: Order #16 and #19 available for testing the complete workflow

### Delivery Status Tracking Enhancement (July 11, 2025)
- **Completed**: Enhanced customer order detail page to show real-time delivery status updates
- **Status Updates**: Customer can now see when delivery person is assigned, order picked up, on the way, and delivered
- **Delivery Timeline**: Added visual timeline showing delivery progress with timestamps and notes
- **Delivery Person Info**: Shows assigned delivery person details including name, phone, and vehicle type
- **Medicine Details**: Enhanced delivery assignment to display medicine name, quantity, price, and subtotal
- **Visual Design**: Added custom CSS styling for delivery status timeline and progress indicators
- **Test Data**: Created sample delivery tracking records for order #19 to demonstrate functionality

### QR Code Payment Confirmation System (July 11, 2025)
- **Completed**: Implemented QR code-based payment confirmation for delivery completion
- **Cash Payment Flow**: When delivery status is "in_transit", customer order page shows QR code for cash payment verification
- **Online Payment Flow**: Shows QR code for online payment confirmation when payment was processed digitally
- **Delivery Confirmation**: Delivery person must scan QR code and confirm payment before completing delivery
- **Dual Payment System**: Supports both cash collection and online payment verification workflows
- **Payment Types**: Cash on delivery requires physical money collection, online payments require verification confirmation
- **QR Code Data**: Contains order details, payment information, customer data, and delivery tracking for verification
- **Test Setup**: Order #19 configured with cash payment (205.00 ETB) for testing the complete workflow
- **QR Code Library**: Added QR code library to base.html template for proper QR code generation
- **Error Handling**: Fixed QR code generation errors by loading library globally in base template

### Customer Location-Based Delivery Address System (July 11, 2025)
- **Completed**: Enhanced delivery system to use customer's current location as delivery address
- **Location Tracking**: Automatic customer location updates when browsing customer pages
- **Delivery Address**: Delivery addresses now show customer's current coordinates in user-friendly format
- **Location API**: Added customer location update endpoint at /customer/update-location/
- **JavaScript Integration**: Enhanced location.js to automatically update customer location on server
- **Dynamic Updates**: Customer location is updated in real-time and used for delivery creation
- **Address Format**: Delivery addresses display as "Customer Address: Lat X.XXXX, Lon Y.YYYY"
- **Test Data**: Updated Order #19 delivery with customer location (9.0450, 38.7880)

### Delivery Status Workflow Enhancement (July 11, 2025)
- **Completed**: Implemented restricted delivery status updates for delivery personnel
- **Status Progression**: Delivery personnel can only update to specific statuses after pharmacy assignment
- **Workflow Control**: From "assigned" → "picked_up" or "in_transit" → "arrived" → "delivered"
- **New Status**: Added "arrived" status to indicate delivery person has reached customer location
- **QR Code Trigger**: QR code payment verification now shows when delivery status is "arrived"
- **Form Restrictions**: DeliveryStatusUpdateForm now dynamically restricts available status choices
- **Customer Notification**: Automatic notification sent to customer when delivery person arrives
- **Database Migration**: Applied migration to add "arrived" status to delivery model

### QR Code Scanner for Delivery Personnel (July 11, 2025)
- **Completed**: Created comprehensive QR code scanner page for delivery personnel
- **Scanner Technology**: Integrated QR-Scanner library with camera access for real-time scanning
- **Manual Input**: Added manual QR code data input option as backup to camera scanning
- **Payment Verification**: Displays payment details, order information, and customer data from scanned QR codes
- **Dual Payment Support**: Handles both cash on delivery and online payment verification workflows
- **Smart Actions**: Provides context-sensitive action buttons based on payment type
- **Access Control**: QR scanner only available when delivery status is "arrived"
- **Dashboard Integration**: Added QR scanner buttons to delivery dashboard and status update pages
- **URL Structure**: Accessible at /delivery/delivery/{delivery_id}/qr-scanner/
- **Error Handling**: Comprehensive error handling for invalid QR codes and camera permissions
- **File Upload Removed**: Eliminated file upload option per user request, keeping only camera scanning and manual input

### Customer Payment Verification QR Code System (July 11, 2025)
- **Completed**: Fixed customer-side QR code generation for payment verification
- **QR Code Display**: Customer order detail page shows QR code when delivery status is "in_transit" or "arrived"
- **Payment Types**: Generates different QR codes for cash on delivery vs online payment verification
- **QR Code Data**: Contains order ID, amount, currency, customer details, pharmacy info, delivery tracking, and payment status
- **Library Integration**: Fixed QR code library loading issues by ensuring proper script loading order
- **Visual Design**: QR codes displayed in clean containers with payment type indicators
- **Error Handling**: Robust error handling for QR code generation failures with fallback messages
- **Test Data**: Order #19 configured with cash payment (205.00 ETB) and "in_transit" delivery status for testing
- **JavaScript Fix**: Added proper QR code generation script with DOM ready event handling and error checking
- **Test Credentials**: Test customer login available - Username: testcustomer, Password: testpass123

### Delivery-Customer Status Synchronization (July 11, 2025)
- **Completed**: Implemented automatic order status updates when delivery personnel update delivery status
- **Status Mapping**: Delivery "in_transit" → Order "on_the_way", Delivery "arrived" → Order "arrived", Delivery "delivered" → Order "delivered"
- **Model Updates**: Added new order status choices: "on_the_way", "arrived", "delivered"
- **Database Migration**: Applied migration to support new order status values
- **Template Updates**: Enhanced customer order detail page to display new status badges and timeline items
- **Workflow Integration**: Status changes automatically propagate from delivery system to customer order view
- **Real-time Updates**: Customers now see live status updates that match delivery personnel actions
- **QR Code Fix**: Fixed template logic for QR code display when delivery status is "in_transit" or "arrived"
- **Test Credentials**: Order #21 - Username: amanu, Password: testpass123 (50.00 ETB cash payment, arrived status)

## System Architecture

### Multi-User Architecture
The platform operates four distinct user types with separate authentication flows:

1. **Customers** - Medicine seekers and prescription uploaders
2. **Pharmacies** - Medicine providers and inventory managers  
3. **Ministry of Health (MoH)** - Independent regulatory oversight system
4. **Platform Administrators** - System managers and pharmacy verifiers

### Technology Stack
- **Backend Framework**: Django 5.2 with Python 3.11
- **Database**: PostgreSQL (with SQLite fallback for development)
- **Frontend**: Bootstrap 5, responsive HTML/CSS, vanilla JavaScript
- **Authentication**: Django's multi-tier authentication system
- **File Storage**: Local media storage with organized directory structure
- **Location Services**: Browser Geolocation API with Haversine distance calculations

## Key Components

### 1. Customer System (`customer/`)
- **Models**: Customer profiles, Orders, Prescriptions, Payments, Receipts
- **Features**: Medicine search, prescription upload, order management, payment integration
- **Authentication**: Standard Django user authentication with customer profiles

### 2. Pharmacy System (`pharmacy/`)
- **Models**: Pharmacy profiles, Medicine inventory, License validation
- **Features**: Registration with document upload, medicine management, order processing
- **Verification**: Multi-stage verification process with MoH integration

### 3. Ministry of Health System (`moh/`)
- **Models**: Independent MoH registry, Officer management, Verification requests
- **Features**: Separate government portal for pharmacy oversight and license management
- **Database**: Uses separate database routing for data isolation

### 4. Platform Administration (`platform_admin/`)
- **Features**: System oversight, pharmacy verification, incident reporting
- **Access Control**: Superuser-only access with comprehensive dashboard

## Data Flow

### Medicine Search and Ordering
1. Customer searches for medicines using location-based queries
2. System calculates distances using Haversine formula
3. Results filtered by availability and pharmacy verification status
4. Orders placed through integrated workflow

### Pharmacy Verification Process
1. Pharmacy registers with mandatory document uploads
2. Platform admin reviews application
3. System checks against MoH registry for license validation
4. Verification status updated with compliance scoring

### Payment Integration
The system includes comprehensive dual payment system:
- **Chapa Payment Gateway**: For online payment processing in Ethiopian Birr
- **Cash on Delivery**: With QR code generation for delivery personnel verification
- **Order Workflow**: Orders start as "pending" → Pharmacy approval → "approved" status → Payment options appear
- **Payment Tracking**: Comprehensive payment tracking and receipt generation for both payment methods

### OCR Integration
The platform now includes advanced OCR (Optical Character Recognition) functionality:
- **Technology**: Tesseract OCR with PIL image processing
- **Purpose**: Validates manually entered medicine names against uploaded prescriptions
- **Features**: Automatic text extraction, medicine name recognition, fuzzy matching
- **Validation**: 60% confidence threshold with user-friendly warning messages
- **Implementation**: Integrated into order placement process with real-time validation

### Shopping Cart System
The platform includes a comprehensive shopping cart system:
- **Models**: Cart and CartItem with prescription validation data storage
- **Features**: Add/remove items, update quantities, prescription validation per item
- **Bulk OCR**: Single prescription image validates all cart medicines simultaneously
- **Workflow**: Medicine search → Add to cart → Bulk OCR verification → Checkout
- **Multi-pharmacy**: Automatic order grouping by pharmacy during checkout
- **Navigation**: Cart icon with live item count in main navigation

### Delivery System
The platform now includes a complete delivery management system:
- **Models**: DeliveryPerson, Delivery, DeliveryTracking, DeliveryNotification, DeliveryZone
- **Features**: Automatic delivery creation when orders are completed, real-time tracking, delivery personnel management
- **Authentication**: Delivery personnel login through unified authentication system
- **Real-time Tracking**: GPS location updates, delivery status tracking, customer notifications
- **Multi-user Interface**: Separate dashboards for delivery personnel, pharmacy managers, and customers
- **Automatic Availability Management**: Delivery personnel status automatically changes based on active deliveries
- **Workflow**: Order completion → Automatic delivery creation → Assignment to delivery personnel → Real-time tracking → Customer feedback
- **Smart Status Updates**: Available/Not Available status updates automatically when deliveries are assigned, in progress, or completed

## External Dependencies

### Required Python Packages
- Django 5.2 (web framework)
- Pillow (image processing)
- psycopg2-binary (PostgreSQL adapter)
- django-bootstrap5 (UI framework)
- dj-database-url (database configuration)
- gunicorn (WSGI server)
- PyJWT (JSON Web Tokens)
- pytesseract (OCR text extraction)
- opencv-python (image processing)
- fuzzywuzzy (string matching)
- python-levenshtein (string similarity)

### Third-Party Services
- **Chapa Payment Gateway**: For processing Ethiopian Birr transactions
- **Browser Geolocation API**: For location-based pharmacy search
- **PostgreSQL**: Primary database (with SQLite fallback)

## Deployment Strategy

### Database Configuration
The application uses a dual-database strategy:
- **Primary Database**: Platform operations (customers, pharmacies, orders)
- **MoH Database**: Independent government registry (separated for security)

### Local Development Setup
1. **Database Options**: 
   - PostgreSQL (recommended for production)
   - SQLite (simplified for development)
2. **Environment Configuration**: Uses `.env` files for sensitive settings
3. **Media Handling**: Local file storage with organized directory structure

### Production Considerations
- **Security**: Separate authentication systems for different user types
- **Scalability**: Modular app structure allows independent scaling
- **Compliance**: MoH integration ensures regulatory compliance
- **Performance**: Location-based queries optimized with distance calculations

### Setup Scripts
Multiple setup scripts provided for different deployment scenarios:
- `run_local.py`: Automated local setup
- `setup_all_logins.py`: Creates test users for all systems
- `create_moh_officer.py`: Sets up MoH officer accounts
- Various database setup guides for different operating systems

The platform is designed to be easily deployable both locally and in production environments, with comprehensive documentation and automated setup processes.