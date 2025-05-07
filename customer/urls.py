from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_medicines, name='search_medicines'),
    path('prescription/upload/', views.upload_prescription, name='upload_prescription'),
    path('prescription/success/', views.prescription_success, name='prescription_success'),
    # Location-based API endpoint removed as requested
]