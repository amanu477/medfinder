"""
OCR Service for Prescription Medicine Validation
Extracts text from prescription images and validates medicine names
"""

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    TESSERACT_AVAILABLE = True
except ImportError as e:
    TESSERACT_AVAILABLE = False
    print(f"Tesseract not available: {e}")

import re
from fuzzywuzzy import fuzz, process
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

class PrescriptionOCRService:
    """Service for extracting and validating medicine names from prescription images"""
    
    def __init__(self):
        # Check if Tesseract is available
        self.tesseract_available = TESSERACT_AVAILABLE
        
        # Try to configure Tesseract path for Windows
        if self.tesseract_available:
            import platform
            if platform.system() == 'Windows':
                # Common Windows installation paths
                windows_paths = [
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                    r'C:\Tesseract-OCR\tesseract.exe',
                ]
                for path in windows_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
        
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
        
        # Medicine name variations and common misspellings
        self.medicine_variations = {
            'aspirin': ['asprin', 'asperin', 'asperine', 'asirin', 'aspirine', 'asa', 'acetylsalicylic'],
            'paracetamol': ['panadol', 'acetaminophen', 'tylenol', 'parcetamol', 'paracetarnol'],
            'ibuprofen': ['brufen', 'advil', 'motrin', 'ibuprophen', 'ibupropen'],
            'amoxicillin': ['amoxycillin', 'amoxil', 'amoxicilin', 'amoxicilline'],
            'ciprofloxacin': ['cipro', 'ciproxin', 'ciprofloxacine', 'ciproloxacin'],
            'metronidazole': ['flagyl', 'metronidazol', 'metronidazole'],
            'omeprazole': ['losec', 'prilosec', 'omeprazol', 'omeprazole'],
            'diclofenac': ['voltaren', 'diclofenac', 'diclofen', 'diclofenac'],
        }
    
    def preprocess_image(self, image_path):
        """
        Preprocess the image for better OCR accuracy using PIL
        """
        try:
            # Open image using PIL
            img = Image.open(image_path)
            
            # Convert to RGB first, then to grayscale
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img = img.convert('L')
            
            # Resize image if too small (improves OCR accuracy)
            width, height = img.size
            if width < 300 or height < 300:
                # Scale up small images
                scale = max(300/width, 300/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            # Apply filter to reduce noise
            img = img.filter(ImageFilter.MedianFilter(size=3))
            
            # Apply edge enhancement for better text detection
            img = img.filter(ImageFilter.EDGE_ENHANCE)
            
            return img
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            return None
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from prescription image using OCR
        """
        if not self.tesseract_available:
            logger.error("Tesseract OCR is not available. Please install Tesseract OCR.")
            return "Tesseract OCR not installed. Please install Tesseract OCR to use prescription validation."
            
        try:
            # Preprocess the image
            processed_img = self.preprocess_image(image_path)
            if processed_img is None:
                # Try with original image if preprocessing fails
                processed_img = Image.open(image_path)
            
            # Configure Tesseract for better accuracy with multiple PSM modes
            custom_configs = [
                r'--oem 3 --psm 6',  # Uniform block of text
                r'--oem 3 --psm 8',  # Single word
                r'--oem 3 --psm 13', # Raw line
                r'--oem 3 --psm 11', # Sparse text
                r'--oem 3 --psm 12', # Sparse text with OSD
            ]
            
            # Try multiple OCR configurations to get best results
            text = ""
            for config in custom_configs:
                try:
                    current_text = pytesseract.image_to_string(processed_img, config=config)
                    if len(current_text) > len(text):
                        text = current_text
                except Exception as e:
                    logger.warning(f"OCR config {config} failed: {str(e)}")
                    continue
            
            # Clean up the extracted text
            text = self.clean_extracted_text(text)
            
            logger.info(f"Extracted text from {image_path}: {len(text)} characters extracted")
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
    
    def apply_ocr_corrections(self, text):
        """
        Apply common OCR corrections to improve text matching
        """
        if not text:
            return text
            
        # Common OCR character corrections
        corrections = [
            ('0', 'o'),  # Zero to lowercase o
            ('1', 'l'),  # One to lowercase l
            ('5', 'S'),  # Five to uppercase S
            ('8', 'B'),  # Eight to uppercase B
            ('6', 'G'),  # Six to uppercase G
            ('rn', 'm'), # Common OCR error: rn -> m
            ('nn', 'm'), # Common OCR error: nn -> m
            ('|', 'l'),  # Pipe to lowercase l
            ('I', 'l'),  # Uppercase I to lowercase l
        ]
        
        corrected_text = text
        for wrong, correct in corrections:
            corrected_text = corrected_text.replace(wrong, correct)
            
        return corrected_text
    
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
    
    def validate_medicine_name(self, manual_medicine_name, prescription_text_or_path, threshold=60):
        """
        Validate if the manually entered medicine name matches any medicine found in the prescription
        
        Args:
            manual_medicine_name (str): Medicine name entered manually
            prescription_text_or_path (str): Either prescription text or path to prescription image
            threshold (int): Similarity threshold (0-100)
        
        Returns:
            dict: Validation result with match status and details
        """
        try:
            # Determine if input is file path or text
            if os.path.exists(prescription_text_or_path):
                # It's a file path
                extracted_text = self.extract_text_from_image(prescription_text_or_path)
            else:
                # It's text content
                extracted_text = prescription_text_or_path
            
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
                    'extracted_text': extracted_text  # Full text without truncation
                }
            
            # Clean the manual medicine name for comparison
            manual_name_clean = re.sub(r'\d+', '', manual_medicine_name).strip()
            manual_name_clean = re.sub(r'mg|ml|gm|mcg', '', manual_name_clean, flags=re.IGNORECASE).strip()
            
            # Check for medicine variations first
            medicine_to_check = [manual_name_clean.lower()]
            
            # Add variations if the medicine is in our variations dictionary
            for base_med, variations in self.medicine_variations.items():
                if manual_name_clean.lower() == base_med.lower():
                    medicine_to_check.extend(variations)
                elif manual_name_clean.lower() in [v.lower() for v in variations]:
                    medicine_to_check.append(base_med)
                    medicine_to_check.extend(variations)
            
            # Remove duplicates
            medicine_to_check = list(set(medicine_to_check))
            
            # Enhanced matching: Only accept high-confidence exact or near-exact matches
            best_match = None
            best_confidence = 0
            
            # Log what we're looking for and what we found
            logger.info(f"Looking for medicine: {manual_medicine_name}")
            logger.info(f"Variations to check: {medicine_to_check}")
            logger.info(f"Extracted medicines: {extracted_medicines}")
            logger.info(f"Extracted text length: {len(extracted_text)} characters")
            
            # Strategy 1: Direct text search (highest confidence)
            for med_variation in medicine_to_check:
                if med_variation.lower() in extracted_text.lower():
                    # Direct match found, set high confidence
                    direct_confidence = 95
                    if direct_confidence > best_confidence:
                        best_match = (med_variation, direct_confidence)
                        best_confidence = direct_confidence
                        logger.info(f"Found direct text match for '{med_variation}' with confidence {direct_confidence}")
            
            # Strategy 2: Exact word matching in extracted medicines list
            if best_confidence == 0:  # Only if no direct match found
                for med_variation in medicine_to_check:
                    for extracted_med in extracted_medicines:
                        # Use strict ratio matching for exact medicine names
                        similarity = fuzz.ratio(med_variation.lower(), extracted_med.lower())
                        if similarity >= 85:  # High threshold for medicine name matching
                            if similarity > best_confidence:
                                best_match = (extracted_med, similarity)
                                best_confidence = similarity
                                logger.info(f"Found exact medicine match: '{extracted_med}' for '{med_variation}' with confidence {similarity}")
            
            # Strategy 3: Word-by-word matching in text (more conservative)
            if best_confidence == 0:  # Only if no good match found yet
                for med_variation in medicine_to_check:
                    text_words = extracted_text.lower().split()
                    for word in text_words:
                        # Clean the word and check if it's a potential medicine name
                        clean_word = re.sub(r'[^\w]', '', word)
                        if len(clean_word) >= len(med_variation) * 0.8:  # Word must be reasonable length
                            similarity = fuzz.ratio(med_variation.lower(), clean_word)
                            # Only accept very high similarity for word matching
                            if similarity >= 90:  # Very high threshold to avoid false positives
                                if similarity > best_confidence:
                                    best_match = (clean_word, similarity)
                                    best_confidence = similarity
                                    logger.info(f"Found word match: '{clean_word}' for '{med_variation}' with confidence {similarity}")
            
            # Strategy 4: If still no match, medicine is not in prescription
            if best_confidence < 70:  # If no strong match found, consider it not found
                logger.info(f"No strong match found for '{manual_medicine_name}' in prescription. Best confidence: {best_confidence}%")
                best_confidence = 0
                best_match = None
            
            if best_match:
                match_name, confidence = best_match
                # Use the better confidence score
                if best_confidence > confidence:
                    confidence = best_confidence
                is_valid = confidence >= threshold
                
                # Enhanced: Check if confidence is too low and set to 0% if medicine not found
                if confidence < 30:  # Very low threshold indicates medicine not in prescription
                    logger.info(f"Low confidence ({confidence}%) for '{manual_medicine_name}'. Medicine likely not in prescription. Setting to 0%")
                    confidence = 0
                    is_valid = False
                    match_name = None
                
                return {
                    'is_valid': is_valid,
                    'confidence': confidence,
                    'extracted_medicines': extracted_medicines,
                    'best_match': match_name,
                    'manual_medicine': manual_medicine_name,
                    'threshold': threshold,
                    'extracted_text': extracted_text,  # Full text without truncation
                    'validation_reason': f"Medicine {'found' if confidence > 0 else 'not found'} in prescription image"
                }
            else:
                # Enhanced: Medicine not found in prescription - return 0% confidence
                logger.info(f"Medicine '{manual_medicine_name}' not found in prescription image. Setting confidence to 0%")
                return {
                    'is_valid': False,
                    'confidence': 0,
                    'extracted_medicines': extracted_medicines,
                    'best_match': None,
                    'manual_medicine': manual_medicine_name,
                    'threshold': threshold,
                    'extracted_text': extracted_text,  # Full text without truncation
                    'validation_reason': 'Medicine not found in prescription image'
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
    
    def get_medicine_confidence(self, manual_medicine_name, prescription_text_or_path):
        """
        Simple method to get confidence score for a medicine name
        
        Args:
            manual_medicine_name (str): Medicine name entered manually
            prescription_text_or_path (str): Either prescription text or path to prescription image
        
        Returns:
            float: Confidence score (0-100)
        """
        try:
            result = self.validate_medicine_name(manual_medicine_name, prescription_text_or_path)
            return result.get('confidence', 0)
        except Exception as e:
            logger.error(f"Error getting medicine confidence: {str(e)}")
            return 0
    
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