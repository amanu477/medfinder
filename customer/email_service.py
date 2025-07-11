"""
Email Service for Ethiopian Pharmacy Platform
Handles all email notifications to customers, pharmacies, and other users
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
# from django.contrib.sites.models import Site
import logging

logger = logging.getLogger(__name__)

class EmailNotificationService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@pharmacyconnect.et')
        self.site_name = "Ethiopian Pharmacy Connect"
        self.site_url = "https://pharmacyconnect.et"
    
    def send_html_email(self, subject, template_name, context, recipient_email, fallback_text=None):
        """
        Send HTML email with text fallback
        
        Args:
            subject (str): Email subject
            template_name (str): HTML template name
            context (dict): Template context variables
            recipient_email (str): Recipient email address
            fallback_text (str): Plain text fallback if template fails
        """
        try:
            # Add common context variables
            context.update({
                'site_name': self.site_name,
                'site_url': self.site_url,
                'support_email': 'support@pharmacyconnect.et',
                'support_phone': '+251-911-123-456'
            })
            
            # Render HTML email
            html_content = render_to_string(template_name, context)
            text_content = strip_tags(html_content) if not fallback_text else fallback_text
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[recipient_email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            logger.info(f"Email sent successfully to {recipient_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False
    
    def send_customer_registration_welcome(self, customer_user):
        """Send welcome email to newly registered customers"""
        subject = f"Welcome to {self.site_name}!"
        context = {
            'customer_name': customer_user.get_full_name() or customer_user.username,
            'username': customer_user.username,
            'login_url': f"{self.site_url}/customer/login/",
        }
        
        return self.send_html_email(
            subject=subject,
            template_name='emails/customer_welcome.html',
            context=context,
            recipient_email=customer_user.email,
            fallback_text=f"Welcome to {self.site_name}! Your account has been created successfully."
        )
    
    def send_pharmacy_registration_confirmation(self, pharmacy):
        """Send confirmation email to newly registered pharmacies"""
        subject = "Pharmacy Registration Submitted - Under Review"
        context = {
            'pharmacy_name': pharmacy.name,
            'license_number': pharmacy.license_number,
            'submission_date': pharmacy.created_at,
        }
        
        return self.send_html_email(
            subject=subject,
            template_name='emails/pharmacy_registration.html',
            context=context,
            recipient_email=pharmacy.email,
            fallback_text=f"Your pharmacy registration has been submitted and is under review."
        )
    
    def send_pharmacy_verification_result(self, pharmacy, approved=True, rejection_reason=None):
        """Send pharmacy verification result email"""
        if approved:
            subject = "Pharmacy Registration Approved!"
            template_name = 'emails/pharmacy_approved.html'
        else:
            subject = "Pharmacy Registration Update Required"
            template_name = 'emails/pharmacy_rejected.html'
        
        context = {
            'pharmacy_name': pharmacy.name,
            'license_number': pharmacy.license_number,
            'approved': approved,
            'rejection_reason': rejection_reason,
            'pharmacy_login_url': f"{self.site_url}/pharmacy/login/",
        }
        
        return self.send_html_email(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_email=pharmacy.email
        )
    
    def send_prescription_upload_confirmation(self, prescription):
        """Send confirmation email when prescription is uploaded"""
        subject = "Prescription Upload Confirmation"
        context = {
            'customer_name': prescription.customer_name,
            'upload_date': prescription.created_at,
            'prescription_id': prescription.id,
        }
        
        return self.send_html_email(
            subject=subject,
            template_name='emails/prescription_uploaded.html',
            context=context,
            recipient_email=prescription.customer_email,
            fallback_text="Your prescription has been uploaded successfully and is being processed."
        )
    
    def send_prescription_to_pharmacy_notification(self, prescription, pharmacy):
        """Notify pharmacy when prescription is sent to them"""
        subject = "New Prescription Received for Processing"
        context = {
            'pharmacy_name': pharmacy.name,
            'customer_name': prescription.customer_name,
            'prescription_id': prescription.id,
            'upload_date': prescription.created_at,
            'customer_phone': prescription.customer_phone,
            'pharmacy_dashboard_url': f"{self.site_url}/pharmacy/dashboard/",
        }
        
        return self.send_html_email(
            subject=subject,
            template_name='emails/prescription_to_pharmacy.html',
            context=context,
            recipient_email=pharmacy.email,
            fallback_text=f"New prescription received from {prescription.customer_name}"
        )
    
    def send_prescription_response_to_customer(self, prescription, response_message, pharmacy):
        """Send pharmacy response back to customer"""
        subject = "Response to Your Prescription"
        context = {
            'customer_name': prescription.customer_name,
            'pharmacy_name': pharmacy.name,
            'prescription_id': prescription.id,
            'response_message': response_message,
            'pharmacy_phone': pharmacy.phone,
            'pharmacy_address': pharmacy.address,
        }
        
        return self.send_html_email(
            subject=subject,
            template_name='emails/prescription_response.html',
            context=context,
            recipient_email=prescription.customer_email,
            fallback_text=f"Response from {pharmacy.name}: {response_message}"
        )
    
    def send_order_confirmation(self, order):
        """Send order confirmation email to customer"""
        subject = f"Order Confirmation #{order.id}"
        context = {
            'customer_name': order.customer.name,
            'order_id': order.id,
            'pharmacy_name': order.pharmacy.name,
            'total_amount': order.total_amount,
            'order_date': order.created_at,
            'order_items': order.orderitem_set.all(),
            'order_url': f"{self.site_url}/customer/orders/{order.id}/",
        }
        
        return self.send_html_email(
            subject=subject,
            template_name='emails/order_confirmation.html',
            context=context,
            recipient_email=order.customer.user.email,
            fallback_text=f"Your order #{order.id} has been placed successfully."
        )
    
    def send_order_status_update(self, order, status_message):
        """Send order status update to customer"""
        subject = f"Order #{order.id} Status Update"
        context = {
            'customer_name': order.customer.name,
            'order_id': order.id,
            'pharmacy_name': order.pharmacy.name,
            'status': order.get_status_display(),
            'status_message': status_message,
            'order_url': f"{self.site_url}/customer/orders/{order.id}/",
        }
        
        return self.send_html_email(
            subject=subject,
            template_name='emails/order_status_update.html',
            context=context,
            recipient_email=order.customer.user.email,
            fallback_text=f"Your order #{order.id} status has been updated to {order.get_status_display()}"
        )
    
    def send_order_to_pharmacy_notification(self, order):
        """Notify pharmacy of new order"""
        subject = f"New Order Received #{order.id}"
        context = {
            'pharmacy_name': order.pharmacy.name,
            'customer_name': order.customer.name,
            'order_id': order.id,
            'total_amount': order.total_amount,
            'order_date': order.created_at,
            'order_items': order.orderitem_set.all(),
            'customer_phone': order.customer.phone,
            'pharmacy_dashboard_url': f"{self.site_url}/pharmacy/orders/",
        }
        
        return self.send_html_email(
            subject=subject,
            template_name='emails/order_to_pharmacy.html',
            context=context,
            recipient_email=order.pharmacy.email,
            fallback_text=f"New order #{order.id} received from {order.customer.name}"
        )

# Initialize global email service instance
email_service = EmailNotificationService()