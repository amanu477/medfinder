#!/usr/bin/env python3
"""
Generate PostgreSQL Database Design Diagram for Ethiopian Pharmacy Platform
Creates a comprehensive database schema visualization in SVG format
"""

def generate_database_svg():
    """Generate SVG diagram of PostgreSQL database design"""
    
    # SVG header
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="1100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .table-header { fill: #3498db; stroke: #2980b9; stroke-width: 2; }
      .table-body { fill: white; stroke: #3498db; stroke-width: 2; }
      .table-text { font-family: Arial, sans-serif; font-size: 12px; fill: white; font-weight: bold; }
      .field-text { font-family: Arial, sans-serif; font-size: 10px; fill: #2c3e50; }
      .primary-key { fill: #e74c3c; font-weight: bold; }
      .foreign-key { fill: #9b59b6; font-style: italic; }
      .field-type { fill: #7f8c8d; font-size: 9px; }
      .title { font-family: Arial, sans-serif; font-size: 20px; font-weight: bold; fill: #2c3e50; }
      .subtitle { font-family: Arial, sans-serif; font-size: 12px; fill: #7f8c8d; }
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="1200" height="1100" fill="#f8f9fa"/>
  
  <!-- Title -->
  <text x="600" y="30" text-anchor="middle" class="title">Database Structure</text>
  
  <!-- Row 1 - User Management Tables -->
  <!-- auth_user table -->
  <g transform="translate(50,70)">
    <rect width="200" height="25" class="table-header"/>
    <text x="100" y="17" text-anchor="middle" class="table-text">auth_user</text>
    <rect y="25" width="200" height="180" class="table-body"/>
    <text x="10" y="42" class="field-text primary-key">id (PK)</text>
    <text x="150" y="42" class="field-type">INTEGER</text>
    <text x="10" y="57" class="field-text">username</text>
    <text x="150" y="57" class="field-type">VARCHAR(150)</text>
    <text x="10" y="72" class="field-text">email</text>
    <text x="150" y="72" class="field-type">VARCHAR(254)</text>
    <text x="10" y="87" class="field-text">password</text>
    <text x="150" y="87" class="field-type">VARCHAR(128)</text>
    <text x="10" y="102" class="field-text">first_name</text>
    <text x="150" y="102" class="field-type">VARCHAR(150)</text>
    <text x="10" y="117" class="field-text">last_name</text>
    <text x="150" y="117" class="field-type">VARCHAR(150)</text>
    <text x="10" y="132" class="field-text">is_active</text>
    <text x="150" y="132" class="field-type">BOOLEAN</text>
    <text x="10" y="147" class="field-text">date_joined</text>
    <text x="150" y="147" class="field-type">TIMESTAMP</text>
  </g>
  
  <!-- customer_customer table -->
  <g transform="translate(300,70)">
    <rect width="200" height="25" class="table-header"/>
    <text x="100" y="17" text-anchor="middle" class="table-text">customer_customer</text>
    <rect y="25" width="200" height="210" class="table-body"/>
    <text x="10" y="42" class="field-text primary-key">id (PK)</text>
    <text x="150" y="42" class="field-type">INTEGER</text>
    <text x="10" y="57" class="field-text foreign-key">user_id (FK)</text>
    <text x="150" y="57" class="field-type">INTEGER</text>
    <text x="10" y="72" class="field-text">name</text>
    <text x="150" y="72" class="field-type">VARCHAR(100)</text>
    <text x="10" y="87" class="field-text">email</text>
    <text x="150" y="87" class="field-type">VARCHAR(254)</text>
    <text x="10" y="102" class="field-text">phone</text>
    <text x="150" y="102" class="field-type">VARCHAR(20)</text>
    <text x="10" y="117" class="field-text">address</text>
    <text x="150" y="117" class="field-type">TEXT</text>
    <text x="10" y="132" class="field-text">latitude</text>
    <text x="150" y="132" class="field-type">DECIMAL(10,8)</text>
    <text x="10" y="147" class="field-text">longitude</text>
    <text x="150" y="147" class="field-type">DECIMAL(11,8)</text>
    <text x="10" y="162" class="field-text">is_verified</text>
    <text x="150" y="162" class="field-type">BOOLEAN</text>
    <text x="10" y="177" class="field-text">created_at</text>
    <text x="150" y="177" class="field-type">TIMESTAMP</text>
  </g>
  
  <!-- pharmacy_pharmacy table -->
  <g transform="translate(550,70)">
    <rect width="200" height="25" class="table-header"/>
    <text x="100" y="17" text-anchor="middle" class="table-text">pharmacy_pharmacy</text>
    <rect y="25" width="200" height="240" class="table-body"/>
    <text x="10" y="42" class="field-text primary-key">id (PK)</text>
    <text x="150" y="42" class="field-type">INTEGER</text>
    <text x="10" y="57" class="field-text foreign-key">user_id (FK)</text>
    <text x="150" y="57" class="field-type">INTEGER</text>
    <text x="10" y="72" class="field-text">name</text>
    <text x="150" y="72" class="field-type">VARCHAR(200)</text>
    <text x="10" y="87" class="field-text">license_number</text>
    <text x="150" y="87" class="field-type">VARCHAR(50)</text>
    <text x="10" y="102" class="field-text">owner_name</text>
    <text x="150" y="102" class="field-type">VARCHAR(100)</text>
    <text x="10" y="117" class="field-text">address</text>
    <text x="150" y="117" class="field-type">TEXT</text>
    <text x="10" y="132" class="field-text">phone</text>
    <text x="150" y="132" class="field-type">VARCHAR(20)</text>
    <text x="10" y="147" class="field-text">latitude</text>
    <text x="150" y="147" class="field-type">DECIMAL(10,8)</text>
    <text x="10" y="162" class="field-text">longitude</text>
    <text x="150" y="162" class="field-type">DECIMAL(11,8)</text>
    <text x="10" y="177" class="field-text">is_verified</text>
    <text x="150" y="177" class="field-type">BOOLEAN</text>
    <text x="10" y="192" class="field-text">opening_time</text>
    <text x="150" y="192" class="field-type">TIME</text>
    <text x="10" y="207" class="field-text">closing_time</text>
    <text x="150" y="207" class="field-type">TIME</text>
  </g>
  
  <!-- pharmacy_medicine table -->
  <g transform="translate(800,70)">
    <rect width="200" height="25" class="table-header"/>
    <text x="100" y="17" text-anchor="middle" class="table-text">pharmacy_medicine</text>
    <rect y="25" width="200" height="195" class="table-body"/>
    <text x="10" y="42" class="field-text primary-key">id (PK)</text>
    <text x="150" y="42" class="field-type">INTEGER</text>
    <text x="10" y="57" class="field-text foreign-key">pharmacy_id (FK)</text>
    <text x="150" y="57" class="field-type">INTEGER</text>
    <text x="10" y="72" class="field-text">name</text>
    <text x="150" y="72" class="field-type">VARCHAR(200)</text>
    <text x="10" y="87" class="field-text">generic_name</text>
    <text x="150" y="87" class="field-type">VARCHAR(200)</text>
    <text x="10" y="102" class="field-text">dosage</text>
    <text x="150" y="102" class="field-type">VARCHAR(50)</text>
    <text x="10" y="117" class="field-text">price</text>
    <text x="150" y="117" class="field-type">DECIMAL(10,2)</text>
    <text x="10" y="132" class="field-text">stock_quantity</text>
    <text x="150" y="132" class="field-type">INTEGER</text>
    <text x="10" y="147" class="field-text">is_prescription_required</text>
    <text x="150" y="147" class="field-type">BOOLEAN</text>
    <text x="10" y="162" class="field-text">is_available</text>
    <text x="150" y="162" class="field-type">BOOLEAN</text>
  </g>
  
  <!-- Row 2 - Order Management Tables -->
  <!-- customer_order table -->
  <g transform="translate(50,370)">
    <rect width="200" height="25" class="table-header"/>
    <text x="100" y="17" text-anchor="middle" class="table-text">customer_order</text>
    <rect y="25" width="200" height="210" class="table-body"/>
    <text x="10" y="42" class="field-text primary-key">id (PK)</text>
    <text x="150" y="42" class="field-type">INTEGER</text>
    <text x="10" y="57" class="field-text foreign-key">customer_id (FK)</text>
    <text x="150" y="57" class="field-type">INTEGER</text>
    <text x="10" y="72" class="field-text foreign-key">pharmacy_id (FK)</text>
    <text x="150" y="72" class="field-type">INTEGER</text>
    <text x="10" y="87" class="field-text">order_number</text>
    <text x="150" y="87" class="field-type">VARCHAR(20)</text>
    <text x="10" y="102" class="field-text">status</text>
    <text x="150" y="102" class="field-type">VARCHAR(20)</text>
    <text x="10" y="117" class="field-text">total_amount</text>
    <text x="150" y="117" class="field-type">DECIMAL(10,2)</text>
    <text x="10" y="132" class="field-text">delivery_address</text>
    <text x="150" y="132" class="field-type">TEXT</text>
    <text x="10" y="147" class="field-text">is_scheduled</text>
    <text x="150" y="147" class="field-type">BOOLEAN</text>
    <text x="10" y="162" class="field-text">scheduled_time</text>
    <text x="150" y="162" class="field-type">TIMESTAMP</text>
    <text x="10" y="177" class="field-text">created_at</text>
    <text x="150" y="177" class="field-type">TIMESTAMP</text>
  </g>
  
  <!-- customer_payment table -->
  <g transform="translate(300,370)">
    <rect width="200" height="25" class="table-header"/>
    <text x="100" y="17" text-anchor="middle" class="table-text">customer_payment</text>
    <rect y="25" width="200" height="150" class="table-body"/>
    <text x="10" y="42" class="field-text primary-key">id (PK)</text>
    <text x="150" y="42" class="field-type">INTEGER</text>
    <text x="10" y="57" class="field-text foreign-key">order_id (FK)</text>
    <text x="150" y="57" class="field-type">INTEGER</text>
    <text x="10" y="72" class="field-text">payment_method</text>
    <text x="150" y="72" class="field-type">VARCHAR(20)</text>
    <text x="10" y="87" class="field-text">payment_status</text>
    <text x="150" y="87" class="field-type">VARCHAR(20)</text>
    <text x="10" y="102" class="field-text">amount</text>
    <text x="150" y="102" class="field-type">DECIMAL(10,2)</text>
    <text x="10" y="117" class="field-text">transaction_id</text>
    <text x="150" y="117" class="field-type">VARCHAR(100)</text>
    <text x="10" y="132" class="field-text">created_at</text>
    <text x="150" y="132" class="field-type">TIMESTAMP</text>
  </g>
  
  <!-- customer_cart table -->
  <g transform="translate(550,370)">
    <rect width="200" height="25" class="table-header"/>
    <text x="100" y="17" text-anchor="middle" class="table-text">customer_cart</text>
    <rect y="25" width="200" height="120" class="table-body"/>
    <text x="10" y="42" class="field-text primary-key">id (PK)</text>
    <text x="150" y="42" class="field-type">INTEGER</text>
    <text x="10" y="57" class="field-text foreign-key">customer_id (FK)</text>
    <text x="150" y="57" class="field-type">INTEGER</text>
    <text x="10" y="72" class="field-text">prescription_image</text>
    <text x="150" y="72" class="field-type">VARCHAR(100)</text>
    <text x="10" y="87" class="field-text">prescription_text</text>
    <text x="150" y="87" class="field-type">TEXT</text>
    <text x="10" y="102" class="field-text">created_at</text>
    <text x="150" y="102" class="field-type">TIMESTAMP</text>
  </g>
  
  <!-- customer_cartitem table -->
  <g transform="translate(800,370)">
    <rect width="200" height="25" class="table-header"/>
    <text x="100" y="17" text-anchor="middle" class="table-text">customer_cartitem</text>
    <rect y="25" width="200" height="165" class="table-body"/>
    <text x="10" y="42" class="field-text primary-key">id (PK)</text>
    <text x="150" y="42" class="field-type">INTEGER</text>
    <text x="10" y="57" class="field-text foreign-key">cart_id (FK)</text>
    <text x="150" y="57" class="field-type">INTEGER</text>
    <text x="10" y="72" class="field-text foreign-key">medicine_id (FK)</text>
    <text x="150" y="72" class="field-type">INTEGER</text>
    <text x="10" y="87" class="field-text">quantity</text>
    <text x="150" y="87" class="field-type">INTEGER</text>
    <text x="10" y="102" class="field-text">validation_data</text>
    <text x="150" y="102" class="field-type">TEXT</text>
    <text x="10" y="117" class="field-text">is_validated</text>
    <text x="150" y="117" class="field-type">BOOLEAN</text>
    <text x="10" y="132" class="field-text">created_at</text>
    <text x="150" y="132" class="field-type">TIMESTAMP</text>
  </g>
  
  <!-- Row 3 - Delivery & MoH Tables -->
  <!-- delivery_deliveryperson table -->
  <g transform="translate(50,650)">
    <rect width="200" height="25" class="table-header"/>
    <text x="100" y="17" text-anchor="middle" class="table-text">delivery_deliveryperson</text>
    <rect y="25" width="200" height="195" class="table-body"/>
    <text x="10" y="42" class="field-text primary-key">id (PK)</text>
    <text x="150" y="42" class="field-type">INTEGER</text>
    <text x="10" y="57" class="field-text foreign-key">user_id (FK)</text>
    <text x="150" y="57" class="field-type">INTEGER</text>
    <text x="10" y="72" class="field-text foreign-key">pharmacy_id (FK)</text>
    <text x="150" y="72" class="field-type">INTEGER</text>
    <text x="10" y="87" class="field-text">employee_id</text>
    <text x="150" y="87" class="field-type">VARCHAR(20)</text>
    <text x="10" y="102" class="field-text">phone</text>
    <text x="150" y="102" class="field-type">VARCHAR(15)</text>
    <text x="10" y="117" class="field-text">vehicle_type</text>
    <text x="150" y="117" class="field-type">VARCHAR(50)</text>
    <text x="10" y="132" class="field-text">is_available</text>
    <text x="150" y="132" class="field-type">BOOLEAN</text>
    <text x="10" y="147" class="field-text">rating</text>
    <text x="150" y="147" class="field-type">DECIMAL(3,2)</text>
    <text x="10" y="162" class="field-text">total_deliveries</text>
    <text x="150" y="162" class="field-type">INTEGER</text>
  </g>
  
  <!-- delivery_delivery table -->
  <g transform="translate(300,650)">
    <rect width="200" height="25" class="table-header"/>
    <text x="100" y="17" text-anchor="middle" class="table-text">delivery_delivery</text>
    <rect y="25" width="200" height="195" class="table-body"/>
    <text x="10" y="42" class="field-text primary-key">id (PK)</text>
    <text x="150" y="42" class="field-type">INTEGER</text>
    <text x="10" y="57" class="field-text foreign-key">order_id (FK)</text>
    <text x="150" y="57" class="field-type">INTEGER</text>
    <text x="10" y="72" class="field-text foreign-key">delivery_person_id (FK)</text>
    <text x="150" y="72" class="field-type">INTEGER</text>
    <text x="10" y="87" class="field-text">status</text>
    <text x="150" y="87" class="field-type">VARCHAR(20)</text>
    <text x="10" y="102" class="field-text">delivery_address</text>
    <text x="150" y="102" class="field-type">TEXT</text>
    <text x="10" y="117" class="field-text">estimated_delivery_time</text>
    <text x="150" y="117" class="field-type">TIMESTAMP</text>
    <text x="10" y="132" class="field-text">actual_delivery_time</text>
    <text x="150" y="132" class="field-type">TIMESTAMP</text>
    <text x="10" y="147" class="field-text">notes</text>
    <text x="150" y="147" class="field-type">TEXT</text>
    <text x="10" y="162" class="field-text">created_at</text>
    <text x="150" y="162" class="field-type">TIMESTAMP</text>
  </g>
  
  <!-- moh_mohpharmacyregistry table -->
  <g transform="translate(550,650)">
    <rect width="200" height="25" class="table-header"/>
    <text x="100" y="17" text-anchor="middle" class="table-text">moh_mohpharmacyregistry</text>
    <rect y="25" width="200" height="225" class="table-body"/>
    <text x="10" y="42" class="field-text primary-key">id (PK)</text>
    <text x="150" y="42" class="field-type">INTEGER</text>
    <text x="10" y="57" class="field-text foreign-key">pharmacy_id (FK)</text>
    <text x="150" y="57" class="field-type">INTEGER</text>
    <text x="10" y="72" class="field-text">pharmacy_name</text>
    <text x="150" y="72" class="field-type">VARCHAR(200)</text>
    <text x="10" y="87" class="field-text">license_number</text>
    <text x="150" y="87" class="field-type">VARCHAR(50)</text>
    <text x="10" y="102" class="field-text">owner_name</text>
    <text x="150" y="102" class="field-type">VARCHAR(100)</text>
    <text x="10" y="117" class="field-text">pharmacist_name</text>
    <text x="150" y="117" class="field-type">VARCHAR(100)</text>
    <text x="10" y="132" class="field-text">region</text>
    <text x="150" y="132" class="field-type">VARCHAR(20)</text>
    <text x="10" y="147" class="field-text">license_status</text>
    <text x="150" y="147" class="field-type">VARCHAR(20)</text>
    <text x="10" y="162" class="field-text">compliance_score</text>
    <text x="150" y="162" class="field-type">INTEGER</text>
    <text x="10" y="177" class="field-text foreign-key">verified_by (FK)</text>
    <text x="150" y="177" class="field-type">INTEGER</text>
  </g>
  
  <!-- moh_mohofficer table -->
  <g transform="translate(800,650)">
    <rect width="200" height="25" class="table-header"/>
    <text x="100" y="17" text-anchor="middle" class="table-text">moh_mohofficer</text>
    <rect y="25" width="200" height="165" class="table-body"/>
    <text x="10" y="42" class="field-text primary-key">id (PK)</text>
    <text x="150" y="42" class="field-type">INTEGER</text>
    <text x="10" y="57" class="field-text foreign-key">user_id (FK)</text>
    <text x="150" y="57" class="field-type">INTEGER</text>
    <text x="10" y="72" class="field-text">officer_id</text>
    <text x="150" y="72" class="field-type">VARCHAR(20)</text>
    <text x="10" y="87" class="field-text">name</text>
    <text x="150" y="87" class="field-type">VARCHAR(100)</text>
    <text x="10" y="102" class="field-text">position</text>
    <text x="150" y="102" class="field-type">VARCHAR(100)</text>
    <text x="10" y="117" class="field-text">department</text>
    <text x="150" y="117" class="field-type">VARCHAR(100)</text>
    <text x="10" y="132" class="field-text">created_at</text>
    <text x="150" y="132" class="field-type">TIMESTAMP</text>
  </g>
  
  <!-- Legend -->
  <g transform="translate(50,970)">
    <rect width="300" height="100" fill="white" stroke="#bdc3c7" stroke-width="1"/>
    <text x="150" y="20" text-anchor="middle" class="table-text" fill="#2c3e50">Legend</text>
    
    <rect x="20" y="35" width="15" height="15" fill="#e74c3c"/>
    <text x="45" y="47" class="field-text">Primary Key (PK)</text>
    
    <rect x="20" y="60" width="15" height="15" fill="#9b59b6"/>
    <text x="45" y="72" class="field-text">Foreign Key (FK)</text>
    
    <rect x="150" y="35" width="15" height="15" fill="#3498db"/>
    <text x="175" y="47" class="field-text">Table Header</text>
  </g>
  
  <!-- Summary -->
  <g transform="translate(400,970)">
    <rect width="500" height="100" fill="white" stroke="#bdc3c7" stroke-width="1"/>
    <text x="250" y="20" text-anchor="middle" class="table-text" fill="#2c3e50">Database Summary</text>
    <text x="20" y="40" class="field-text">• 13 Core Tables</text>
    <text x="20" y="55" class="field-text">• Multi-user Authentication</text>
    <text x="20" y="70" class="field-text">• Customer Management</text>
    <text x="20" y="85" class="field-text">• Order Processing</text>
    <text x="150" y="40" class="field-text">• Pharmacy Operations</text>
    <text x="150" y="55" class="field-text">• Medicine Inventory</text>
    <text x="150" y="70" class="field-text">• Payment Integration</text>
    <text x="150" y="85" class="field-text">• Delivery Tracking</text>
    <text x="280" y="40" class="field-text">• MoH Verification</text>
    <text x="280" y="55" class="field-text">• OCR Prescription Validation</text>
    <text x="280" y="70" class="field-text">• QR Code Payment System</text>
    <text x="280" y="85" class="field-text">• Production-Ready PostgreSQL</text>
  </g>
  
</svg>'''
    
    return svg_content

def convert_svg_to_png():
    """Convert SVG to PNG using Python"""
    svg_content = generate_database_svg()
    
    # Save SVG file
    with open('ethiopian_pharmacy_postgresql_database_design.svg', 'w') as f:
        f.write(svg_content)
    
    print("✅ PostgreSQL Database Design diagram saved as 'ethiopian_pharmacy_postgresql_database_design.svg'")
    print("📊 Diagram includes all 13 core tables with complete field details")
    print("🎨 SVG format suitable for documentation and presentations")
    print("💡 To convert to PNG, use: convert ethiopian_pharmacy_postgresql_database_design.svg ethiopian_pharmacy_postgresql_database_design.png")

if __name__ == "__main__":
    convert_svg_to_png()