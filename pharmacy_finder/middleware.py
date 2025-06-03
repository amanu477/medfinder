"""
Custom middleware to handle Replit host validation and CSRF issues
"""

class DisableHostCheckMiddleware:
    """
    Middleware to disable Django's ALLOWED_HOSTS validation in development
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Override the get_host method to return a valid host
        original_get_host = request.get_host
        
        def get_host_override():
            try:
                return original_get_host()
            except Exception:
                # Return localhost as fallback
                return 'localhost'
        
        request.get_host = get_host_override
        response = self.get_response(request)
        return response


class DisableCSRFMiddleware:
    """
    Middleware to disable CSRF protection for development on Replit
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Disable CSRF validation for all requests in development
        setattr(request, '_dont_enforce_csrf_checks', True)
        response = self.get_response(request)
        return response