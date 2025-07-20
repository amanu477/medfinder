"""
URL configuration for pharmacy_finder project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from customer import views as customer_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Demo Route
    path('demo/', lambda request: __import__('demo_view').demo_home(request), name='demo'),
    
    # Customer Routes
    path('', customer_views.home, name='home'),
    path('search/', customer_views.search_medicines, name='search_medicines'),
    path('prescription/upload/', customer_views.upload_prescription, name='upload_prescription'),
    path('prescription/success/', customer_views.prescription_success, name='prescription_success'),
    path('customer/', include('customer.urls', namespace='customer')),
    
    # Unified Authentication System
    path('login/', customer_views.unified_login, name='login'),
    path('logout/', customer_views.customer_logout, name='logout'),
    
    # Pharmacy Routes
    path('pharmacy/', include('pharmacy.urls', namespace='pharmacy')),
    
    # Ministry of Health System (Independent Government Portal)
    path('moh/', include('moh.urls', namespace='moh')),
    
    # Platform Admin Dashboard (Independent Admin System)
    path('platform-admin/', include('platform_admin.urls', namespace='platform_admin')),
    
    # Delivery System
    path('delivery/', include('delivery.urls', namespace='delivery')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)