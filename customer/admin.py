from django.contrib import admin
from .models import Customer, Prescription, Payment, Receipt, Cart, CartItem, Order, OrderItem

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

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('added_at',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'get_total_items', 'get_total_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer__name', 'customer__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'medicine', 'quantity', 'get_total_price', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('cart__customer__name', 'medicine__name')
    readonly_fields = ('added_at',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'pharmacy', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at', 'pharmacy')
    search_fields = ('customer__name', 'customer__email', 'pharmacy__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'medicine', 'quantity', 'price', 'get_total_price')
    list_filter = ('order__created_at',)
    search_fields = ('order__customer__name', 'medicine__name')
