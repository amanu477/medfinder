from django.conf import settings

def google_maps_api_key(request):
    """
    Add the Google Maps API key to every template context
    """
    return {'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY}