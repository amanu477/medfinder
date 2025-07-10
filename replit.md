# Ethiopian Pharmacy Connection Platform

## Overview

This is a comprehensive digital pharmacy ecosystem for Ethiopian users that revolutionizes medicine procurement and healthcare access. The platform creates a seamless connection between customers seeking medications and pharmacies providing them, with integrated Ministry of Health verification and platform administration systems.

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

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
The system includes Chapa payment service integration for Ethiopian Birr transactions, with comprehensive payment tracking and receipt generation.

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
- **Workflow**: Order completion → Automatic delivery creation → Assignment to delivery personnel → Real-time tracking → Customer feedback

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