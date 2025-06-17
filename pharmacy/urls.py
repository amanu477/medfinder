from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.pharmacy_login, name='pharmacy_login'),
    path('logout/', views.pharmacy_logout, name='pharmacy_logout'),
    path('register/', views.register, name='pharmacy_register'),
    
    # Verification
    path('verification/', views.pharmacy_verification, name='pharmacy_verification'),
    path('verification/pending/', views.verification_pending, name='verification_pending'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='pharmacy_dashboard'),
    path('profile/', views.pharmacy_profile, name='pharmacy_profile'),
    
    # Medicines
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/add/', views.add_medicine, name='add_medicine'),
    path('medicines/edit/<int:medicine_id>/', views.edit_medicine, name='edit_medicine'),
    path('medicines/delete/<int:medicine_id>/', views.delete_medicine, name='delete_medicine'),
    
    # Prescriptions
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/update/<int:prescription_id>/', views.update_prescription_status, name='update_prescription_status'),
    
    # Orders
    path('orders/', views.order_management, name='order_management'),
    path('orders/<int:order_id>/', views.order_detail_pharmacy, name='order_detail_pharmacy'),
    path('orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    
    # Receipts
    path('receipts/', views.pharmacy_receipts, name='pharmacy_receipts'),
    path('receipts/<int:receipt_id>/', views.pharmacy_receipt_detail, name='pharmacy_receipt_detail'),
]