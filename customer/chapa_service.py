import requests
import json
import uuid
from datetime import datetime
from django.conf import settings
from .models import Payment, Order
from django.utils import timezone


class ChapaService:
    """Service for handling Chapa payment integration"""
    
    def __init__(self):
        # Use Chapa's test/sandbox environment for development
        self.base_url = "https://api.chapa.co/v1"
        self.secret_key = getattr(settings, 'CHAPA_SECRET_KEY', '')
        self.public_key = getattr(settings, 'CHAPA_PUBLIC_KEY', 'CHAPUBK_TEST-')
        self.test_mode = getattr(settings, 'CHAPA_TEST_MODE', True)
        
    def generate_tx_ref(self):
        """Generate unique transaction reference"""
        return f"PCP-{uuid.uuid4().hex[:12].upper()}"
    
    def initialize_payment(self, order, customer_data):
        """Initialize payment with Chapa"""
        if not self.secret_key:
            raise ValueError("Chapa secret key not configured")
            
        # Check if payment already exists for this order
        try:
            payment = Payment.objects.get(order=order)
            # If payment exists and is successful, return error
            if payment.status == 'success':
                return {
                    'success': False,
                    'error': 'This order has already been paid successfully'
                }
            # If payment exists but failed/pending, update it with new transaction reference
            payment.tx_ref = self.generate_tx_ref()
            payment.status = 'pending'
            payment.customer_email = customer_data['email']
            payment.customer_first_name = customer_data['first_name']
            payment.customer_last_name = customer_data['last_name']
            payment.customer_phone = customer_data['phone']
            payment.save()
        except Payment.DoesNotExist:
            # Create new payment record
            tx_ref = self.generate_tx_ref()
            payment = Payment.objects.create(
                order=order,
                tx_ref=tx_ref,
                amount=order.total_amount,
                customer_email=customer_data['email'],
                customer_first_name=customer_data['first_name'],
                customer_last_name=customer_data['last_name'],
                customer_phone=customer_data['phone']
            )
        
        # Sanitize customer data to prevent encoding issues - ASCII only
        def sanitize_string(text):
            if not text:
                return ""
            # Convert to string and ensure only ASCII characters
            text = str(text)
            # Keep only ASCII characters (0-127)
            sanitized = ""
            for char in text:
                if ord(char) < 128:  # Only ASCII characters
                    sanitized += char
                elif char.isalpha():
                    sanitized += "a"  # Replace with ASCII letter
                elif char.isdigit():
                    sanitized += "1"  # Replace with ASCII digit
                elif char.isspace():
                    sanitized += " "  # Keep space
                # Skip all other non-ASCII characters
            return sanitized.strip()[:50]  # Limit length
        
        # Prepare payment data for Chapa using the payment's transaction reference
        payment_data = {
            "amount": str(order.total_amount),
            "currency": "ETB",
            "email": sanitize_string(customer_data['email']),
            "first_name": sanitize_string(customer_data['first_name']),
            "last_name": sanitize_string(customer_data['last_name']),
            "phone_number": sanitize_string(customer_data['phone']),
            "tx_ref": payment.tx_ref,
            "callback_url": sanitize_string(f"{settings.SITE_URL}/payment/callback/"),
            "return_url": sanitize_string(f"{settings.SITE_URL}/payment/success/"),
            "customization": {
                "title": sanitize_string("Ethiopian Pharmacy Platform"),
                "description": sanitize_string(f"Payment for Order #{order.id}"),
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            # In test mode, simulate successful payment initialization
            if self.test_mode:
                print(f"TEST MODE: Simulating payment initialization for {payment.tx_ref}")
                
                # Simulate successful Chapa response
                mock_response_data = {
                    "status": "success",
                    "message": "Payment initialized successfully (TEST MODE)",
                    "data": {
                        "checkout_url": f"https://checkout.chapa.co/test/{payment.tx_ref}",
                        "tx_ref": payment.tx_ref
                    }
                }
                
                # Update payment with simulated response
                payment.chapa_response = mock_response_data
                payment.checkout_url = mock_response_data['data']['checkout_url']
                payment.save()
                
                return {
                    'success': True,
                    'checkout_url': mock_response_data['data']['checkout_url'],
                    'tx_ref': payment.tx_ref,
                    'payment_id': payment.id
                }
            
            # Production mode - make actual API call
            import json
            
            # Ensure all values in payment_data are ASCII-safe
            safe_payment_data = {}
            for key, value in payment_data.items():
                if isinstance(value, dict):
                    safe_payment_data[key] = {k: sanitize_string(str(v)) for k, v in value.items()}
                else:
                    safe_payment_data[key] = sanitize_string(str(value))
            
            # Create ASCII-safe headers
            safe_headers = {
                "Authorization": f"Bearer {sanitize_string(self.secret_key)}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            # Log the data being sent for debugging
            print(f"Sending payment data: {safe_payment_data}")
            
            # Use requests with explicit encoding
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                data=json.dumps(safe_payment_data).encode('utf-8'),
                headers=safe_headers,
                timeout=30
            )
            
            # Log the response for debugging
            print(f"Chapa API Response Status: {response.status_code}")
            print(f"Chapa API Response Text: {response.text}")
            
            try:
                response_data = response.json()
            except ValueError as e:
                payment.status = 'failed'
                payment.save()
                return {
                    'success': False,
                    'error': f'Invalid JSON response from Chapa API: {str(e)}'
                }
            
            if response.status_code == 200 and response_data.get('status') == 'success':
                # Extract checkout URL safely
                checkout_url = response_data.get('data', {}).get('checkout_url')
                if not checkout_url:
                    payment.status = 'failed'
                    payment.chapa_response = response_data
                    payment.save()
                    return {
                        'success': False,
                        'error': 'No checkout URL received from Chapa API'
                    }
                
                # Update payment with Chapa response
                payment.chapa_response = response_data
                payment.checkout_url = checkout_url
                payment.save()
                
                return {
                    'success': True,
                    'checkout_url': checkout_url,
                    'tx_ref': tx_ref,
                    'payment_id': payment.id
                }
            else:
                payment.status = 'failed'
                payment.chapa_response = response_data
                payment.save()
                
                error_message = response_data.get('message', f'Payment initialization failed (Status: {response.status_code})')
                return {
                    'success': False,
                    'error': error_message
                }
                
        except requests.RequestException as e:
            payment.status = 'failed'
            payment.save()
            
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def verify_payment(self, tx_ref):
        """Verify payment status with Chapa"""
        if not self.secret_key:
            raise ValueError("Chapa secret key not configured")
            
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/transaction/verify/{tx_ref}",
                headers=headers,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Verification failed')
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def handle_webhook(self, webhook_data):
        """Handle Chapa webhook notifications"""
        tx_ref = webhook_data.get('tx_ref')
        status = webhook_data.get('status')
        
        if not tx_ref:
            return {'success': False, 'error': 'No tx_ref provided'}
        
        try:
            payment = Payment.objects.get(tx_ref=tx_ref)
            
            # Verify the payment with Chapa API
            verification_result = self.verify_payment(tx_ref)
            
            if verification_result['success']:
                verified_data = verification_result['data']
                
                if verified_data.get('status') == 'success' and status == 'success':
                    # Payment successful
                    payment.status = 'success'
                    payment.chapa_tx_ref = verified_data.get('reference')
                    payment.paid_at = timezone.now()
                    payment.chapa_response = verified_data
                    payment.save()
                    
                    # Update order status
                    payment.order.status = 'paid'
                    payment.order.save()
                    
                    return {'success': True, 'message': 'Payment confirmed'}
                else:
                    # Payment failed
                    payment.status = 'failed'
                    payment.chapa_response = verified_data
                    payment.save()
                    
                    return {'success': True, 'message': 'Payment failed'}
            else:
                return {'success': False, 'error': 'Verification failed'}
                
        except Payment.DoesNotExist:
            return {'success': False, 'error': 'Payment not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}