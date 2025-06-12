from django.urls import path
from . import views

# Admin Portal URLs (System Administration)
urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.admin_users, name='admin_users'),
    path('pharmacies/', views.admin_pharmacies, name='admin_pharmacies'),
    path('notifications/', views.admin_notifications, name='admin_notifications'),
    path('analytics/', views.admin_analytics, name='admin_analytics'),
    path('settings/', views.admin_settings, name='admin_settings'),
    path('maintenance/', views.admin_maintenance, name='admin_maintenance'),
    path('logout/', views.admin_logout, name='admin_logout'),
]