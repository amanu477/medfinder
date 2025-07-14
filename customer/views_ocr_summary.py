"""
OCR Validation Summary Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Customer, Cart, CartItem

@login_required
def ocr_validation_summary(request):
    """Display comprehensive OCR validation summary"""
    try:
        customer = request.user.customer
        cart = get_object_or_404(Cart, customer=customer)
        cart_items = cart.cartitem_set.all().select_related('medicine', 'medicine__pharmacy')
        
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('cart_view')
        
        # Calculate overall statistics
        total_count = cart_items.count()
        validated_count = 0
        failed_count = 0
        
        # Group by pharmacy for detailed analysis
        pharmacy_results = {}
        
        for item in cart_items:
            pharmacy = item.medicine.pharmacy
            if pharmacy not in pharmacy_results:
                pharmacy_results[pharmacy] = {
                    'validated_medicines': [],
                    'failed_medicines': [],
                    'total_medicines': 0,
                    'validation_rate': 0
                }
            
            pharmacy_results[pharmacy]['total_medicines'] += 1
            
            if item.validation_data:
                medicine_data = {
                    'name': item.medicine.name,
                    'confidence': item.validation_data.get('confidence', 0)
                }
                
                if item.validation_data.get('is_valid', False):
                    pharmacy_results[pharmacy]['validated_medicines'].append(medicine_data)
                    validated_count += 1
                else:
                    pharmacy_results[pharmacy]['failed_medicines'].append(medicine_data)
                    failed_count += 1
            else:
                # No OCR data means not validated
                pharmacy_results[pharmacy]['failed_medicines'].append({
                    'name': item.medicine.name,
                    'confidence': 0
                })
                failed_count += 1
        
        # Calculate validation rates for each pharmacy
        for pharmacy, result in pharmacy_results.items():
            validated_for_pharmacy = len(result['validated_medicines'])
            total_for_pharmacy = result['total_medicines']
            result['validation_rate'] = (validated_for_pharmacy / total_for_pharmacy) * 100 if total_for_pharmacy > 0 else 0
        
        # Calculate overall validation percentage
        validation_percentage = (validated_count / total_count) * 100 if total_count > 0 else 0
        
        context = {
            'total_count': total_count,
            'validated_count': validated_count,
            'failed_count': failed_count,
            'validation_percentage': round(validation_percentage, 1),
            'pharmacy_results': pharmacy_results,
            'cart_items': cart_items,
        }
        
        return render(request, 'customer/ocr_validation_summary.html', context)
        
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('cart_view')