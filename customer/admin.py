from django.contrib import admin
from .models import Customer, Prescription, Payment

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'pharmacy', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('tx_ref', 'order', 'amount', 'currency', 'status', 'customer_email', 'created_at', 'paid_at')
    list_filter = ('status', 'currency', 'created_at', 'paid_at')
    search_fields = ('tx_ref', 'chapa_tx_ref', 'customer_email', 'order__id')
    readonly_fields = ('tx_ref', 'chapa_tx_ref', 'chapa_response', 'created_at', 'updated_at', 'paid_at')
    ordering = ('-created_at',)
