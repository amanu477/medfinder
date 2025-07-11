"""
QR Code utilities for payment verification
"""
import qrcode
import json
import base64
from io import BytesIO
from PIL import Image

def generate_qr_code_image(data, size=(200, 200)):
    """
    Generate QR code image from data
    Returns base64 encoded image string
    """
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        
        # Add data to QR code
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize image
        img = img.resize(size, Image.LANCZOS)
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

def generate_payment_qr_data(order, delivery):
    """
    Generate QR code data for payment verification
    """
    try:
        qr_data = {
            'order_id': order.id,
            'amount': str(order.payment.amount),
            'currency': order.payment.currency,
            'payment_type': order.payment.payment_type,
            'payment_status': order.payment.status,
            'customer_name': order.customer.name,
            'customer_email': order.customer.email,
            'customer_phone': order.customer.phone,
            'pharmacy_name': order.pharmacy.name,
            'pharmacy_phone': order.pharmacy.phone,
            'delivery_tracking': delivery.tracking_number,
            'delivery_status': delivery.status,
            'order_status': order.status,
            'timestamp': order.created_at.isoformat(),
            'verification_code': f'PC{order.id}{delivery.id}'
        }
        
        return json.dumps(qr_data)
    except Exception as e:
        print(f"Error generating QR data: {e}")
        return None