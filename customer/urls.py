from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Customer authentication
    path('register/', views.customer_register, name='customer_register'),
    path('login/', auth_views.LoginView.as_view(template_name='customer/login.html'), name='customer_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='customer_logout'),
    
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
]