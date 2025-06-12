from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Unified authentication
    path('login/', views.unified_login, name='unified_login'),
    
    # Customer authentication
    path('register/', views.customer_register, name='customer_register'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('logout/', views.customer_logout, name='customer_logout'),
    
    # Customer dashboard and profile
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    
    # Order management
    path('order/<int:medicine_id>/', views.place_order, name='place_order'),
    path('orders/', views.order_history, name='order_history'),
    path('order/detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    
    # Prescription management
    path('prescription/upload/', views.upload_prescription, name='upload_prescription'),
    path('prescription/success/', views.prescription_success, name='prescription_success'),
    
    # Quick incident reporting (moved from admin)
    path('report-incident/', views.quick_report_incident, name='quick_report_incident'),
    
    # Ministry of Health Admin (separate system)
    path('moh/', views.moh_login, name='moh_login'),
    path('moh/dashboard/', views.moh_dashboard, name='moh_dashboard'),
    path('moh/pharmacies/', views.moh_pharmacy_list, name='moh_pharmacy_list'),
    path('moh/pharmacy/add/', views.moh_add_pharmacy, name='moh_add_pharmacy'),
    path('moh/pharmacy/<int:pharmacy_id>/edit/', views.moh_edit_pharmacy, name='moh_edit_pharmacy'),
    path('moh/pharmacy/<int:pharmacy_id>/delete/', views.moh_delete_pharmacy, name='moh_delete_pharmacy'),
    path('moh/logout/', views.moh_logout, name='moh_logout'),
]