"""
OCR Service for Prescription Medicine Validation
Extracts text from prescription images and validates medicine names
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
from fuzzywuzzy import fuzz, process
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

class PrescriptionOCRService:
    """Service for extracting and validating medicine names from prescription images"""
    
    def __init__(self):
        # Common medicine name patterns and variations
        self.medicine_keywords = [
            'tablet', 'capsule', 'syrup', 'injection', 'drops', 'cream', 'ointment',
            'mg', 'ml', 'gm', 'mcg', 'units', 'twice', 'once', 'daily', 'bid', 'tid', 'qid'
        ]
        
        # Common Ethiopian medicine names for better matching
        self.common_ethiopian_medicines = [
            'paracetamol', 'aspirin', 'ibuprofen', 'amoxicillin', 'ciprofloxacin',
            'metronidazole', 'chloramphenicol', 'tetracycline', 'erythromycin',
            'cotrimoxazole', 'doxycycline', 'fluconazole', 'nystatin', 'albendazole',
            'mebendazole', 'iron', 'folic acid', 'vitamin', 'omeprazole', 'ranitidine',
            'diclofenac', 'prednisolone', 'hydrocortisone', 'salbutamol', 'theophylline'
        ]
    
    def preprocess_image(self, image_path):
        """
        Preprocess the image for better OCR accuracy using PIL
        """
        try:
            # Open image using PIL
            img = Image.open(image_path)
            
            # Convert to grayscale
            img = img.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            # Apply filter to reduce noise
            img = img.filter(ImageFilter.MedianFilter(size=3))
            
            return img
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            return None
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from prescription image using OCR
        """
        try:
            # Preprocess the image
            processed_img = self.preprocess_image(image_path)
            if processed_img is None:
                # Try with original image if preprocessing fails
                processed_img = Image.open(image_path)
            
            # Configure Tesseract for better accuracy
            custom_config = r'--oem 3 --psm 6'
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(processed_img, config=custom_config)
            
            # Clean up the extracted text
            text = self.clean_extracted_text(text)
            
            logger.info(f"Extracted text from {image_path}: {text[:200]}...")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from image {image_path}: {str(e)}")
            return ""
    
    def clean_extracted_text(self, text):
        """
        Clean and normalize extracted text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\.,\-\(\)\/:]', '', text)
        
        return text
    
    def extract_medicine_names(self, text):
        """
        Extract potential medicine names from the OCR text
        """
        if not text:
            return []
        
        # Split text into lines and words
        lines = text.split('\n')
        potential_medicines = []
        
        # Common medicine keywords that might appear around medicine names
        medicine_indicators = ['tablet', 'capsule', 'syrup', 'injection', 'drops', 'cream', 'ointment', 'mg', 'ml', 'gm']
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Convert to lowercase for pattern matching
            line_lower = line.lower()
            
            # Look for lines that contain medicine indicators
            has_medicine_indicators = any(indicator in line_lower for indicator in medicine_indicators)
            
            if has_medicine_indicators:
                # Extract words from this line
                words = line.split()
                
                for i, word in enumerate(words):
                    word_clean = re.sub(r'[^\w]', '', word)  # Remove punctuation
                    word_lower = word_clean.lower()
                    
                    # Skip common non-medicine words
                    skip_words = ['take', 'tablet', 'times', 'daily', 'after', 'before', 'food', 'mg', 'ml', 'gm', 'mcg', 'capsule', 'syrup', 'the', 'and', 'or', 'with', 'without']
                    if word_lower in skip_words:
                        continue
                    
                    # Look for words that might be medicine names
                    if len(word_clean) >= 4:  # Minimum length for medicine names
                        # Check if it contains letters (medicine names usually do)
                        if re.search(r'[a-zA-Z]', word_clean):
                            # Remove numbers and dosage info for better matching
                            clean_name = re.sub(r'\d+', '', word_clean).strip()
                            clean_name = re.sub(r'mg|ml|gm|mcg', '', clean_name, flags=re.IGNORECASE).strip()
                            
                            if len(clean_name) >= 4:
                                potential_medicines.append(clean_name)
        
        # Also try to find medicine names from the common list
        for medicine in self.common_ethiopian_medicines:
            if medicine.lower() in text.lower():
                potential_medicines.append(medicine)
        
        # Remove duplicates and return
        return list(set(potential_medicines))
    
    def validate_medicine_name(self, manual_medicine_name, prescription_image_path, threshold=70):
        """
        Validate if the manually entered medicine name matches any medicine found in the prescription
        
        Args:
            manual_medicine_name (str): Medicine name entered manually
            prescription_image_path (str): Path to the prescription image
            threshold (int): Similarity threshold (0-100)
        
        Returns:
            dict: Validation result with match status and details
        """
        try:
            if not os.path.exists(prescription_image_path):
                return {
                    'is_valid': False,
                    'error': 'Prescription image not found',
                    'confidence': 0,
                    'extracted_medicines': [],
                    'best_match': None
                }
            
            # Extract text from prescription image
            extracted_text = self.extract_text_from_image(prescription_image_path)
            
            if not extracted_text:
                return {
                    'is_valid': False,
                    'error': 'Could not extract text from prescription image',
                    'confidence': 0,
                    'extracted_medicines': [],
                    'best_match': None
                }
            
            # Extract potential medicine names
            extracted_medicines = self.extract_medicine_names(extracted_text)
            
            if not extracted_medicines:
                return {
                    'is_valid': False,
                    'error': 'No medicine names found in prescription',
                    'confidence': 0,
                    'extracted_medicines': [],
                    'best_match': None,
                    'extracted_text': extracted_text[:500]  # For debugging
                }
            
            # Clean the manual medicine name for comparison
            manual_name_clean = re.sub(r'\d+', '', manual_medicine_name).strip()
            manual_name_clean = re.sub(r'mg|ml|gm|mcg', '', manual_name_clean, flags=re.IGNORECASE).strip()
            
            # Find the best match using fuzzy string matching
            best_match = process.extractOne(
                manual_name_clean, 
                extracted_medicines,
                scorer=fuzz.token_sort_ratio
            )
            
            if best_match:
                match_name, confidence = best_match
                is_valid = confidence >= threshold
                
                return {
                    'is_valid': is_valid,
                    'confidence': confidence,
                    'extracted_medicines': extracted_medicines,
                    'best_match': match_name,
                    'manual_medicine': manual_medicine_name,
                    'threshold': threshold,
                    'extracted_text': extracted_text[:500]  # For debugging
                }
            else:
                return {
                    'is_valid': False,
                    'confidence': 0,
                    'extracted_medicines': extracted_medicines,
                    'best_match': None,
                    'manual_medicine': manual_medicine_name,
                    'threshold': threshold,
                    'extracted_text': extracted_text[:500]  # For debugging
                }
                
        except Exception as e:
            logger.error(f"Error validating medicine name: {str(e)}")
            return {
                'is_valid': False,
                'error': f'Validation error: {str(e)}',
                'confidence': 0,
                'extracted_medicines': [],
                'best_match': None
            }
    
    def batch_validate_medicines(self, medicine_list, prescription_image_path, threshold=70):
        """
        Validate multiple medicines against a prescription image
        
        Args:
            medicine_list (list): List of medicine names to validate
            prescription_image_path (str): Path to the prescription image
            threshold (int): Similarity threshold (0-100)
        
        Returns:
            dict: Validation results for each medicine
        """
        results = {}
        
        for medicine_name in medicine_list:
            results[medicine_name] = self.validate_medicine_name(
                medicine_name, 
                prescription_image_path, 
                threshold
            )
        
        return results
    
    def get_prescription_summary(self, prescription_image_path):
        """
        Get a summary of all medicines found in a prescription
        
        Args:
            prescription_image_path (str): Path to the prescription image
        
        Returns:
            dict: Summary of prescription contents
        """
        try:
            extracted_text = self.extract_text_from_image(prescription_image_path)
            extracted_medicines = self.extract_medicine_names(extracted_text)
            
            return {
                'success': True,
                'extracted_text': extracted_text,
                'medicine_count': len(extracted_medicines),
                'medicines': extracted_medicines,
                'text_length': len(extracted_text)
            }
            
        except Exception as e:
            logger.error(f"Error getting prescription summary: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'medicine_count': 0,
                'medicines': [],
                'text_length': 0
            }