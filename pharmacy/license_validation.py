"""
License validation service for two separate systems:
1. Independent MoH registry (for MoH registrations)
2. Platform pharmacy database (for normal registrations)
3. Admin verification matches license numbers between both systems
"""

from django.core.exceptions import ValidationError
from difflib import SequenceMatcher
from moh.models import MoHPharmacyRegistry
import logging

logger = logging.getLogger(__name__)


class LicenseValidationService:
    """Service to handle two separate pharmacy registration systems"""

    @staticmethod
    def check_moh_license_match(platform_pharmacy):
        """
        Check if a platform pharmacy has a matching license in the independent MoH registry
        Used by admin for verification process
        """
        try:
            moh_record = MoHPharmacyRegistry.objects.get(
                license_number=platform_pharmacy.license_number,
                license_status='active'
            )
            
            # If match found, link the records
            if moh_record and not moh_record.pharmacy:
                moh_record.pharmacy = platform_pharmacy
                moh_record.save()
            
            return {
                'match_found': True,
                'moh_record': moh_record,
                'license_status': moh_record.license_status,
                'compliance_score': moh_record.compliance_score,
                'verification_details': {
                    'license_number_match': True,
                    'pharmacy_name_similarity': LicenseValidationService._calculate_similarity(
                        platform_pharmacy.name, moh_record.pharmacy_name
                    ),
                    'owner_name_similarity': LicenseValidationService._calculate_similarity(
                        platform_pharmacy.owner_name, moh_record.owner_name
                    ),
                    'license_active': moh_record.license_status == 'active',
                    'license_valid': moh_record.is_license_valid
                },
                'approve_recommendation': moh_record.license_status == 'active' and moh_record.is_license_valid
            }
            
        except MoHPharmacyRegistry.DoesNotExist:
            return {
                'match_found': False,
                'moh_record': None,
                'license_status': 'not_found_in_moh',
                'compliance_score': 0,
                'verification_details': {
                    'license_number_match': False,
                    'pharmacy_name_similarity': 0,
                    'owner_name_similarity': 0,
                    'license_active': False,
                    'license_valid': False
                },
                'approve_recommendation': False,
                'error': f'License number {platform_pharmacy.license_number} not found in MoH registry'
            }
    
    @staticmethod
    def validate_moh_registration(license_number):
        """
        Validate MoH registration (separate from platform)
        Ensures license number is unique in MoH system
        """
        if MoHPharmacyRegistry.objects.filter(license_number=license_number).exists():
            raise ValidationError(f"License number {license_number} already exists in MoH registry")
        return True
    
    @staticmethod
    def validate_platform_registration(license_number):
        """
        Validate platform registration (separate from MoH)
        No MoH check required during registration
        """
        from pharmacy.models import Pharmacy
        if Pharmacy.objects.filter(license_number=license_number).exists():
            raise ValidationError(f"License number {license_number} already exists in platform")
        return True
    
    @staticmethod
    def _calculate_similarity(name1, name2):
        """Calculate similarity between two names"""
        if not name1 or not name2:
            return 0
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
    
    @staticmethod 
    def _fuzzy_name_match(name1, name2, threshold=0.8):
        """Check if names are similar enough"""
        return LicenseValidationService._calculate_similarity(name1, name2) >= threshold
    
    @staticmethod
    def get_moh_record_by_license(license_number):
        """Get MoH record by license number"""
        try:
            return MoHPharmacyRegistry.objects.get(license_number=license_number)
        except MoHPharmacyRegistry.DoesNotExist:
            return None
    
    @staticmethod
    def get_unmatched_moh_records():
        """Get MoH records that haven't been matched to platform pharmacies"""
        return MoHPharmacyRegistry.objects.filter(pharmacy__isnull=True)
    
    @staticmethod
    def get_matched_moh_records():
        """Get MoH records that have been matched to platform pharmacies"""
        return MoHPharmacyRegistry.objects.filter(pharmacy__isnull=False)


def validate_pharmacy_license_for_platform(license_number):
    """
    Validate license for platform registration (no MoH check required)
    """
    return LicenseValidationService.validate_platform_registration(license_number)


def validate_pharmacy_license_for_moh(license_number):
    """
    Validate license for MoH registration (separate system)
    """
    return LicenseValidationService.validate_moh_registration(license_number)