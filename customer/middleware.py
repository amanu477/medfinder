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
        # Get current messages
        storage = messages.get_messages(request)
        
        # Check if we're in MoH area
        is_moh_area = request.path.startswith('/moh/')
        
        # Filter messages based on context
        filtered_messages = []
        for message in storage:
            message_text = str(message).lower()
            
            # If we're NOT in MoH area, exclude MoH-related messages
            if not is_moh_area:
                # Skip messages containing MoH-related keywords
                moh_keywords = ['ministry', 'moh', 'verification', 'pharmacy license', 'government']
                if any(keyword in message_text for keyword in moh_keywords):
                    continue
            
            # If we're in MoH area, only show relevant messages
            elif is_moh_area:
                # Only show general system messages or MoH-specific messages
                if 'customer' in message_text or 'order' in message_text:
                    continue
            
            filtered_messages.append(message)
        
        # Clear existing messages and add filtered ones back
        storage.used = True  # Mark as used to clear
        for message in filtered_messages:
            messages.add_message(request, message.level, message.message, message.tags)
        
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
        
        # Set notification suppression flags
        if request.is_main_website:
            request.suppress_moh_notifications = True
        else:
            request.suppress_moh_notifications = False
        
        return None