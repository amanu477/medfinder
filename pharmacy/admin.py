from django.contrib import admin
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html
from .models import Pharmacy, Medicine

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_number', 'verification_status', 'phone', 'email', 'is_active', 'created_at', 'verification_actions')
    search_fields = ('name', 'license_number', 'phone', 'email')
    list_filter = ('verification_status', 'is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'verified_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'license_number', 'address', 'phone', 'email')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Operating Hours', {
            'fields': ('opening_time', 'closing_time', 'is_active')
        }),
        ('Verification', {
            'fields': ('verification_status', 'business_license', 'pharmacist_certificate', 'verification_documents', 'rejection_reason', 'verified_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def verification_actions(self, obj):
        if obj.verification_status == 'pending':
            approve_url = reverse('admin:approve_pharmacy', args=[obj.pk])
            reject_url = reverse('admin:reject_pharmacy', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}">Approve</a>&nbsp;'
                '<a class="button" href="{}">Reject</a>',
                approve_url, reject_url
            )
        elif obj.verification_status == 'verified':
            return format_html('<span style="color: green;">✓ Verified</span>')
        elif obj.verification_status == 'rejected':
            return format_html('<span style="color: red;">✗ Rejected</span>')
        return '-'
    verification_actions.short_description = 'Actions'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:pharmacy_id>/approve/', self.admin_site.admin_view(self.approve_pharmacy), name='approve_pharmacy'),
            path('<int:pharmacy_id>/reject/', self.admin_site.admin_view(self.reject_pharmacy), name='reject_pharmacy'),
        ]
        return custom_urls + urls
    
    def approve_pharmacy(self, request, pharmacy_id):
        from django.shortcuts import redirect, get_object_or_404
        from django.contrib import messages
        
        pharmacy = get_object_or_404(Pharmacy, pk=pharmacy_id)
        pharmacy.verification_status = 'verified'
        pharmacy.verified_at = timezone.now()
        pharmacy.rejection_reason = None
        pharmacy.save()
        
        messages.success(request, f'Pharmacy "{pharmacy.name}" has been approved and verified.')
        return redirect('admin:pharmacy_pharmacy_changelist')
    
    def reject_pharmacy(self, request, pharmacy_id):
        from django.shortcuts import redirect, get_object_or_404, render
        from django.contrib import messages
        
        pharmacy = get_object_or_404(Pharmacy, pk=pharmacy_id)
        
        if request.method == 'POST':
            rejection_reason = request.POST.get('rejection_reason', '')
            pharmacy.verification_status = 'rejected'
            pharmacy.rejection_reason = rejection_reason
            pharmacy.verified_at = None
            pharmacy.save()
            
            messages.success(request, f'Pharmacy "{pharmacy.name}" has been rejected.')
            return redirect('admin:pharmacy_pharmacy_changelist')
        
        return render(request, 'admin/pharmacy/reject_pharmacy.html', {
            'pharmacy': pharmacy,
            'title': f'Reject Pharmacy: {pharmacy.name}'
        })

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'pharmacy', 'price', 'stock_quantity', 'expiry_date', 'is_available', 'prescription_required')
    list_filter = ('is_available', 'prescription_required', 'pharmacy__verification_status', 'pharmacy')
    search_fields = ('name', 'description', 'pharmacy__name')
    date_hierarchy = 'expiry_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pharmacy')
