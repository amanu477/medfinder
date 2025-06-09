"""
Middleware for filtering notifications based on request context
"""
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin


class NotificationFilterMiddleware(MiddlewareMixin):
    """
    Middleware to filter notifications based on current request path.
    Prevents MoH notifications from appearing on main website.
    """
    
    def process_response(self, request, response):
        """
        Filter messages before response is sent to ensure proper notification separation.
        """
        # Skip filtering if response is not HTML
        if not response.get('Content-Type', '').startswith('text/html'):
            return response
            
        # Check if we're in MoH area
        is_moh_area = request.path.startswith('/moh/')
        
        # If we're on main website, filter out MoH messages from the response content
        if not is_moh_area and hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            
            # Remove MoH-related alert messages from HTML content
            import re
            
            # Pattern to match alert divs containing MoH content
            moh_alert_pattern = r'<div[^>]*class="[^"]*alert[^"]*"[^>]*>[^<]*(?:ministry|moh_admin|moh|Ministry of Health)[^<]*</div>'
            content = re.sub(moh_alert_pattern, '', content, flags=re.IGNORECASE)
            
            # Also remove any standalone MoH welcome messages
            welcome_pattern = r'Welcome to the Ministry of Health system[^<.]*\.?'
            content = re.sub(welcome_pattern, '', content, flags=re.IGNORECASE)
            
            response.content = content.encode('utf-8')
        
        return response


class MoHContextMiddleware(MiddlewareMixin):
    """
    Middleware to add MoH-specific context and ensure proper isolation.
    """
    
    def process_request(self, request):
        """
        Add MoH context flags to request for proper template rendering.
        """
        # Add context flags
        request.is_moh_area = request.path.startswith('/moh/')
        request.is_admin_area = request.path.startswith('/customer/admin/')
        request.is_main_website = not (request.is_moh_area or request.is_admin_area)
        
        # Clear MoH session data when accessing main website
        if request.is_main_website and request.session.get('moh_authenticated'):
            request.session.pop('moh_authenticated', None)
            request.session.pop('moh_officer', None)
            request.session.modified = True
        
        # Set notification suppression flags
        if request.is_main_website:
            request.suppress_moh_notifications = True
        else:
            request.suppress_moh_notifications = False
        
        return None