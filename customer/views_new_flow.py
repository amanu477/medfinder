from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from .models import Customer, Order, OrderItem
from .ocr_service import PrescriptionOCRService
from .chapa_service import ChapaService
from pharmacy.models import Medicine
from .forms import OrderForm
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

@login_required
def prescription_validation_view(request, medicine_id):
    """
    New view: Upload prescription and validate medicine name with OCR
    This comes after medicine search but before order placement
    """
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    if request.method == 'POST':
        prescription_image = request.FILES.get('prescription_image')
        quantity = int(request.POST.get('quantity', 1))
        
        if not prescription_image:
            messages.error(request, 'Please upload a prescription image.')
            return render(request, 'customer/prescription_validation.html', {
                'medicine': medicine,
                'step': 1  # Step 1: Upload prescription
            })
        
        # Process OCR validation
        try:
            # Save uploaded image temporarily for OCR processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                for chunk in prescription_image.chunks():
                    temp_file.write(chunk)
                temp_image_path = temp_file.name
            
            # Initialize OCR service
            ocr_service = PrescriptionOCRService()
            
            # Validate medicine name against prescription
            ocr_result = ocr_service.validate_medicine_name(
                medicine.name, 
                temp_image_path, 
                threshold=60
            )
            
            # Clean up temporary file
            os.unlink(temp_image_path)
            
            # Store results in session for order placement
            request.session['prescription_validation'] = {
                'medicine_id': medicine_id,
                'quantity': quantity,
                'ocr_result': ocr_result,
                'prescription_uploaded': True
            }
            
            # Store the actual prescription image in session (base64 encoded)
            prescription_image.seek(0)  # Reset file pointer
            import base64
            prescription_data = base64.b64encode(prescription_image.read()).decode('utf-8')
            request.session['prescription_image_data'] = prescription_data
            request.session['prescription_image_name'] = prescription_image.name
            
            context = {
                'medicine': medicine,
                'quantity': quantity,
                'ocr_result': ocr_result,
                'step': 2  # Step 2: Show OCR results
            }
            
            return render(request, 'customer/prescription_validation.html', context)
            
        except Exception as e:
            logger.error(f"OCR validation error: {str(e)}")
            messages.error(request, f'Error processing prescription: {str(e)}')
            return render(request, 'customer/prescription_validation.html', {
                'medicine': medicine,
                'step': 1
            })
    
    # GET request - show prescription upload form
    return render(request, 'customer/prescription_validation.html', {
        'medicine': medicine,
        'step': 1
    })

@login_required
def confirm_order_with_prescription(request, medicine_id):
    """
    New view: Confirm order after prescription validation
    """
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('home')
    
    # Check if prescription validation was completed
    validation_data = request.session.get('prescription_validation')
    if not validation_data or validation_data.get('medicine_id') != medicine_id:
        messages.error(request, 'Please complete prescription validation first.')
        return redirect('prescription_validation', medicine_id=medicine_id)
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    quantity = validation_data.get('quantity', 1)
    ocr_result = validation_data.get('ocr_result')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirm_order':
            # User confirmed they want to proceed with the order
            return create_order_with_prescription(request, medicine, quantity, ocr_result)
        elif action == 'retry_prescription':
            # User wants to upload a different prescription
            # Clear session data
            if 'prescription_validation' in request.session:
                del request.session['prescription_validation']
            if 'prescription_image_data' in request.session:
                del request.session['prescription_image_data']
            if 'prescription_image_name' in request.session:
                del request.session['prescription_image_name']
            
            return redirect('prescription_validation', medicine_id=medicine_id)
    
    # Show order confirmation with OCR results
    context = {
        'medicine': medicine,
        'quantity': quantity,
        'ocr_result': ocr_result,
        'total_price': medicine.price * quantity,
        'step': 3  # Step 3: Order confirmation
    }
    
    return render(request, 'customer/prescription_validation.html', context)

def create_order_with_prescription(request, medicine, quantity, ocr_result):
    """
    Create order with prescription and OCR validation data
    """
    try:
        customer = request.user.customer
        
        # Check stock availability
        if quantity > medicine.stock_quantity:
            messages.error(request, f'Only {medicine.stock_quantity} units available in stock.')
            return redirect('prescription_validation', medicine_id=medicine.id)
        
        # Create order
        with transaction.atomic():
            order = Order.objects.create(
                customer=customer,
                pharmacy=medicine.pharmacy,
                total_amount=medicine.price * quantity,
                status='pending',
                notes=f'OCR Validation - Confidence: {ocr_result.get("confidence", 0):.1f}%'
            )
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                medicine=medicine,
                quantity=quantity,
                price=medicine.price
            )
            
            # Save prescription image if available
            prescription_image_data = request.session.get('prescription_image_data')
            prescription_image_name = request.session.get('prescription_image_name')
            
            if prescription_image_data and prescription_image_name:
                import base64
                from django.core.files.base import ContentFile
                
                # Decode base64 image data
                image_data = base64.b64decode(prescription_image_data)
                image_file = ContentFile(image_data, name=prescription_image_name)
                
                # Save to order
                order.prescription_image = image_file
                order.save()
            
            # Update stock
            medicine.stock_quantity -= quantity
            medicine.save()
            
            # Clear session data
            if 'prescription_validation' in request.session:
                del request.session['prescription_validation']
            if 'prescription_image_data' in request.session:
                del request.session['prescription_image_data']
            if 'prescription_image_name' in request.session:
                del request.session['prescription_image_name']
            
            messages.success(request, f'Order #{order.id} placed successfully!')
            return redirect('order_detail', order_id=order.id)
            
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        messages.error(request, f'Error creating order: {str(e)}')
        return redirect('prescription_validation', medicine_id=medicine.id)