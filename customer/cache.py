# Fast caching for medicine search
from django.core.cache import cache
from django.utils import timezone
import hashlib

def get_search_cache_key(query, user_lat=None, user_lon=None):
    """Generate cache key for search results"""
    key_data = f"search_{query}"
    if user_lat and user_lon:
        # Round coordinates to reduce cache variations
        lat_rounded = round(float(user_lat), 3)
        lon_rounded = round(float(user_lon), 3)
        key_data += f"_{lat_rounded}_{lon_rounded}"
    
    return hashlib.md5(key_data.encode()).hexdigest()

def cache_search_results(cache_key, medicines, timeout=300):  # 5 minutes
    """Cache search results"""
    cache.set(cache_key, medicines, timeout)

def get_cached_search_results(cache_key):
    """Get cached search results"""
    return cache.get(cache_key)