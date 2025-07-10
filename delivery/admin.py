from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import DeliveryPerson, Delivery, DeliveryTracking, DeliveryNotification, DeliveryZone


@admin.register(DeliveryPerson)
class DeliveryPersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'pharmacy', 'employee_id', 'phone', 'vehicle_type', 'is_active', 'is_available', 'rating', 'total_deliveries')
    list_filter = ('pharmacy', 'vehicle_type', 'is_active', 'is_available')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'employee_id', 'phone', 'national_id')
    readonly_fields = ('created_at', 'updated_at', 'last_location_update')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'pharmacy', 'employee_id', 'phone', 'national_id')
        }),
        ('Vehicle Information', {
            'fields': ('vehicle_type', 'vehicle_plate')
        }),
        ('Status', {
            'fields': ('is_active', 'is_available', 'rating', 'total_deliveries')
        }),
        ('Location', {
            'fields': ('current_location_lat', 'current_location_lon', 'last_location_update')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class DeliveryTrackingInline(admin.TabularInline):
    model = DeliveryTracking
    extra = 0
    readonly_fields = ('timestamp',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'order', 'delivery_person', 'status', 'customer_phone', 'created_at', 'delivery_time')
    list_filter = ('status', 'created_at', 'delivery_time')
    search_fields = ('tracking_number', 'order__customer__name', 'customer_phone', 'delivery_person__user__username')
    readonly_fields = ('tracking_number', 'created_at', 'updated_at')
    inlines = [DeliveryTrackingInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'tracking_number', 'status', 'delivery_person')
        }),
        ('Customer Details', {
            'fields': ('customer_location_lat', 'customer_location_lon', 'customer_address', 'customer_phone')
        }),
        ('Delivery Details', {
            'fields': ('pickup_time', 'delivery_time', 'estimated_delivery_time', 'distance_km', 'delivery_fee')
        }),
        ('Notes and Feedback', {
            'fields': ('pharmacy_notes', 'delivery_notes', 'customer_feedback', 'customer_rating')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'delivery_person', 'order__customer')


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'status', 'timestamp', 'latitude', 'longitude')
    list_filter = ('status', 'timestamp')
    search_fields = ('delivery__tracking_number', 'status')
    readonly_fields = ('timestamp',)


@admin.register(DeliveryNotification)
class DeliveryNotificationAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'recipient_type', 'notification_type', 'is_read', 'created_at')
    list_filter = ('recipient_type', 'notification_type', 'is_read', 'created_at')
    search_fields = ('delivery__tracking_number', 'message')
    readonly_fields = ('created_at',)


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'pharmacy', 'delivery_fee', 'estimated_delivery_time', 'is_active')
    list_filter = ('pharmacy', 'is_active')
    search_fields = ('name', 'pharmacy__name')
    readonly_fields = ('created_at',)