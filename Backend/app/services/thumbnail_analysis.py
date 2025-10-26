import requests
import cv2
import pytesseract
import numpy as np
from PIL import Image
from io import BytesIO
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class ThumbnailAnalyzer:
    def __init__(self):
        # Set tesseract path if specified in config
        if settings.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_path
    
    async def analyze_thumbnail(self, thumbnail_url: str) -> Dict[str, Any]:
        """Analyze thumbnail for suspicious elements"""
        try:
            # Download thumbnail image
            response = requests.get(thumbnail_url)
            response.raise_for_status()
            
            # Convert to PIL Image
            image = Image.open(BytesIO(response.content))
            
            # Convert to OpenCV format
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Extract text using OCR
            text_extracted = self.extract_text_from_image(image_cv)
            
            # Analyze for suspicious elements
            suspicious_elements = self.detect_suspicious_elements(text_extracted, image_cv)
            
            # Calculate image quality metrics
            quality_metrics = self.calculate_image_metrics(image_cv)
            
            return {
                "text_extracted": text_extracted,
                "suspicious_elements": suspicious_elements,
                "quality_metrics": quality_metrics,
                "analysis_timestamp": "2023-01-01T00:00:00Z"  # This will be set in the calling function
            }
            
        except Exception as e:
            logger.error(f"Error analyzing thumbnail: {e}")
            return {
                "text_extracted": "",
                "suspicious_elements": ["analysis_failed"],
                "quality_metrics": {},
                "analysis_timestamp": "2023-01-01T00:00:00Z"
            }
    
    def extract_text_from_image(self, image) -> str:
        """Extract text from image using OCR"""
        try:
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def detect_suspicious_elements(self, text: str, image) -> list:
        """Detect suspicious elements in thumbnail"""
        suspicious_elements = []
        
        # Check for clickbait text patterns
        clickbait_patterns = [
            "SHOCKING", "UNBELIEVABLE", "YOU WON'T BELIEVE", 
            "BREAKING", "EXPOSED", "TRUTH", "SECRET", 
            "MUST SEE", "INCREDIBLE", "INSANE"
        ]
        
        text_upper = text.upper()
        for pattern in clickbait_patterns:
            if pattern in text_upper:
                suspicious_elements.append(f"clickbait_text: {pattern}")
        
        # Check for excessive exclamation marks
        if text.count('!') > 3:
            suspicious_elements.append("excessive_exclamation_marks")
        
        # Check for all caps text ratio
        words = text.split()
        if words:
            all_caps_ratio = sum(1 for word in words if word.isupper()) / len(words)
            if all_caps_ratio > 0.5:
                suspicious_elements.append("high_all_caps_ratio")
        
        return suspicious_elements
    
    def calculate_image_metrics(self, image) -> Dict[str, Any]:
        """Calculate image quality metrics"""
        try:
            # Calculate brightness
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # Calculate contrast
            contrast = gray.std()
            
            # Calculate sharpness (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            return {
                "brightness": float(brightness),
                "contrast": float(contrast),
                "sharpness": float(laplacian_var)
            }
        except Exception as e:
            logger.error(f"Error calculating image metrics: {e}")
            return {
                "brightness": 0.0,
                "contrast": 0.0,
                "sharpness": 0.0
            }

# Global instance
analyzer = ThumbnailAnalyzer()

async def analyze_thumbnail(thumbnail_url: str) -> Dict[str, Any]:
    """Public function to analyze thumbnail"""
    return await analyzer.analyze_thumbnail(thumbnail_url)