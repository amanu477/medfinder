"""
License validation service to verify pharmacy registrations against independent MoH records
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from moh.models import MoHPharmacyRegistry
import logging

logger = logging.getLogger(__name__)

class LicenseValidationService:
    """Service to validate pharmacy license numbers against independent MoH registry"""

    @staticmethod
    def validate_license(license_number, pharmacy_name=None, owner_name=None):
        """
        Validate if a license number exists in independent MoH records
        Returns validation result with details
        """
        if not license_number:
            return {
                'valid': False,
                'status': 'missing_license',
                'message': 'License number is required for validation.',
                'data': None
            }
        
        try:
            # Check if MoH record exists in the independent MoH database
            moh_record = MoHPharmacyRegistry.objects.get(license_number=license_number)
            
            # Check license status
            if moh_record.license_status not in ['active', 'pending']:
                return {
                    'valid': False,
                    'status': 'invalid_license',
                    'message': f'License {license_number} is {moh_record.license_status} or expired. Please renew your license with MoH.',
                    'data': moh_record
                }
            
            # Check if pharmacy name matches (fuzzy matching)
            name_match = True
            if pharmacy_name:
                name_match = LicenseValidationService._fuzzy_name_match(
                    pharmacy_name, moh_record.pharmacy_name
                )
            
            # Create warnings list
            warnings = []
            if not name_match:
                warnings.append(f"Pharmacy name '{pharmacy_name}' does not match MoH record '{moh_record.pharmacy_name}'")
            
            if moh_record.compliance_score < 70:
                warnings.append(f"Low compliance score: {moh_record.compliance_score}/100")
            
            return {
                'valid': True,
                'status': 'valid',
                'message': 'License number verified successfully with Ministry of Health.',
                'data': moh_record,
                'name_match': name_match,
                'warnings': warnings if warnings else None
            }
            
        except MoHPharmacyRecord.DoesNotExist:
            return {
                'valid': False,
                'status': 'not_found',
                'message': f'License number {license_number} not found in Ministry of Health records.',
                'data': None
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
        
        # Simple fuzzy matching - can be enhanced with more sophisticated algorithms
        name1_clean = name1.lower().strip()
        name2_clean = name2.lower().strip()
        
        # Exact match
        if name1_clean == name2_clean:
            return True
        
        # Check if one name contains the other
        if name1_clean in name2_clean or name2_clean in name1_clean:
            return True
        
        # Basic similarity check (can be enhanced)
        common_words = set(name1_clean.split()) & set(name2_clean.split())
        total_words = set(name1_clean.split()) | set(name2_clean.split())
        
        if len(total_words) > 0:
            similarity = len(common_words) / len(total_words)
            return similarity >= threshold
        
        return False

    @staticmethod
    def get_moh_record_by_license(license_number):
        """Get MoH record by license number"""
        try:
            return MoHPharmacyRecord.objects.get(license_number=license_number)
        except MoHPharmacyRecord.DoesNotExist:
            return None

def validate_pharmacy_license(license_number, pharmacy_name=None):
    """
    Convenience function to validate pharmacy license
    Raises ValidationError if license is invalid
    """
    result = LicenseValidationService.validate_license(license_number, pharmacy_name)
    
    if not result['valid']:
        raise ValidationError(result['message'])
    
    return result