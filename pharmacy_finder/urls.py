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
    
    # Customer Routes
    path('', customer_views.home, name='home'),
    path('search/', customer_views.search_medicines, name='search_medicines'),
    path('prescription/upload/', customer_views.upload_prescription, name='upload_prescription'),
    path('prescription/success/', customer_views.prescription_success, name='prescription_success'),
    path('customer/', include('customer.urls')),
    
    # Pharmacy Routes
    path('pharmacy/', include('pharmacy.urls')),
    
    # Authentication Routes are handled in individual apps
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)