from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.pharmacy_login, name='pharmacy_login'),
    path('register/', views.register, name='register'),
    
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
]