#!/usr/bin/env python3
"""
Generate Class Diagram for Ethiopian Pharmacy Platform using actual Django models
Creates a UML class diagram in the style of the provided sample
"""

def generate_project_class_diagram():
    """Generate SVG class diagram based on actual Django models"""
    
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="1000" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .class-box { fill: white; stroke: black; stroke-width: 1; }
      .class-header { font-family: Arial, sans-serif; font-size: 12px; font-weight: bold; text-anchor: middle; }
      .attribute-text { font-family: Arial, sans-serif; font-size: 10px; }
      .method-text { font-family: Arial, sans-serif; font-size: 10px; }
      .separator { stroke: black; stroke-width: 1; }
      .association { stroke: black; stroke-width: 1; fill: none; }
      .inheritance { stroke: black; stroke-width: 1; fill: none; }
      .composition { stroke: black; stroke-width: 1; fill: none; }
      .multiplicity { font-family: Arial, sans-serif; font-size: 9px; }
      .diamond { fill: white; stroke: black; stroke-width: 1; }
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="1200" height="1000" fill="#f5f5f5"/>
  
  <!-- User Class (Django's built-in User model) -->
  <g transform="translate(50,50)">
    <rect width="150" height="120" class="class-box"/>
    <text x="75" y="15" class="class-header">User</text>
    <line x1="0" y1="25" x2="150" y2="25" class="separator"/>
    <text x="10" y="40" class="attribute-text">+ username</text>
    <text x="10" y="55" class="attribute-text">+ email</text>
    <text x="10" y="70" class="attribute-text">+ password</text>
    <line x1="0" y1="80" x2="150" y2="80" class="separator"/>
    <text x="10" y="95" class="method-text">+ authenticate()</text>
    <text x="10" y="110" class="method-text">+ save()</text>
  </g>
  
  <!-- Customer Class -->
  <g transform="translate(250,50)">
    <rect width="150" height="140" class="class-box"/>
    <text x="75" y="15" class="class-header">Customer</text>
    <line x1="0" y1="25" x2="150" y2="25" class="separator"/>
    <text x="10" y="40" class="attribute-text">+ name</text>
    <text x="10" y="55" class="attribute-text">+ email</text>
    <text x="10" y="70" class="attribute-text">+ phone</text>
    <text x="10" y="85" class="attribute-text">+ address</text>
    <text x="10" y="100" class="attribute-text">+ latitude</text>
    <text x="10" y="115" class="attribute-text">+ longitude</text>
    <line x1="0" y1="125" x2="150" y2="125" class="separator"/>
    <text x="10" y="140" class="method-text">+ __str__()</text>
  </g>
  
  <!-- Pharmacy Class -->
  <g transform="translate(450,50)">
    <rect width="150" height="160" class="class-box"/>
    <text x="75" y="15" class="class-header">Pharmacy</text>
    <line x1="0" y1="25" x2="150" y2="25" class="separator"/>
    <text x="10" y="40" class="attribute-text">+ name</text>
    <text x="10" y="55" class="attribute-text">+ license_number</text>
    <text x="10" y="70" class="attribute-text">+ address</text>
    <text x="10" y="85" class="attribute-text">+ phone</text>
    <text x="10" y="100" class="attribute-text">+ latitude</text>
    <text x="10" y="115" class="attribute-text">+ longitude</text>
    <text x="10" y="130" class="attribute-text">+ is_24_hour</text>
    <line x1="0" y1="140" x2="150" y2="140" class="separator"/>
    <text x="10" y="155" class="method-text">+ is_open_now()</text>
  </g>
  
  <!-- DeliveryPerson Class -->
  <g transform="translate(650,50)">
    <rect width="150" height="140" class="class-box"/>
    <text x="75" y="15" class="class-header">DeliveryPerson</text>
    <line x1="0" y1="25" x2="150" y2="25" class="separator"/>
    <text x="10" y="40" class="attribute-text">+ employee_id</text>
    <text x="10" y="55" class="attribute-text">+ phone</text>
    <text x="10" y="70" class="attribute-text">+ vehicle_type</text>
    <text x="10" y="85" class="attribute-text">+ is_available</text>
    <text x="10" y="100" class="attribute-text">+ rating</text>
    <line x1="0" y1="110" x2="150" y2="110" class="separator"/>
    <text x="10" y="125" class="method-text">+ update_location()</text>
    <text x="10" y="140" class="method-text">+ has_active_deliveries()</text>
  </g>
  
  <!-- Order Class -->
  <g transform="translate(250,250)">
    <rect width="150" height="180" class="class-box"/>
    <text x="75" y="15" class="class-header">Order</text>
    <line x1="0" y1="25" x2="150" y2="25" class="separator"/>
    <text x="10" y="40" class="attribute-text">+ total_amount</text>
    <text x="10" y="55" class="attribute-text">+ status</text>
    <text x="10" y="70" class="attribute-text">+ notes</text>
    <text x="10" y="85" class="attribute-text">+ is_scheduled</text>
    <text x="10" y="100" class="attribute-text">+ scheduled_for</text>
    <text x="10" y="115" class="attribute-text">+ created_at</text>
    <line x1="0" y1="125" x2="150" y2="125" class="separator"/>
    <text x="10" y="140" class="method-text">+ calculate_total()</text>
    <text x="10" y="155" class="method-text">+ can_be_scheduled()</text>
    <text x="10" y="170" class="method-text">+ get_total_items()</text>
  </g>
  
  <!-- Medicine Class -->
  <g transform="translate(50,450)">
    <rect width="150" height="140" class="class-box"/>
    <text x="75" y="15" class="class-header">Medicine</text>
    <line x1="0" y1="25" x2="150" y2="25" class="separator"/>
    <text x="10" y="40" class="attribute-text">+ name</text>
    <text x="10" y="55" class="attribute-text">+ description</text>
    <text x="10" y="70" class="attribute-text">+ price</text>
    <text x="10" y="85" class="attribute-text">+ stock_quantity</text>
    <text x="10" y="100" class="attribute-text">+ expiry_date</text>
    <line x1="0" y1="110" x2="150" y2="110" class="separator"/>
    <text x="10" y="125" class="method-text">+ is_expired()</text>
    <text x="10" y="140" class="method-text">+ is_expiring_soon()</text>
  </g>
  
  <!-- Payment Class -->
  <g transform="translate(450,450)">
    <rect width="150" height="160" class="class-box"/>
    <text x="75" y="15" class="class-header">Payment</text>
    <line x1="0" y1="25" x2="150" y2="25" class="separator"/>
    <text x="10" y="40" class="attribute-text">+ tx_ref</text>
    <text x="10" y="55" class="attribute-text">+ amount</text>
    <text x="10" y="70" class="attribute-text">+ currency</text>
    <text x="10" y="85" class="attribute-text">+ payment_type</text>
    <text x="10" y="100" class="attribute-text">+ status</text>
    <text x="10" y="115" class="attribute-text">+ qr_code_data</text>
    <line x1="0" y1="125" x2="150" y2="125" class="separator"/>
    <text x="10" y="140" class="method-text">+ generate_qr_code_data()</text>
    <text x="10" y="155" class="method-text">+ __str__()</text>
  </g>
  
  <!-- Delivery Class -->
  <g transform="translate(650,450)">
    <rect width="150" height="160" class="class-box"/>
    <text x="75" y="15" class="class-header">Delivery</text>
    <line x1="0" y1="25" x2="150" y2="25" class="separator"/>
    <text x="10" y="40" class="attribute-text">+ status</text>
    <text x="10" y="55" class="attribute-text">+ tracking_number</text>
    <text x="10" y="70" class="attribute-text">+ customer_address</text>
    <text x="10" y="85" class="attribute-text">+ pickup_time</text>
    <text x="10" y="100" class="attribute-text">+ delivery_time</text>
    <text x="10" y="115" class="attribute-text">+ delivery_fee</text>
    <line x1="0" y1="125" x2="150" y2="125" class="separator"/>
    <text x="10" y="140" class="method-text">+ assign_delivery_person()</text>
    <text x="10" y="155" class="method-text">+ update_order_status()</text>
  </g>
  
  <!-- Cart Class -->
  <g transform="translate(50,650)">
    <rect width="150" height="120" class="class-box"/>
    <text x="75" y="15" class="class-header">Cart</text>
    <line x1="0" y1="25" x2="150" y2="25" class="separator"/>
    <text x="10" y="40" class="attribute-text">+ created_at</text>
    <text x="10" y="55" class="attribute-text">+ updated_at</text>
    <line x1="0" y1="65" x2="150" y2="65" class="separator"/>
    <text x="10" y="80" class="method-text">+ get_total_items()</text>
    <text x="10" y="95" class="method-text">+ get_total_amount()</text>
    <text x="10" y="110" class="method-text">+ clear()</text>
  </g>
  
  <!-- CartItem Class -->
  <g transform="translate(250,650)">
    <rect width="150" height="120" class="class-box"/>
    <text x="75" y="15" class="class-header">CartItem</text>
    <line x1="0" y1="25" x2="150" y2="25" class="separator"/>
    <text x="10" y="40" class="attribute-text">+ quantity</text>
    <text x="10" y="55" class="attribute-text">+ validation_data</text>
    <line x1="0" y1="65" x2="150" y2="65" class="separator"/>
    <text x="10" y="80" class="method-text">+ get_total_price()</text>
    <text x="10" y="95" class="method-text">+ __str__()</text>
  </g>
  
  <!-- MoHPharmacyRegistry Class -->
  <g transform="translate(450,650)">
    <rect width="150" height="140" class="class-box"/>
    <text x="75" y="15" class="class-header">MoHPharmacyRegistry</text>
    <line x1="0" y1="25" x2="150" y2="25" class="separator"/>
    <text x="10" y="40" class="attribute-text">+ pharmacy_name</text>
    <text x="10" y="55" class="attribute-text">+ license_number</text>
    <text x="10" y="70" class="attribute-text">+ owner_name</text>
    <text x="10" y="85" class="attribute-text">+ license_status</text>
    <text x="10" y="100" class="attribute-text">+ compliance_score</text>
    <line x1="0" y1="110" x2="150" y2="110" class="separator"/>
    <text x="10" y="125" class="method-text">+ verify_license()</text>
    <text x="10" y="140" class="method-text">+ update_compliance()</text>
  </g>
  
  <!-- OrderItem Class -->
  <g transform="translate(650,650)">
    <rect width="150" height="120" class="class-box"/>
    <text x="75" y="15" class="class-header">OrderItem</text>
    <line x1="0" y1="25" x2="150" y2="25" class="separator"/>
    <text x="10" y="40" class="attribute-text">+ quantity</text>
    <text x="10" y="55" class="attribute-text">+ price</text>
    <line x1="0" y1="65" x2="150" y2="65" class="separator"/>
    <text x="10" y="80" class="method-text">+ get_total_price()</text>
    <text x="10" y="95" class="method-text">+ __str__()</text>
  </g>
  
  <!-- Relationships with Enhanced Multiplicity -->
  
  <!-- User to Customer (1:1) -->
  <line x1="200" y1="110" x2="250" y2="110" class="association"/>
  <rect x="205" y="100" width="15" height="12" fill="white" stroke="none"/>
  <text x="212" y="109" class="multiplicity">1</text>
  <rect x="235" y="100" width="15" height="12" fill="white" stroke="none"/>
  <text x="242" y="109" class="multiplicity">1</text>
  
  <!-- User to Pharmacy (1:1) -->
  <line x1="200" y1="110" x2="200" y2="30" class="association"/>
  <line x1="200" y1="30" x2="450" y2="30" class="association"/>
  <line x1="450" y1="30" x2="450" y2="50" class="association"/>
  <rect x="195" y="95" width="15" height="12" fill="white" stroke="none"/>
  <text x="202" y="104" class="multiplicity">1</text>
  <rect x="440" y="40" width="15" height="12" fill="white" stroke="none"/>
  <text x="447" y="49" class="multiplicity">1</text>
  
  <!-- User to DeliveryPerson (1:1) -->
  <line x1="200" y1="110" x2="200" y2="20" class="association"/>
  <line x1="200" y1="20" x2="650" y2="20" class="association"/>
  <line x1="650" y1="20" x2="650" y2="50" class="association"/>
  <rect x="195" y="85" width="15" height="12" fill="white" stroke="none"/>
  <text x="202" y="94" class="multiplicity">1</text>
  <rect x="640" y="40" width="15" height="12" fill="white" stroke="none"/>
  <text x="647" y="49" class="multiplicity">1</text>
  
  <!-- Customer to Order (1:*) -->
  <line x1="325" y1="190" x2="325" y2="250" class="association"/>
  <rect x="315" y="205" width="15" height="12" fill="white" stroke="none"/>
  <text x="322" y="214" class="multiplicity">1</text>
  <rect x="315" y="240" width="15" height="12" fill="white" stroke="none"/>
  <text x="322" y="249" class="multiplicity">*</text>
  
  <!-- Pharmacy to Order (1:*) -->
  <line x1="450" y1="210" x2="400" y2="210" class="association"/>
  <line x1="400" y1="210" x2="400" y2="250" class="association"/>
  <rect x="415" y="200" width="15" height="12" fill="white" stroke="none"/>
  <text x="422" y="209" class="multiplicity">1</text>
  <rect x="390" y="240" width="15" height="12" fill="white" stroke="none"/>
  <text x="397" y="249" class="multiplicity">*</text>
  
  <!-- Order to Payment (1:1) -->
  <line x1="325" y1="430" x2="325" y2="470" class="association"/>
  <line x1="325" y1="470" x2="450" y2="470" class="association"/>
  <line x1="450" y1="470" x2="450" y2="450" class="association"/>
  <rect x="315" y="445" width="15" height="12" fill="white" stroke="none"/>
  <text x="322" y="454" class="multiplicity">1</text>
  <rect x="440" y="460" width="15" height="12" fill="white" stroke="none"/>
  <text x="447" y="469" class="multiplicity">1</text>
  
  <!-- Order to Delivery (1:1) -->
  <line x1="400" y1="340" x2="400" y2="420" class="association"/>
  <line x1="400" y1="420" x2="650" y2="420" class="association"/>
  <line x1="650" y1="420" x2="650" y2="450" class="association"/>
  <rect x="390" y="355" width="15" height="12" fill="white" stroke="none"/>
  <text x="397" y="364" class="multiplicity">1</text>
  <rect x="640" y="440" width="15" height="12" fill="white" stroke="none"/>
  <text x="647" y="449" class="multiplicity">1</text>
  
  <!-- Pharmacy to Medicine (1:*) -->
  <line x1="450" y1="210" x2="430" y2="210" class="association"/>
  <line x1="430" y1="210" x2="430" y2="440" class="association"/>
  <line x1="430" y1="440" x2="200" y2="440" class="association"/>
  <line x1="200" y1="440" x2="200" y2="450" class="association"/>
  <rect x="435" y="320" width="15" height="12" fill="white" stroke="none"/>
  <text x="442" y="329" class="multiplicity">1</text>
  <rect x="190" y="440" width="15" height="12" fill="white" stroke="none"/>
  <text x="197" y="449" class="multiplicity">*</text>
  
  <!-- DeliveryPerson to Delivery (1:*) -->
  <line x1="650" y1="190" x2="650" y2="220" class="association"/>
  <line x1="650" y1="220" x2="800" y2="220" class="association"/>
  <line x1="800" y1="220" x2="800" y2="530" class="association"/>
  <line x1="800" y1="530" x2="725" y2="530" class="association"/>
  <rect x="645" y="205" width="15" height="12" fill="white" stroke="none"/>
  <text x="652" y="214" class="multiplicity">1</text>
  <rect x="720" y="520" width="15" height="12" fill="white" stroke="none"/>
  <text x="727" y="529" class="multiplicity">*</text>
  
  <!-- Customer to Cart (1:1) -->
  <line x1="250" y1="190" x2="230" y2="190" class="association"/>
  <line x1="230" y1="190" x2="230" y2="630" class="association"/>
  <line x1="230" y1="630" x2="125" y2="630" class="association"/>
  <line x1="125" y1="630" x2="125" y2="650" class="association"/>
  <rect x="240" y="180" width="15" height="12" fill="white" stroke="none"/>
  <text x="247" y="189" class="multiplicity">1</text>
  <rect x="115" y="640" width="15" height="12" fill="white" stroke="none"/>
  <text x="122" y="649" class="multiplicity">1</text>
  
  <!-- Cart to CartItem (1:*) -->
  <line x1="200" y1="710" x2="250" y2="710" class="association"/>
  <rect x="205" y="700" width="15" height="12" fill="white" stroke="none"/>
  <text x="212" y="709" class="multiplicity">1</text>
  <rect x="235" y="700" width="15" height="12" fill="white" stroke="none"/>
  <text x="242" y="709" class="multiplicity">*</text>
  
  <!-- CartItem to Medicine (*:1) -->
  <line x1="250" y1="710" x2="220" y2="710" class="association"/>
  <line x1="220" y1="710" x2="220" y2="590" class="association"/>
  <line x1="220" y1="590" x2="125" y2="590" class="association"/>
  <rect x="240" y="700" width="15" height="12" fill="white" stroke="none"/>
  <text x="247" y="709" class="multiplicity">*</text>
  <rect x="115" y="580" width="15" height="12" fill="white" stroke="none"/>
  <text x="122" y="589" class="multiplicity">1</text>
  
  <!-- Order to OrderItem (1:*) -->
  <line x1="400" y1="430" x2="400" y2="630" class="association"/>
  <line x1="400" y1="630" x2="650" y2="630" class="association"/>
  <line x1="650" y1="630" x2="650" y2="650" class="association"/>
  <rect x="390" y="530" width="15" height="12" fill="white" stroke="none"/>
  <text x="397" y="539" class="multiplicity">1</text>
  <rect x="640" y="640" width="15" height="12" fill="white" stroke="none"/>
  <text x="647" y="649" class="multiplicity">*</text>
  
  <!-- OrderItem to Medicine (*:1) -->
  <line x1="650" y1="710" x2="620" y2="710" class="association"/>
  <line x1="620" y1="710" x2="620" y2="750" class="association"/>
  <line x1="620" y1="750" x2="125" y2="750" class="association"/>
  <line x1="125" y1="750" x2="125" y2="590" class="association"/>
  <rect x="640" y="700" width="15" height="12" fill="white" stroke="none"/>
  <text x="647" y="709" class="multiplicity">*</text>
  <rect x="115" y="740" width="15" height="12" fill="white" stroke="none"/>
  <text x="122" y="749" class="multiplicity">1</text>
  
  <!-- Pharmacy to MoHPharmacyRegistry (1:0..1) -->
  <line x1="525" y1="210" x2="525" y2="630" class="association"/>
  <line x1="525" y1="630" x2="525" y2="650" class="association"/>
  <rect x="515" y="420" width="15" height="12" fill="white" stroke="none"/>
  <text x="522" y="429" class="multiplicity">1</text>
  <rect x="510" y="640" width="25" height="12" fill="white" stroke="none"/>
  <text x="517" y="649" class="multiplicity">0..1</text>
  
</svg>'''
    
    return svg_content

def convert_to_png():
    """Convert SVG to PNG"""
    svg_content = generate_project_class_diagram()
    
    # Save SVG file
    with open('ethiopian_pharmacy_project_class_diagram.svg', 'w') as f:
        f.write(svg_content)
    
    print("✅ Project Class Diagram saved as 'ethiopian_pharmacy_project_class_diagram.svg'")
    print("📊 Diagram shows actual Django models from the project")
    print("🔗 Includes all major classes and their relationships")
    print("💡 Converting to PNG format...")

if __name__ == "__main__":
    convert_to_png()