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
        self.base_url = "https://api.chapa.co/v1"
        self.secret_key = getattr(settings, 'CHAPA_SECRET_KEY', None)
        self.public_key = getattr(settings, 'CHAPA_PUBLIC_KEY', None)
        
    def generate_tx_ref(self):
        """Generate unique transaction reference"""
        return f"PCP-{uuid.uuid4().hex[:12].upper()}"
    
    def initialize_payment(self, order, customer_data):
        """Initialize payment with Chapa"""
        if not self.secret_key:
            raise ValueError("Chapa secret key not configured")
            
        tx_ref = self.generate_tx_ref()
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            tx_ref=tx_ref,
            amount=order.total_amount,
            customer_email=customer_data['email'],
            customer_first_name=customer_data['first_name'],
            customer_last_name=customer_data['last_name'],
            customer_phone=customer_data['phone']
        )
        
        # Sanitize customer data to prevent encoding issues
        def sanitize_string(text):
            if not text:
                return ""
            # Remove or replace problematic characters, keep only ASCII and common Unicode
            import unicodedata
            # Normalize unicode characters
            text = unicodedata.normalize('NFKD', str(text))
            # Keep only printable ASCII characters and basic punctuation
            text = ''.join(char for char in text if ord(char) < 128 or char.isalnum())
            return text.strip()
        
        # Prepare payment data for Chapa
        payment_data = {
            "amount": str(order.total_amount),
            "currency": "ETB",
            "email": sanitize_string(customer_data['email']),
            "first_name": sanitize_string(customer_data['first_name']),
            "last_name": sanitize_string(customer_data['last_name']),
            "phone_number": sanitize_string(customer_data['phone']),
            "tx_ref": tx_ref,
            "callback_url": f"{settings.SITE_URL}/payment/callback/",
            "return_url": f"{settings.SITE_URL}/payment/success/",
            "customization": {
                "title": "Ethiopian Pharmacy Platform",
                "description": f"Payment for Order #{order.id}",
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            # Ensure all string data is properly encoded
            import json
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                data=json.dumps(payment_data, ensure_ascii=False).encode('utf-8'),
                headers=headers,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('status') == 'success':
                # Update payment with Chapa response
                payment.chapa_response = response_data
                payment.checkout_url = response_data['data']['checkout_url']
                payment.save()
                
                return {
                    'success': True,
                    'checkout_url': response_data['data']['checkout_url'],
                    'tx_ref': tx_ref,
                    'payment_id': payment.id
                }
            else:
                payment.status = 'failed'
                payment.chapa_response = response_data
                payment.save()
                
                return {
                    'success': False,
                    'error': response_data.get('message', 'Payment initialization failed')
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