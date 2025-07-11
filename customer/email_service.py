"""
Email Verification Service for Ethiopian Pharmacy Platform
Handles email verification for user registration
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class EmailVerificationService:
    """Service for sending email verification codes"""
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@pharmacyconnect.et')
        self.site_name = "Ethiopian Pharmacy Connect"
    
    def generate_verification_code(self):
        """Generate a 6-digit verification code"""
        return get_random_string(6, allowed_chars='0123456789')
    
    def send_verification_email(self, email, verification_code, user_name=None):
        """
        Send verification email with code
        
        Args:
            email (str): Recipient email address
            verification_code (str): 6-digit verification code
            user_name (str): Name of the user (optional)
        """
        try:
            greeting = f"Dear {user_name}," if user_name else "Dear Customer,"
            
            subject = f"Verify Your Email - {self.site_name}"
            message = f"""
{greeting}

Thank you for registering with {self.site_name}!

To complete your account registration, please enter the following verification code on the platform:

Verification Code: {verification_code}

This code will expire in 15 minutes.

If you did not create an account, please ignore this email.

Best regards,
{self.site_name} Team

Note: This is an automated message. Please do not reply to this email.
            """
            
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[email],
                fail_silently=False
            )
            
            logger.info(f"Verification email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {str(e)}")
            return False

# Initialize global email verification service instance
email_verification_service = EmailVerificationService()