from django.urls import path
from . import views

urlpatterns = [
    # Delivery person dashboard
    path('dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    
    # Pharmacy delivery management
    path('pharmacy/dashboard/', views.pharmacy_delivery_dashboard, name='pharmacy_delivery_dashboard'),
    path('pharmacy/management/', views.delivery_management, name='delivery_management'),
    path('pharmacy/create-delivery-person/', views.create_delivery_person, name='create_delivery_person'),
    path('pharmacy/assign/<int:order_id>/', views.assign_delivery, name='assign_delivery'),
    
    # Delivery management
    path('delivery/<int:delivery_id>/', views.delivery_detail, name='delivery_detail'),
    path('delivery/<int:delivery_id>/update-status/', views.update_delivery_status, name='update_delivery_status'),
    path('delivery/<int:delivery_id>/confirm-payment/', views.delivery_confirm_payment, name='delivery_confirm_payment'),
    path('delivery/<int:delivery_id>/feedback/', views.delivery_feedback, name='delivery_feedback'),
    path('delivery/<int:delivery_id>/qr-scanner/', views.qr_scanner, name='qr_scanner'),
    path('delivery/<int:delivery_id>/confirm/', views.delivery_confirm_with_code, name='delivery_confirm_with_code'),
    
    # Location tracking
    path('update-location/', views.update_location, name='update_location'),
    
    # Customer tracking
    path('track/<int:order_id>/', views.customer_delivery_tracking, name='customer_delivery_tracking'),
    
    # API endpoints
    path('api/tracking/<int:delivery_id>/', views.get_delivery_tracking_data, name='delivery_tracking_data'),
    
    # Cash payment confirmation
    path('cash-payment/scanner/<int:delivery_id>/', views.cash_payment_qr_scanner, name='cash_payment_qr_scanner'),
    path('cash-payment/confirm/<int:delivery_id>/', views.confirm_cash_payment, name='confirm_cash_payment'),
]