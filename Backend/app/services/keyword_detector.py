import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class KeywordDetector:
    def __init__(self):
        # Define suspicious keyword patterns
        self.suspicious_patterns = [
            r'\b(shocking|unbelievable|incredible|insane|crazy)\b',
            r'\b(you won\'t believe|must see|everyone is talking about)\b',
            r'\b(breaking news|breaking|urgent|alert)\b',
            r'\b(secret|truth|exposed|revealed)\b',
            r'\b(government|conspiracy|coverup)\b',
            r'\b(!+)\b',  # Multiple exclamation marks
        ]
        
        # Define fact-check keywords
        self.fact_check_keywords = [
            'source', 'evidence', 'study', 'research', 'data', 'statistics',
            'verified', 'confirmed', 'proven', 'documented', 'reported'
        ]
    
    def detect_keywords(self, text: str) -> List[str]:
        """Detect suspicious keywords in text"""
        if not text or not isinstance(text, str):
            return []
        
        detected_keywords = []
        text_lower = text.lower()
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            detected_keywords.extend(matches)
        
        # Check for fact-check keywords
        for keyword in self.fact_check_keywords:
            if keyword.lower() in text_lower:
                detected_keywords.append(keyword)
        
        # Extract unique keywords
        unique_keywords = list(set(detected_keywords))
        
        return unique_keywords
    
    def analyze_keyword_density(self, text: str) -> Dict[str, Any]:
        """Analyze keyword density and patterns"""
        if not text:
            return {"density_score": 0.0, "suspicious_count": 0, "keywords": []}
        
        keywords = self.detect_keywords(text)
        word_count = len(text.split())
        density_score = len(keywords) / word_count if word_count > 0 else 0
        
        return {
            "density_score": density_score,
            "suspicious_count": len([k for k in keywords if k in ['shocking', 'unbelievable', 'breaking', 'truth', 'secret']]),
            "keywords": keywords,
            "keyword_ratio": len(keywords) / word_count if word_count > 0 else 0
        }

# Global instance
detector = KeywordDetector()

def detect_keywords(text: str) -> List[str]:
    """Public function to detect keywords"""
    return detector.detect_keywords(text)