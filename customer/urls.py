from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views_ocr_summary import ocr_validation_summary

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
    path('payment/choice/<int:order_id>/', views.payment_choice, name='payment_choice'),
    path('payment/cash/<int:order_id>/', views.cash_payment_choice, name='cash_payment_choice'),
    path('payment/initiate/<int:order_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('payment/success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
    
    # Receipt management
    path('receipts/', views.receipt_list, name='receipt_list'),
    path('receipt/<int:receipt_id>/', views.receipt_detail, name='receipt_detail'),
    
    # Quick incident reporting (moved from admin)
    path('report-incident/', views.quick_report_incident, name='quick_report_incident'),
    
    # Shopping cart
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:medicine_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
    path('cart/bulk-ocr/', views.bulk_ocr_verification, name='bulk_ocr_verification'),
    path('cart/ocr-summary/', ocr_validation_summary, name='ocr_validation_summary'),
]