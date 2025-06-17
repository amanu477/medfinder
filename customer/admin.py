from django.contrib import admin
from .models import Customer, Prescription, Payment, Receipt

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

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'order', 'customer', 'pharmacy', 'generated_at', 'is_printed', 'print_count')
    list_filter = ('generated_at', 'is_printed', 'pharmacy')
    search_fields = ('receipt_number', 'customer__name', 'customer__email', 'pharmacy__name', 'order__id')
    readonly_fields = ('receipt_number', 'generated_at', 'last_viewed_by_customer', 'last_viewed_by_pharmacy')
    ordering = ('-generated_at',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('payment', 'order', 'customer', 'pharmacy')
        return self.readonly_fields
