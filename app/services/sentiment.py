from textblob import TextBlob
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze sentiment of text using TextBlob"""
    try:
        if not text or not isinstance(text, str):
            return {"score": 0.0, "label": "neutral"}
        
        # Create TextBlob object
        blob = TextBlob(text)
        
        # Get polarity (-1 to 1, where -1 is negative, 1 is positive)
        polarity = blob.sentiment.polarity
        
        # Determine sentiment label
        if polarity > 0.1:
            label = "positive"
        elif polarity < -0.1:
            label = "negative"
        else:
            label = "neutral"
        
        return {
            "score": float(polarity),
            "label": label,
            "confidence": abs(float(polarity))
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return {"score": 0.0, "label": "neutral"}

def analyze_sentiment_batch(texts: list) -> list:
    """Analyze sentiment for multiple texts"""
    results = []
    for text in texts:
        results.append(analyze_sentiment(text))
    return results