from django.urls import path
from . import views

app_name = 'moh'

# Ministry of Health URLs (Independent Government System)
urlpatterns = [
    path('', views.moh_login, name='moh_login'),
    path('login/', views.moh_login, name='moh_login_explicit'),
    path('dashboard/', views.moh_dashboard, name='moh_dashboard'),
    path('pharmacies/', views.moh_pharmacy_list, name='moh_pharmacy_list'),
    path('pharmacy/add/', views.moh_add_pharmacy, name='moh_add_pharmacy'),
    path('pharmacy/<int:pharmacy_id>/edit/', views.moh_edit_pharmacy, name='moh_edit_pharmacy'),
    path('pharmacy/<int:pharmacy_id>/delete/', views.moh_delete_pharmacy, name='moh_delete_pharmacy'),
    path('verification-requests/', views.moh_verification_requests, name='moh_verification_requests'),
    path('verification-requests/<int:request_id>/respond/', views.moh_respond_verification, name='moh_respond_verification'),
    path('logout/', views.moh_logout, name='moh_logout'),
]