"""
License validation service to verify pharmacy registrations against MoH records
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import MoHPharmacyRecord, Pharmacy
import logging

logger = logging.getLogger(__name__)

class LicenseValidationService:
    """Service to validate pharmacy license numbers against MoH registry"""
    
    @staticmethod
    def validate_license(license_number, pharmacy_name=None, owner_name=None):
        """
        Validate if a license number exists in MoH records
        Returns validation result with details
        """
        try:
            # Check if license number exists in MoH registry
            moh_record = MoHPharmacyRecord.objects.filter(
                license_number=license_number
            ).first()
            
            if not moh_record:
                return {
                    'valid': False,
                    'status': 'not_found',
                    'message': f'License number {license_number} not found in Ministry of Health registry. Please verify your license number or contact MoH.',
                    'data': None
                }
            
            # Check if license is active and not expired
            if not moh_record.is_license_valid:
                return {
                    'valid': False,
                    'status': 'invalid_license',
                    'message': f'License {license_number} is {moh_record.status} or expired. Please renew your license with MoH.',
                    'data': moh_record
                }
            
            # Check if pharmacy name matches (fuzzy matching)
            name_match = True
            if pharmacy_name:
                name_match = LicenseValidationService._fuzzy_name_match(
                    pharmacy_name, moh_record.pharmacy_name
                )
            
            # Check if already registered on platform
            existing_pharmacy = Pharmacy.objects.filter(
                license_number=license_number
            ).first()
            
            if existing_pharmacy:
                return {
                    'valid': False,
                    'status': 'already_registered',
                    'message': f'License number {license_number} is already registered on this platform.',
                    'data': moh_record,
                    'existing_pharmacy': existing_pharmacy
                }
            
            return {
                'valid': True,
                'status': 'valid',
                'message': 'License number verified successfully with Ministry of Health.',
                'data': moh_record,
                'name_match': name_match,
                'warnings': [] if name_match else ['Pharmacy name does not exactly match MoH records']
            }
            
        except Exception as e:
            logger.error(f"License validation error for {license_number}: {str(e)}")
            return {
                'valid': False,
                'status': 'validation_error',
                'message': 'Unable to validate license at this time. Please try again later.',
                'data': None
            }
    
    @staticmethod
    def _fuzzy_name_match(name1, name2, threshold=0.8):
        """
        Perform fuzzy matching of pharmacy names
        Returns True if names are similar enough
        """
        if not name1 or not name2:
            return False
        
        # Simple fuzzy matching - normalize and compare
        name1_normalized = name1.lower().strip().replace(' ', '')
        name2_normalized = name2.lower().strip().replace(' ', '')
        
        # Exact match
        if name1_normalized == name2_normalized:
            return True
        
        # Check if one name contains the other
        if name1_normalized in name2_normalized or name2_normalized in name1_normalized:
            return True
        
        # Calculate similarity ratio (simplified version)
        shorter = min(len(name1_normalized), len(name2_normalized))
        longer = max(len(name1_normalized), len(name2_normalized))
        
        if shorter == 0:
            return False
            
        # Count matching characters at same positions
        matches = sum(1 for i in range(shorter) if name1_normalized[i] == name2_normalized[i])
        similarity = matches / longer
        
        return similarity >= threshold
    
    @staticmethod
    def get_moh_record_by_license(license_number):
        """Get MoH record by license number"""
        try:
            return MoHPharmacyRecord.objects.get(license_number=license_number)
        except MoHPharmacyRecord.DoesNotExist:
            return None
    
    @staticmethod
    def sync_pharmacy_with_moh(pharmacy, moh_record):
        """
        Sync pharmacy data with MoH record after validation
        Updates pharmacy with verified MoH data
        """
        if not moh_record:
            return False
        
        try:
            # Update pharmacy with MoH verified data
            pharmacy.moh_verification_data = {
                'moh_pharmacy_name': moh_record.pharmacy_name,
                'moh_owner_name': moh_record.owner_name,
                'moh_pharmacist_name': moh_record.pharmacist_name,
                'moh_pharmacist_license': moh_record.pharmacist_license,
                'moh_license_type': moh_record.license_type,
                'moh_issue_date': moh_record.issue_date.isoformat(),
                'moh_expiry_date': moh_record.expiry_date.isoformat(),
                'moh_region': moh_record.region,
                'moh_city': moh_record.city,
                'verification_date': timezone.now().isoformat()
            }
            pharmacy.moh_verification_status = 'verified'
            pharmacy.save()
            return True
            
        except Exception as e:
            logger.error(f"Error syncing pharmacy {pharmacy.id} with MoH record: {str(e)}")
            return False

def validate_pharmacy_license(license_number, pharmacy_name=None):
    """
    Convenience function to validate pharmacy license
    Raises ValidationError if license is invalid
    """
    validation_result = LicenseValidationService.validate_license(
        license_number, pharmacy_name
    )
    
    if not validation_result['valid']:
        raise ValidationError(validation_result['message'])
    
    return validation_result