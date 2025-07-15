#!/usr/bin/env python3
"""
Generate PostgreSQL Database Design Diagram for Ethiopian Pharmacy Platform
Creates a comprehensive database schema visualization in PNG format
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# Set up the figure
fig, ax = plt.subplots(1, 1, figsize=(20, 14))
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)
ax.axis('off')

# Title
fig.suptitle('Ethiopian Pharmacy Platform - PostgreSQL Database Design', 
             fontsize=24, fontweight='bold', y=0.95)

# Database info
ax.text(10, 13.5, 'Database: pharmacy_platform_db | User: pharmacy_user | Host: localhost:5432 | Engine: PostgreSQL 14+', 
        ha='center', va='center', fontsize=12, style='italic', 
        bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))

# Define table data structure
tables = {
    'auth_user': {
        'pos': (1, 11),
        'fields': [
            ('id', 'INTEGER', True),
            ('username', 'VARCHAR(150)', False),
            ('email', 'VARCHAR(254)', False),
            ('password', 'VARCHAR(128)', False),
            ('first_name', 'VARCHAR(150)', False),
            ('last_name', 'VARCHAR(150)', False),
            ('is_active', 'BOOLEAN', False),
            ('date_joined', 'TIMESTAMP', False)
        ]
    },
    'customer_customer': {
        'pos': (5, 11),
        'fields': [
            ('id', 'INTEGER', True),
            ('user_id', 'INTEGER', 'FK'),
            ('name', 'VARCHAR(100)', False),
            ('email', 'VARCHAR(254)', False),
            ('phone', 'VARCHAR(20)', False),
            ('address', 'TEXT', False),
            ('latitude', 'DECIMAL(10,8)', False),
            ('longitude', 'DECIMAL(11,8)', False),
            ('is_verified', 'BOOLEAN', False),
            ('created_at', 'TIMESTAMP', False)
        ]
    },
    'pharmacy_pharmacy': {
        'pos': (9, 11),
        'fields': [
            ('id', 'INTEGER', True),
            ('user_id', 'INTEGER', 'FK'),
            ('name', 'VARCHAR(200)', False),
            ('license_number', 'VARCHAR(50)', False),
            ('owner_name', 'VARCHAR(100)', False),
            ('address', 'TEXT', False),
            ('phone', 'VARCHAR(20)', False),
            ('latitude', 'DECIMAL(10,8)', False),
            ('longitude', 'DECIMAL(11,8)', False),
            ('is_verified', 'BOOLEAN', False),
            ('opening_time', 'TIME', False),
            ('closing_time', 'TIME', False)
        ]
    },
    'pharmacy_medicine': {
        'pos': (13, 11),
        'fields': [
            ('id', 'INTEGER', True),
            ('pharmacy_id', 'INTEGER', 'FK'),
            ('name', 'VARCHAR(200)', False),
            ('generic_name', 'VARCHAR(200)', False),
            ('dosage', 'VARCHAR(50)', False),
            ('price', 'DECIMAL(10,2)', False),
            ('stock_quantity', 'INTEGER', False),
            ('is_prescription_required', 'BOOLEAN', False),
            ('is_available', 'BOOLEAN', False)
        ]
    },
    'customer_order': {
        'pos': (5, 7.5),
        'fields': [
            ('id', 'INTEGER', True),
            ('customer_id', 'INTEGER', 'FK'),
            ('pharmacy_id', 'INTEGER', 'FK'),
            ('order_number', 'VARCHAR(20)', False),
            ('status', 'VARCHAR(20)', False),
            ('total_amount', 'DECIMAL(10,2)', False),
            ('delivery_address', 'TEXT', False),
            ('is_scheduled', 'BOOLEAN', False),
            ('scheduled_time', 'TIMESTAMP', False),
            ('created_at', 'TIMESTAMP', False)
        ]
    },
    'customer_orderitem': {
        'pos': (1, 7.5),
        'fields': [
            ('id', 'INTEGER', True),
            ('order_id', 'INTEGER', 'FK'),
            ('medicine_id', 'INTEGER', 'FK'),
            ('quantity', 'INTEGER', False),
            ('price', 'DECIMAL(10,2)', False),
            ('subtotal', 'DECIMAL(10,2)', False)
        ]
    },
    'customer_cart': {
        'pos': (5, 5),
        'fields': [
            ('id', 'INTEGER', True),
            ('customer_id', 'INTEGER', 'FK'),
            ('prescription_image', 'VARCHAR(100)', False),
            ('created_at', 'TIMESTAMP', False),
            ('updated_at', 'TIMESTAMP', False)
        ]
    },
    'customer_cartitem': {
        'pos': (1, 5),
        'fields': [
            ('id', 'INTEGER', True),
            ('cart_id', 'INTEGER', 'FK'),
            ('medicine_id', 'INTEGER', 'FK'),
            ('quantity', 'INTEGER', False),
            ('validation_data', 'TEXT', False),
            ('created_at', 'TIMESTAMP', False)
        ]
    },
    'customer_payment': {
        'pos': (5, 2.5),
        'fields': [
            ('id', 'INTEGER', True),
            ('order_id', 'INTEGER', 'FK'),
            ('payment_method', 'VARCHAR(20)', False),
            ('payment_status', 'VARCHAR(20)', False),
            ('amount', 'DECIMAL(10,2)', False),
            ('transaction_id', 'VARCHAR(100)', False),
            ('created_at', 'TIMESTAMP', False)
        ]
    },
    'delivery_deliveryperson': {
        'pos': (13, 7.5),
        'fields': [
            ('id', 'INTEGER', True),
            ('user_id', 'INTEGER', 'FK'),
            ('pharmacy_id', 'INTEGER', 'FK'),
            ('employee_id', 'VARCHAR(20)', False),
            ('phone', 'VARCHAR(15)', False),
            ('vehicle_type', 'VARCHAR(50)', False),
            ('is_available', 'BOOLEAN', False),
            ('rating', 'DECIMAL(3,2)', False),
            ('total_deliveries', 'INTEGER', False)
        ]
    },
    'delivery_delivery': {
        'pos': (13, 5),
        'fields': [
            ('id', 'INTEGER', True),
            ('order_id', 'INTEGER', 'FK'),
            ('delivery_person_id', 'INTEGER', 'FK'),
            ('status', 'VARCHAR(20)', False),
            ('delivery_address', 'TEXT', False),
            ('estimated_delivery_time', 'TIMESTAMP', False),
            ('actual_delivery_time', 'TIMESTAMP', False),
            ('notes', 'TEXT', False),
            ('created_at', 'TIMESTAMP', False)
        ]
    },
    'moh_mohpharmacyregistry': {
        'pos': (17, 11),
        'fields': [
            ('id', 'INTEGER', True),
            ('pharmacy_id', 'INTEGER', 'FK'),
            ('pharmacy_name', 'VARCHAR(200)', False),
            ('license_number', 'VARCHAR(50)', False),
            ('owner_name', 'VARCHAR(100)', False),
            ('pharmacist_name', 'VARCHAR(100)', False),
            ('region', 'VARCHAR(20)', False),
            ('license_status', 'VARCHAR(20)', False),
            ('compliance_score', 'INTEGER', False),
            ('verified_by', 'INTEGER', 'FK')
        ]
    },
    'moh_mohofficer': {
        'pos': (17, 7.5),
        'fields': [
            ('id', 'INTEGER', True),
            ('user_id', 'INTEGER', 'FK'),
            ('officer_id', 'VARCHAR(20)', False),
            ('name', 'VARCHAR(100)', False),
            ('department', 'VARCHAR(100)', False),
            ('position', 'VARCHAR(100)', False),
            ('region', 'VARCHAR(20)', False),
            ('phone', 'VARCHAR(20)', False),
            ('is_active', 'BOOLEAN', False)
        ]
    }
}

# Function to draw a table
def draw_table(table_name, table_data, ax):
    x, y = table_data['pos']
    fields = table_data['fields']
    
    # Calculate table height
    field_height = 0.3
    header_height = 0.4
    table_height = header_height + len(fields) * field_height
    table_width = 3.5
    
    # Draw table background
    table_rect = FancyBboxPatch((x-table_width/2, y-table_height), table_width, table_height,
                               boxstyle="round,pad=0.05", facecolor='white', 
                               edgecolor='#3498db', linewidth=2)
    ax.add_patch(table_rect)
    
    # Draw header
    header_rect = FancyBboxPatch((x-table_width/2, y-header_height), table_width, header_height,
                                boxstyle="round,pad=0.05", facecolor='#3498db', 
                                edgecolor='#3498db', linewidth=2)
    ax.add_patch(header_rect)
    
    # Table name
    ax.text(x, y-header_height/2, table_name, ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white')
    
    # Draw fields
    for i, (field_name, field_type, is_key) in enumerate(fields):
        field_y = y - header_height - (i + 0.5) * field_height
        
        # Color coding for keys
        if is_key == True:  # Primary key
            color = '#e74c3c'
            weight = 'bold'
        elif is_key == 'FK':  # Foreign key
            color = '#9b59b6'
            weight = 'normal'
            field_name = field_name + ' (FK)'
        else:
            color = '#2c3e50'
            weight = 'normal'
        
        # Field name
        ax.text(x - table_width/2 + 0.1, field_y, field_name, ha='left', va='center', 
                fontsize=8, color=color, weight=weight)
        
        # Field type
        ax.text(x + table_width/2 - 0.1, field_y, field_type, ha='right', va='center', 
                fontsize=7, color='#7f8c8d')

# Draw all tables
for table_name, table_data in tables.items():
    draw_table(table_name, table_data, ax)

# Define relationships (simplified connections)
relationships = [
    ('auth_user', 'customer_customer', 'user_id'),
    ('auth_user', 'pharmacy_pharmacy', 'user_id'),
    ('auth_user', 'delivery_deliveryperson', 'user_id'),
    ('auth_user', 'moh_mohofficer', 'user_id'),
    ('customer_customer', 'customer_order', 'customer_id'),
    ('customer_customer', 'customer_cart', 'customer_id'),
    ('pharmacy_pharmacy', 'customer_order', 'pharmacy_id'),
    ('pharmacy_pharmacy', 'pharmacy_medicine', 'pharmacy_id'),
    ('pharmacy_pharmacy', 'delivery_deliveryperson', 'pharmacy_id'),
    ('pharmacy_pharmacy', 'moh_mohpharmacyregistry', 'pharmacy_id'),
    ('customer_order', 'customer_orderitem', 'order_id'),
    ('customer_order', 'customer_payment', 'order_id'),
    ('customer_order', 'delivery_delivery', 'order_id'),
    ('customer_cart', 'customer_cartitem', 'cart_id'),
    ('pharmacy_medicine', 'customer_orderitem', 'medicine_id'),
    ('pharmacy_medicine', 'customer_cartitem', 'medicine_id'),
    ('delivery_deliveryperson', 'delivery_delivery', 'delivery_person_id'),
    ('moh_mohofficer', 'moh_mohpharmacyregistry', 'verified_by')
]

# Draw relationship lines (simplified)
def draw_relationship_line(from_table, to_table, ax):
    from_pos = tables[from_table]['pos']
    to_pos = tables[to_table]['pos']
    
    # Simple straight line connection
    line = ConnectionPatch(from_pos, to_pos, "data", "data",
                          arrowstyle="->", shrinkA=50, shrinkB=50,
                          mutation_scale=20, fc="red", ec="red", alpha=0.6)
    ax.add_patch(line)

# Draw some key relationships (avoid overcrowding)
key_relationships = [
    ('auth_user', 'customer_customer'),
    ('auth_user', 'pharmacy_pharmacy'),
    ('customer_customer', 'customer_order'),
    ('pharmacy_pharmacy', 'pharmacy_medicine'),
    ('customer_order', 'customer_payment'),
    ('customer_order', 'delivery_delivery'),
    ('pharmacy_pharmacy', 'delivery_deliveryperson'),
    ('auth_user', 'moh_mohofficer')
]

for from_table, to_table in key_relationships:
    draw_relationship_line(from_table, to_table, ax)

# Add legend
legend_elements = [
    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#e74c3c', 
               markersize=10, label='Primary Key'),
    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#9b59b6', 
               markersize=10, label='Foreign Key'),
    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#3498db', 
               markersize=10, label='Table Header'),
    plt.Line2D([0], [0], color='red', linewidth=2, alpha=0.6, label='Relationship')
]

ax.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(0.98, 0.02))

# Add summary box
summary_text = """
Database Summary:
• 13 Core Tables
• Multi-user Authentication
• Customer Management
• Pharmacy Operations
• Medicine Inventory
• Order Processing
• Payment Integration
• Delivery Tracking
• MoH Verification
• Complete Audit Trail
"""

ax.text(0.5, 1, summary_text, ha='left', va='top', fontsize=10,
        bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))

# Save as PNG
plt.tight_layout()
plt.savefig('ethiopian_pharmacy_postgresql_database_design.png', 
            dpi=300, bbox_inches='tight', facecolor='white')

print("✅ PostgreSQL Database Design diagram saved as 'ethiopian_pharmacy_postgresql_database_design.png'")
print("📊 Diagram includes all 13 core tables with relationships and field details")
print("🎨 High-resolution PNG format suitable for documentation and presentations")