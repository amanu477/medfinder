from django.contrib import admin
from .models import Pharmacy, Medicine

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_number', 'phone', 'email', 'is_active')
    search_fields = ('name', 'license_number', 'phone', 'email')
    list_filter = ('is_active',)

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'pharmacy', 'price', 'stock_quantity', 'expiry_date', 'is_available')
    list_filter = ('is_available', 'pharmacy')
    search_fields = ('name', 'description')
    date_hierarchy = 'expiry_date'
