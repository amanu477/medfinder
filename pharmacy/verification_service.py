"""
Ministry of Health Verification Service
Simulates verification against official government database
"""
import random
from typing import Dict, Any, Optional
from django.utils import timezone
from datetime import datetime, timedelta

class MinistryOfHealthVerificationService:
    """
    Simulates verification against Ministry of Health database
    In production, this would connect to actual government APIs
    """
    
    # Simulated legitimate pharmacy data (would be from real MoH database)
    LEGITIMATE_PHARMACIES = {
        'PH001234': {
            'name': 'Central Pharmacy',
            'owner': 'Dr. Abebe Bekele',
            'license_type': 'Full Service Pharmacy',
            'issue_date': '2020-03-15',
            'expiry_date': '2025-03-15',
            'status': 'active',
            'location': 'Addis Ababa',
            'specializations': ['General Medicines', 'Prescription Drugs']
        },
        'PH005678': {
            'name': 'Health Plus Pharmacy',
            'owner': 'Dr. Meron Tadesse',
            'license_type': 'Community Pharmacy',
            'issue_date': '2019-07-22',
            'expiry_date': '2024-07-22',
            'status': 'active',
            'location': 'Bahir Dar',
            'specializations': ['General Medicines', 'Medical Supplies']
        },
        'PH009876': {
            'name': 'Care Pharmacy',
            'owner': 'Dr. Solomon Worku',
            'license_type': 'Hospital Pharmacy',
            'issue_date': '2021-01-10',
            'expiry_date': '2026-01-10',
            'status': 'active',
            'location': 'Hawassa',
            'specializations': ['Hospital Medicines', 'Prescription Drugs', 'Emergency Medicines']
        },
        'PH012345': {
            'name': 'MedCare Pharmacy',
            'owner': 'Dr. Hanna Gebremedhin',
            'license_type': 'Full Service Pharmacy',
            'issue_date': '2018-11-05',
            'expiry_date': '2023-11-05',
            'status': 'expired',
            'location': 'Mekelle',
            'specializations': ['General Medicines']
        }
    }
    
    # Valid pharmacist certificate patterns
    VALID_CERTIFICATE_PATTERNS = [
        'CERT-PH-2020-',
        'CERT-PH-2021-',
        'CERT-PH-2022-',
        'CERT-PH-2023-',
        'CERT-PH-2024-'
    ]
    
    @classmethod
    def verify_pharmacy_license(cls, license_number: str, pharmacy_name: str) -> Dict[str, Any]:
        """
        Verify pharmacy license against Ministry of Health database
        """
        verification_result = {
            'license_number': license_number,
            'is_valid': False,
            'status': 'not_found',
            'details': {},
            'verification_date': timezone.now().isoformat(),
            'verification_id': f"VER-{random.randint(100000, 999999)}"
        }
        
        # Check if license exists in database
        if license_number in cls.LEGITIMATE_PHARMACIES:
            pharmacy_data = cls.LEGITIMATE_PHARMACIES[license_number]
            
            # Check if names match (allow for slight variations)
            name_match = cls._check_name_similarity(pharmacy_name.lower(), pharmacy_data['name'].lower())
            
            if name_match:
                verification_result.update({
                    'is_valid': True,
                    'status': pharmacy_data['status'],
                    'details': {
                        'registered_name': pharmacy_data['name'],
                        'owner': pharmacy_data['owner'],
                        'license_type': pharmacy_data['license_type'],
                        'issue_date': pharmacy_data['issue_date'],
                        'expiry_date': pharmacy_data['expiry_date'],
                        'location': pharmacy_data['location'],
                        'specializations': pharmacy_data['specializations']
                    }
                })
                
                # Check if license is expired
                expiry_date = datetime.strptime(pharmacy_data['expiry_date'], '%Y-%m-%d').date()
                if expiry_date < timezone.now().date():
                    verification_result['status'] = 'expired'
                    verification_result['warnings'] = ['License has expired']
                
            else:
                verification_result.update({
                    'status': 'name_mismatch',
                    'details': {
                        'registered_name': pharmacy_data['name'],
                        'submitted_name': pharmacy_name
                    },
                    'warnings': ['Pharmacy name does not match registered name']
                })
        else:
            # Simulate checking if license number format is valid
            if cls._is_valid_license_format(license_number):
                verification_result['status'] = 'not_found'
                verification_result['warnings'] = ['License number not found in Ministry database']
            else:
                verification_result['status'] = 'invalid_format'
                verification_result['warnings'] = ['Invalid license number format']
        
        return verification_result
    
    @classmethod
    def verify_pharmacist_certificate(cls, certificate_data: str) -> Dict[str, Any]:
        """
        Verify pharmacist certificate
        """
        verification_result = {
            'is_valid': False,
            'status': 'invalid',
            'verification_date': timezone.now().isoformat(),
            'verification_id': f"CERT-VER-{random.randint(100000, 999999)}"
        }
        
        # Check certificate format
        is_valid_format = any(certificate_data.startswith(pattern) for pattern in cls.VALID_CERTIFICATE_PATTERNS)
        
        if is_valid_format:
            # Simulate additional checks
            certificate_year = certificate_data.split('-')[2]
            current_year = timezone.now().year
            
            if int(certificate_year) <= current_year:
                verification_result.update({
                    'is_valid': True,
                    'status': 'valid',
                    'details': {
                        'certificate_year': certificate_year,
                        'valid_until': f"{int(certificate_year) + 5}-12-31"
                    }
                })
            else:
                verification_result.update({
                    'status': 'future_date',
                    'warnings': ['Certificate date is in the future']
                })
        else:
            verification_result.update({
                'status': 'invalid_format',
                'warnings': ['Invalid certificate format']
            })
        
        return verification_result
    
    @classmethod
    def get_risk_assessment(cls, pharmacy_data: dict) -> Dict[str, Any]:
        """
        Assess risk level based on verification results
        """
        risk_factors = []
        risk_score = 0
        
        # Check license verification
        license_verification = pharmacy_data.get('license_verification', {})
        if not license_verification.get('is_valid'):
            risk_factors.append('Invalid or unverified license')
            risk_score += 30
        elif license_verification.get('status') == 'expired':
            risk_factors.append('Expired license')
            risk_score += 25
        elif license_verification.get('status') == 'name_mismatch':
            risk_factors.append('Name mismatch with registered records')
            risk_score += 20
        
        # Check certificate verification
        cert_verification = pharmacy_data.get('certificate_verification', {})
        if not cert_verification.get('is_valid'):
            risk_factors.append('Invalid pharmacist certificate')
            risk_score += 25
        
        # Additional risk factors
        if not pharmacy_data.get('business_license'):
            risk_factors.append('Missing business license document')
            risk_score += 15
        
        if not pharmacy_data.get('address_verified'):
            risk_factors.append('Address not verified')
            risk_score += 10
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = 'HIGH'
            recommendation = 'REJECT'
        elif risk_score >= 25:
            risk_level = 'MEDIUM'
            recommendation = 'MANUAL_REVIEW'
        else:
            risk_level = 'LOW'
            recommendation = 'APPROVE'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendation': recommendation,
            'assessment_date': timezone.now().isoformat()
        }
    
    @classmethod
    def _check_name_similarity(cls, name1: str, name2: str) -> bool:
        """
        Check if two pharmacy names are similar enough
        """
        # Simple similarity check - in production would use more sophisticated methods
        name1_words = set(name1.replace('pharmacy', '').replace('ph', '').split())
        name2_words = set(name2.replace('pharmacy', '').replace('ph', '').split())
        
        if not name1_words or not name2_words:
            return False
        
        common_words = name1_words.intersection(name2_words)
        similarity_ratio = len(common_words) / max(len(name1_words), len(name2_words))
        
        return similarity_ratio >= 0.6  # 60% similarity threshold
    
    @classmethod
    def _is_valid_license_format(cls, license_number: str) -> bool:
        """
        Check if license number follows valid format
        """
        # Ethiopian pharmacy license format: PH + 6 digits
        return (
            len(license_number) == 8 and
            license_number.startswith('PH') and
            license_number[2:].isdigit()
        )