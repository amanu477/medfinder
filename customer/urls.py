from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Customer authentication
    path('register/', views.customer_register, name='customer_register'),
    path('login/', views.customer_login, name='customer_login'),
    path('logout/', views.customer_logout, name='customer_logout'),
    
    # Customer dashboard and profile
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    
    # Order management
    path('order/<int:medicine_id>/', views.place_order, name='place_order'),
    # New prescription validation flow
    path('prescription-validation/<int:medicine_id>/', views.prescription_validation_view, name='prescription_validation'),
    path('confirm-order/<int:medicine_id>/', views.confirm_order_with_prescription, name='confirm_order_with_prescription'),
    path('orders/', views.order_history, name='order_history'),
    path('order/detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    
    # Prescription management
    path('prescription/upload/', views.upload_prescription, name='upload_prescription'),
    path('prescription/success/', views.prescription_success, name='prescription_success'),
    
    # Payment management
    path('payment/initiate/<int:order_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('payment/success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
    
    # Receipt management
    path('receipts/', views.receipt_list, name='receipt_list'),
    path('receipt/<int:receipt_id>/', views.receipt_detail, name='receipt_detail'),
    
    # Quick incident reporting (moved from admin)
    path('report-incident/', views.quick_report_incident, name='quick_report_incident'),
]