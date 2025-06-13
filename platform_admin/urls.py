from django.urls import path
from . import views

app_name = 'platform_admin'

urlpatterns = [
    # Main admin dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),
    
    # Pharmacy management
    path('pharmacies/', views.admin_pharmacy_list, name='admin_pharmacy_list'),
    path('pharmacy/verify/<int:pharmacy_id>/', views.admin_verify_pharmacy, name='admin_verify_pharmacy'),
    path('pharmacy/approve/<int:pharmacy_id>/', views.admin_approve_pharmacy, name='admin_approve_pharmacy'),
    path('pharmacy/reject/<int:pharmacy_id>/', views.admin_reject_pharmacy, name='admin_reject_pharmacy'),
    path('pharmacy/verify-moh/', views.admin_verify_moh, name='admin_verify_moh'),
    
    # User management
    path('customers/', views.admin_customer_list, name='admin_customer_list'),
    
    # Content management
    path('medicines/', views.admin_medicine_list, name='admin_medicine_list'),
    path('orders/', views.admin_order_list, name='admin_order_list'),
    path('prescriptions/', views.admin_prescription_list, name='admin_prescription_list'),
    
    # Admin reporting system
    path('incidents/', views.admin_incident_reports, name='admin_incident_reports'),
    path('incidents/create/', views.admin_create_incident, name='admin_create_incident'),
    path('incidents/<int:incident_id>/', views.admin_incident_detail, name='admin_incident_detail'),
    path('security-alerts/', views.admin_security_alerts, name='admin_security_alerts'),
    path('security-alerts/create/', views.admin_create_security_alert, name='admin_create_security_alert'),
    path('notifications/', views.admin_notifications, name='admin_notifications'),
    path('system-health/', views.admin_system_health, name='admin_system_health'),
    
    # Quick reporting
    path('report-incident/', views.quick_report_incident, name='quick_report_incident'),
]