"""
Ministry of Health Verification Service
Verifies pharmacies against official government database
"""
import random
from typing import Dict, Any, Optional
from django.utils import timezone
from datetime import datetime, timedelta, date
from moh.models import MoHPharmacyRegistry

class MinistryOfHealthVerificationService:
    """
    Verifies pharmacies against Ministry of Health database
    Checks real MoH records that were pre-registered by government officials
    """
    
    def verify_pharmacy(self, pharmacy_name: str, license_number: str, owner_name: str = None) -> Dict[str, Any]:
        """
        Verify pharmacy against MoH database
        
        Args:
            pharmacy_name: Name of the pharmacy to verify
            license_number: License number to check
            owner_name: Optional owner name for additional verification
            
        Returns:
            Dict containing verification results
        """
        verification_id = f"MOH-{random.randint(100000, 999999)}-{timezone.now().strftime('%Y%m%d')}"
        
        # Check if pharmacy exists in MoH database
        try:
            moh_record = MoHPharmacyRegistry.objects.get(license_number=license_number)
            
            # Verify pharmacy details
            license_verification = self._verify_license(moh_record, pharmacy_name, owner_name)
            certificate_verification = self._verify_pharmacist_certificate(moh_record)
            risk_assessment = self._assess_risk(moh_record, license_verification, certificate_verification)
            
            return {
                'verification_timestamp': timezone.now().isoformat(),
                'verification_id': verification_id,
                'license_verification': license_verification,
                'certificate_verification': certificate_verification,
                'risk_assessment': risk_assessment,
                'moh_record_found': True,
                'moh_record_id': moh_record.id
            }
            
        except MoHPharmacyRegistry.DoesNotExist:
            # Pharmacy not found in MoH database - this is a red flag
            return {
                'verification_timestamp': timezone.now().isoformat(),
                'verification_id': verification_id,
                'license_verification': {
                    'is_valid': False,
                    'verification_id': verification_id,
                    'details': None,
                    'warnings': ['Pharmacy license not found in Ministry of Health database', 
                               'This pharmacy may not be legally authorized to operate']
                },
                'certificate_verification': {
                    'is_valid': False,
                    'verification_id': verification_id,
                    'warnings': ['Cannot verify pharmacist certificate - pharmacy not in MoH database']
                },
                'risk_assessment': {
                    'risk_level': 'CRITICAL',
                    'risk_score': 100,
                    'recommendation': 'REJECT',
                    'risk_factors': [
                        'Pharmacy not registered in Ministry of Health database',
                        'Cannot verify legitimacy of operations',
                        'High risk of unlicensed pharmacy operations'
                    ]
                },
                'moh_record_found': False,
                'moh_record_id': None
            }
    
    def _verify_license(self, moh_record: MoHPharmacyRegistry, pharmacy_name: str, owner_name: str = None) -> Dict[str, Any]:
        """Verify license details against MoH record"""
        verification_id = f"LIC-{random.randint(100000, 999999)}"
        warnings = []
        
        # Check license validity
        is_valid = moh_record.is_license_valid
        if not is_valid:
            if moh_record.license_status != 'active':
                warnings.append(f"License status is '{moh_record.get_license_status_display()}' - not active")
            if moh_record.expiry_date < date.today():
                warnings.append(f"License expired on {moh_record.expiry_date}")
        
        # Check name matching (fuzzy matching for common variations)
        name_similarity = self._calculate_name_similarity(pharmacy_name.lower(), str(moh_record.pharmacy_name).lower())
        if name_similarity < 0.8:
            warnings.append(f"Pharmacy name mismatch: Registered as '{moh_record.pharmacy_name}', applying as '{pharmacy_name}'")
        
        # Check owner name if provided
        if owner_name and moh_record.owner_name:
            owner_similarity = self._calculate_name_similarity(owner_name.lower(), str(moh_record.owner_name).lower())
            if owner_similarity < 0.8:
                warnings.append(f"Owner name mismatch: Registered owner '{moh_record.owner_name}', provided '{owner_name}'")
        
        return {
            'is_valid': is_valid and name_similarity >= 0.6,  # Allow some flexibility in names
            'verification_id': verification_id,
            'details': {
                'registered_name': moh_record.pharmacy_name,
                'owner': moh_record.owner_name,
                'license_type': moh_record.get_license_type_display(),
                'location': f"{moh_record.city}, {moh_record.woreda}, {moh_record.get_region_display()}",
                'issue_date': moh_record.issue_date.strftime('%Y-%m-%d') if moh_record.issue_date else None,
                'expiry_date': moh_record.expiry_date.strftime('%Y-%m-%d') if moh_record.expiry_date else None,
                'status': moh_record.get_license_status_display(),
                'pharmacist': moh_record.pharmacist_name,
                'pharmacist_license': moh_record.pharmacist_license
            },
            'warnings': warnings
        }
    
    def _verify_pharmacist_certificate(self, moh_record: MoHPharmacyRegistry) -> Dict[str, Any]:
        """Verify pharmacist certificate"""
        verification_id = f"CERT-{random.randint(100000, 999999)}"
        warnings = []
        
        # Check if pharmacist license is valid format
        pharmacist_license = getattr(moh_record, 'pharmacist_license', None)
        is_valid = bool(pharmacist_license and len(pharmacist_license) >= 6)
        
        if not is_valid:
            warnings.append("Invalid or missing pharmacist license number")
        
        # Additional checks could be added here for pharmacist license verification
        # In a real system, this would check against pharmacist licensing board
        
        return {
            'is_valid': is_valid,
            'verification_id': verification_id,
            'warnings': warnings
        }
    
    def _assess_risk(self, moh_record: MoHPharmacyRegistry, license_verification: Dict, certificate_verification: Dict) -> Dict[str, Any]:
        """Assess risk level and provide recommendation"""
        risk_score = 0
        risk_factors = []
        
        # License validity (40 points)
        if not license_verification['is_valid']:
            risk_score += 40
            risk_factors.append("Invalid or expired pharmacy license")
        
        # Certificate validity (20 points)
        if not certificate_verification['is_valid']:
            risk_score += 20
            risk_factors.append("Invalid pharmacist certification")
        
        # License expiry warning (10 points)
        if moh_record.days_until_expiry is not None and moh_record.days_until_expiry < 90:
            risk_score += 10
            risk_factors.append(f"License expires in {moh_record.days_until_expiry} days")
        
        # Status checks (15 points)
        if moh_record.license_status == 'suspended':
            risk_score += 15
            risk_factors.append("Pharmacy is currently suspended by MoH")
        elif moh_record.license_status == 'revoked':
            risk_score += 40
            risk_factors.append("Pharmacy license has been revoked")
        
        # Name mismatches from warnings (10 points)
        if any('mismatch' in warning.lower() for warning in license_verification.get('warnings', [])):
            risk_score += 10
            risk_factors.append("Name inconsistencies detected")
        
        # Last inspection date (5 points)
        last_inspection = getattr(moh_record, 'inspection_date', None)
        if last_inspection:
            days_since_inspection = (date.today() - last_inspection).days
            if days_since_inspection > 365:
                risk_score += 5
                risk_factors.append(f"Last inspection was {days_since_inspection} days ago")
        
        # Determine risk level and recommendation
        if risk_score >= 60:
            risk_level = 'CRITICAL'
            recommendation = 'REJECT'
        elif risk_score >= 40:
            risk_level = 'HIGH'
            recommendation = 'MANUAL_REVIEW'
        elif risk_score >= 20:
            risk_level = 'MEDIUM'
            recommendation = 'CONDITIONAL_APPROVE'
        else:
            risk_level = 'LOW'
            recommendation = 'APPROVE'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'recommendation': recommendation,
            'risk_factors': risk_factors
        }
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names using Levenshtein distance"""
        if not name1 or not name2:
            return 0.0
        
        # Simple similarity check - could be enhanced with fuzzy matching library
        if name1 == name2:
            return 1.0
        
        # Remove common words and compare
        common_words = ['pharmacy', 'drug', 'store', 'clinic', 'medical', 'health']
        clean_name1 = ' '.join([word for word in name1.split() if word not in common_words])
        clean_name2 = ' '.join([word for word in name2.split() if word not in common_words])
        
        if clean_name1 == clean_name2:
            return 0.9
        
        # Basic character overlap check
        overlap = len(set(clean_name1) & set(clean_name2))
        total = len(set(clean_name1) | set(clean_name2))
        
        return overlap / total if total > 0 else 0.0