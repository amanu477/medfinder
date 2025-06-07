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
    
    # Admin panel
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/pharmacies/', views.admin_pharmacy_list, name='admin_pharmacy_list'),
    path('admin/pharmacy/<int:pharmacy_id>/', views.admin_pharmacy_detail, name='admin_pharmacy_detail'),
    path('admin/pharmacy/verify/<int:pharmacy_id>/', views.admin_verify_pharmacy, name='admin_verify_pharmacy'),
    path('admin/pharmacy/approve/<int:pharmacy_id>/', views.admin_approve_pharmacy, name='admin_approve_pharmacy'),
    path('admin/pharmacy/reject/<int:pharmacy_id>/', views.admin_reject_pharmacy, name='admin_reject_pharmacy'),
    path('admin/customers/', views.admin_customer_list, name='admin_customer_list'),
    path('admin/medicines/', views.admin_medicine_list, name='admin_medicine_list'),
    path('admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('admin/prescriptions/', views.admin_prescription_list, name='admin_prescription_list'),
]