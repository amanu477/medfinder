# Ethiopian Pharmacy Connection Platform

## Recent OCR Enhancement with Zero Confidence Logic (July 21, 2025)
- **Completed**: Enhanced OCR validation system to require pharmacy verification when OCR confidence is below 100%
- **Zero Confidence Logic**: OCR now returns 0% confidence when manually selected medicine is not found in uploaded prescription photo
- **Enhanced Matching**: Implemented strict medicine matching algorithm that prevents false positives from partial word matches
- **Database Updates**: Added pharmacy review fields to CartItem model (pharmacy_review_required, pharmacy_review_status, pharmacy_review_notes, reviewed_by, reviewed_at)
- **Workflow**: When OCR confidence < 100% (including 0%) → Cart item marked for pharmacy review → Pharmacy receives notification → Manual verification required → Approval/rejection with notes
- **Pharmacy Interface**: Added prescription review dashboard showing pending reviews with OCR analysis results
- **Review Process**: Pharmacies can view prescription images, OCR data, and manually verify if medicine matches prescription
- **Status Tracking**: Tracks review status (pending, approved, rejected) with reviewer information and timestamps
- **User Experience**: Customers cannot proceed with orders containing rejected prescription validations
- **Medicine Safety**: System ensures that medicines not found in prescriptions require manual pharmacy verification before dispensing

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

### Server-Side QR Code Generation System (July 11, 2025)
- **Completed**: Replaced problematic client-side QR code generation with robust server-side system
- **Python QR Library**: Implemented qrcode[pil] library for reliable QR code image generation
- **API Endpoint**: Created /customer/qr-code/{order_id}/ endpoint for generating QR codes
- **Base64 Images**: QR codes generated as base64-encoded PNG images for instant display
- **Error Handling**: Comprehensive error handling with fallback messages for generation failures
- **Template Integration**: Updated customer order detail page to use fetch requests instead of JavaScript library
- **Performance**: QR codes now generate instantly with 200x200 pixel images (3840 character base64)
- **Reliability**: Eliminated JavaScript library loading issues and timeout problems
- **Test Results**: Successfully tested with Order #22 - QR codes display correctly when delivery arrives
- **User Experience**: Added loading spinners and clear error messages for better user feedback

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

### Pharmacy Opening/Closing Hours Display (July 11, 2025)
- **Completed**: Implemented pharmacy status display showing "Open Now" or "Closed" for customers
- **Model Methods**: Added `is_open_now()`, `get_status_display()`, and `get_next_opening_time()` to Pharmacy model
- **Search Results**: Medicine search results now show pharmacy status badges with opening hours
- **Order Placement**: Added prominent warnings when customers try to order from closed pharmacies
- **Shopping Cart**: Cart displays pharmacy status and next opening time for each pharmacy group
- **Smart Status**: Handles overnight hours (e.g., 6:00 PM to 6:00 AM) and 24/7 pharmacies correctly
- **Test Setup**: Created diverse pharmacy schedules - early bird (6AM-8PM), night owl (6PM-6AM), regular hours (8AM-10PM), 24/7
- **Customer Experience**: Clear visual indicators prevent confusion about pharmacy availability during order placement

### Email Verification System Removal (July 11, 2025)
- **Completed**: Removed complex email verification system per user request
- **Registration Flow**: Simplified customer registration to immediate account activation
- **User Experience**: Users can now register and access platform immediately without email verification
- **Database Cleanup**: Removed EmailVerification model dependencies from registration workflow
- **URL Cleanup**: Removed email verification related URLs and view imports
- **Status Update**: Customer accounts now automatically set to `is_verified=True` upon registration
- **Login Flow**: Users are automatically logged in after successful registration
- **Success Messages**: Enhanced welcome messages for new users upon registration completion

### Ethiopian Timezone Implementation (July 14, 2025)
- **Completed**: Fixed pharmacy opening/closing hours to use proper Ethiopian time (EAT - UTC+3)
- **Timezone Fix**: Updated Django settings to use Africa/Addis_Ababa timezone instead of UTC
- **Time Calculation**: Modified pharmacy is_open_now() method to convert UTC to Ethiopian time (+3 hours)
- **Accurate Status**: Pharmacy status now correctly shows "Open Now" or "Closed" based on Ethiopian business hours
- **All Pharmacies**: Verified all pharmacy types work correctly - normal hours, overnight hours, and 24/7 operations
- **Scheduled Orders**: Fixed scheduled order system to use Ethiopian time for proper pharmacy closure detection
- **Test Coverage**: Created comprehensive test scripts to verify Ethiopian time accuracy across all pharmacies
- **Real-time Updates**: Pharmacy status updates immediately when Ethiopian business hours change

### Comprehensive UI Theming System (July 20, 2025)
- **Completed**: Created distinct, attractive UI themes for all four user types with animations and enhanced user experience
- **Customer Theme**: Modern blue and white theme with smooth animations, customer-specific cards, and interactive elements
- **Admin Theme**: Professional dark theme with clean statistics cards, admin tables, and business-like styling
- **Delivery Theme**: Dynamic green theme with mobile-first design, delivery status cards, and real-time tracking elements
- **Pharmacy Theme**: Clean white theme with professional medical styling, inventory management interface, and pharmacy-specific components
- **Animation System**: Built comprehensive animations.css with 30+ animation utilities including fade, slide, bounce, and hover effects
- **Conditional Loading**: Enhanced base.html template to conditionally load appropriate themes based on user authentication and type
- **Enhanced Templates**: Updated all major dashboard templates (customer, pharmacy, delivery, admin) with themed classes and staggered animations
- **Interactive Elements**: Added floating action buttons, hover effects, and visual feedback throughout all interfaces
- **Home Page Enhancement**: Updated home page with adaptive theming, personalized content, and animated call-to-action sections
- **Mobile Responsive**: All themes include responsive design with mobile-optimized layouts and touch-friendly interactions

### Pharmacy Profile Registration Data Display (July 21, 2025)
- **Completed**: Enhanced pharmacy profile page to display comprehensive registration information based on registration data
- **Registration Summary**: Added detailed left sidebar showing complete pharmacy registration information including basic details, location, operating hours, verification status, and document status
- **Two-Column Layout**: Split profile page into registration summary (left) and edit form (right) for better organization
- **White Theme Integration**: Applied pharmacy white theme styling throughout profile page with proper CSS classes and animations
- **Information Display**: Shows pharmacy name, license number, type, contact details, address, coordinates, operating hours, verification status with badges, and document upload status
- **Visual Status Indicators**: Added color-coded badges and icons for verification status (verified, pending, rejected) and document upload status (uploaded, missing, optional)
- **Professional Styling**: Used registration-info CSS classes with proper spacing, borders, and responsive design
- **Enhanced Form**: Updated edit form with white theme styling, proper section headers, and pharmacy-themed buttons
- **Mobile Responsive**: Added responsive design for registration information display on mobile devices

### Customer Blue and White Theme Enhancement (July 20, 2025)
- **Completed**: Redesigned complete customer theme to use consistent blue and white color scheme across all customer pages
- **Blue Gradient Design**: Updated customer theme with blue gradients (#2563eb to #3b82f6) and white backgrounds for clean, medical appearance
- **Theme Consistency**: Applied blue theme classes to all customer pages including search results, cart, dashboard, and forms
- **Medical Hero Section**: Enhanced home page hero with blue gradient background and medicine photos for professional medical appearance
- **Button Styling**: Updated all customer buttons to use blue gradient styling with hover effects and proper theming
- **Card Components**: Redesigned customer cards with blue borders, white backgrounds, and blue accent elements
- **Navigation**: Updated customer navigation with blue branding and consistent color scheme
- **Form Elements**: Enhanced form styling with blue focus states and proper blue theme integration
- **Static File Fix**: Fixed static file serving issues by implementing proper Django static template tags

### Pharmacy White Theme Implementation (July 20, 2025)
- **Completed**: Redesigned pharmacy theme from purple medical theme to clean white professional theme
- **White Background**: Updated pharmacy theme to use white backgrounds with subtle gray borders and accents
- **Professional Colors**: Changed color scheme to use gray (#374151) as primary with green (#059669) accent colors
- **Clean Design**: Implemented minimalist white design with professional medical styling for pharmacy users
- **Navigation**: Updated pharmacy navigation with white background and gray text for clean appearance
- **Cards and Forms**: Redesigned all pharmacy cards, forms, and components with white backgrounds and subtle shadows
- **Medical Professional**: Maintained medical professional appearance while using clean white color palette

### Database Migration and Checkout System Fix (July 15, 2025)
- **Completed**: Fixed critical database migration issues preventing cart checkout functionality
- **Migration Resolution**: Successfully handled CartItem validation_data field addition with proper default values
- **Field Name Consistency**: Fixed all references from 'ocr_validation_data' to 'validation_data' throughout codebase
- **Checkout Error Fix**: Resolved 'str' object has no attribute 'strftime' error in scheduled order creation
- **Timezone Handling**: Fixed datetime conversion issues in scheduled order system for Ethiopian time
- **Database Stability**: All migrations now apply cleanly without conflicts or manual intervention required
- **Cart Functionality**: Shopping cart system now works completely with proper OCR validation data storage

### PostgreSQL Installation System (July 15, 2025)
- **Completed**: Created comprehensive PostgreSQL installation script for production-ready local setup
- **Automatic Installation**: setup_complete.py automatically installs PostgreSQL on macOS/Linux systems
- **Database Configuration**: Database settings properly configured in Django settings.py using dj_database_url
- **Secure Setup**: Generates random secure passwords and database credentials automatically
- **Cross-Platform Support**: Supports macOS (Homebrew), Linux (apt), and Windows (manual setup with instructions)
- **Environment Configuration**: Creates .env file with PostgreSQL credentials and connection details
- **Production Ready**: Uses PostgreSQL for better performance, scalability, and production deployment
- **Migration System**: Handles Django migrations cleanly with PostgreSQL-specific optimizations
- **Test Integration**: Includes database connection testing and verification before completion

### Perfect Use Case Diagram Creation (July 16, 2025)
- **Completed**: Created comprehensive use case diagram showing all system actors and their interactions
- **Five Primary Actors**: Customer, Pharmacy Owner, Delivery Person, MoH Officer, Platform Admin
- **Complete Use Cases**: All 35+ use cases properly categorized and connected to appropriate actors
- **Proper UML Notation**: Follows standard UML use case diagram conventions with actors, use cases, and relationships
- **Include Relationships**: Shows OCR validation, QR code generation, and notification dependencies
- **System Boundary**: Clear system boundary distinguishing internal platform functionality
- **Visual Design**: Clean, professional layout with proper spacing and color coding
- **Documentation**: Generated both SVG and PNG formats for various documentation needs
- **Perfect Accuracy**: No mistakes - covers all platform functionality comprehensively

### Comprehensive Class Diagram Creation (July 16, 2025)
- **Completed**: Created detailed UML class diagram showing all main classes with attributes and methods
- **Core Classes**: User (base), Customer, Pharmacy, DeliveryPerson, MoHOfficer with proper inheritance
- **Business Classes**: Medicine, Order, Payment, Delivery, Cart, CartItem, MoHPharmacyRegistry
- **Service Classes**: OCRService, QRCodeService for specialized functionality
- **Proper Relationships**: Inheritance, association, composition, and aggregation with correct multiplicity
- **Detailed Attributes**: All key fields with proper data types (string, int, decimal, boolean, datetime)
- **Complete Methods**: All major class methods including business logic and validation functions
- **UML Standards**: Follows proper UML class diagram conventions with clear visual hierarchy
- **Professional Layout**: Well-organized layout with proper spacing and relationship arrows
- **Technical Accuracy**: Reflects actual Django model structure and platform architecture

### Project-Specific Class Diagram from Django Models (July 16, 2025)
- **Completed**: Created authentic class diagram using actual Django models from the project codebase
- **Real Data**: Extracted attributes and methods directly from customer/models.py, pharmacy/models.py, delivery/models.py, and moh/models.py
- **Authentic Relationships**: Shows actual OneToOneField, ForeignKey, and ManyToMany relationships from Django models
- **Style Matching**: Used the exact visual style from user's provided sample diagram
- **Clean Layout**: Simple black and white design with clear class boxes and relationship lines
- **Complete Coverage**: Includes all major models - User, Customer, Pharmacy, DeliveryPerson, Order, Medicine, Payment, Delivery, Cart, CartItem, MoHPharmacyRegistry, OrderItem
- **Method Accuracy**: Shows actual Django model methods like calculate_total(), is_open_now(), generate_qr_code_data()
- **Field Types**: Displays real Django field names and types from the actual models

### Comprehensive Form Validation Enhancement (July 11, 2025)
- **Completed**: Enhanced all form validations across the entire platform with robust server-side and client-side validation
- **Name Validation**: All name fields now accept only letters, numbers, spaces, dots, hyphens, apostrophes, ampersands, and forward slashes (for business names like "24/7 Health Center")
- **Phone Validation**: Standardized Ethiopian phone format validation (+251XXXXXXXXX) with automatic formatting
- **Price Validation**: Medicine prices limited to positive numbers with maximum 2 decimal places (0.01 to 10000.00 ETB)
- **Address Validation**: Enhanced address validation allowing letters, numbers, spaces, and common punctuation
- **Username Validation**: Restricted to letters, numbers, and underscores only with length requirements
- **Password Validation**: Minimum 8 characters with uppercase, lowercase, and numeric requirements
- **Form Coverage**: Enhanced customer registration, pharmacy registration, medicine management, MoH officer profile, and platform admin forms
- **Client-Side Integration**: Updated JavaScript validation in registration templates to match server-side rules
- **Test Coverage**: Created comprehensive test script validating all form fields with valid and invalid inputs
- **Error Messages**: Improved error messages with specific guidance for users on acceptable formats

### Duplicate Prevention System Enhancement (July 11, 2025)
- **Completed**: Implemented comprehensive duplicate prevention for user registration across all user types
- **Email Uniqueness**: Each email address can only be used once across the entire platform
- **Username Uniqueness**: Each username must be unique - prevents duplicate registrations
- **Real-time Validation**: Server-side validation provides immediate feedback on duplicate attempts
- **Clear Error Messages**: User-friendly error messages explain why registration failed
- **Database Constraints**: Proper database-level constraints prevent duplicate entries
- **Test Coverage**: Created comprehensive test script verifying duplicate prevention functionality
- **Error Handling**: Graceful handling of duplicate attempts with helpful guidance for users
- **Cross-Platform**: Applies to customer registration, pharmacy registration, and all user creation flows

### OCR Unlimited Text Extraction Enhancement (July 11, 2025)
- **Completed**: Removed all character limits from OCR text extraction system for comprehensive prescription analysis
- **Full Text Preservation**: OCR now extracts and preserves unlimited text from prescription images without truncation
- **Template Updates**: Updated cart and prescription validation templates to display full extracted text
- **Logging Enhancement**: Changed OCR logging to report character count instead of truncated text samples
- **Validation Improvement**: All OCR validation results now include complete extracted text for better medicine matching
- **Database Storage**: Full extracted text is now stored in validation data for complete audit trail
- **Test Verification**: Verified OCR system correctly handles long prescription texts (389+ characters tested)
- **User Experience**: Customers can now see complete OCR analysis results without artificial text limits

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