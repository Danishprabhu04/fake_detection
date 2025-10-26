from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class RiskCalculator:
    def __init__(self):
        # Weight factors for different risk indicators
        self.weights = {
            'sentiment_extremes': 0.2,
            'toxicity': 0.15,
            'suspicious_keywords': 0.25,
            'comment_patterns': 0.2,
            'thumbnail_flags': 0.2
        }
    
    def calculate_risk_score(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate overall risk score based on multiple factors"""
        try:
            score = 0.0
            
            # Sentiment-based risk
            sentiment_risk = self._calculate_sentiment_risk(analysis_result)
            score += sentiment_risk * self.weights['sentiment_extremes']
            
            # Toxicity-based risk
            toxicity_risk = self._calculate_toxicity_risk(analysis_result)
            score += toxicity_risk * self.weights['toxicity']
            
            # Keyword-based risk
            keyword_risk = self._calculate_keyword_risk(analysis_result)
            score += keyword_risk * self.weights['suspicious_keywords']
            
            # Comment pattern risk
            comment_risk = self._calculate_comment_risk(analysis_result)
            score += comment_risk * self.weights['comment_patterns']
            
            # Thumbnail-based risk
            thumbnail_risk = self._calculate_thumbnail_risk(analysis_result)
            score += thumbnail_risk * self.weights['thumbnail_flags']
            
            # Ensure score is between 0 and 1
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.5  # Default moderate risk
    
    def _calculate_sentiment_risk(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate risk based on sentiment analysis"""
        sentiment_data = analysis_result.get('sentiment_analysis', {})
        
        # Check for extreme sentiment in title/description
        title_sentiment = sentiment_data.get('title', {}).get('score', 0)
        desc_sentiment = sentiment_data.get('description', {}).get('score', 0)
        
        # Extreme positive or negative sentiment can indicate clickbait
        sentiment_extremes = abs(title_sentiment) + abs(desc_sentiment)
        
        # Also check comment sentiment
        comment_analysis = analysis_result.get('comment_analysis', {})
        avg_sentiment = comment_analysis.get('average_sentiment', 0)
        
        return min((abs(title_sentiment) + abs(desc_sentiment) + abs(avg_sentiment)) / 3, 1.0)
    
    def _calculate_toxicity_risk(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate risk based on toxicity scores"""
        comment_analysis = analysis_result.get('comment_analysis', {})
        avg_toxicity = comment_analysis.get('average_toxicity', 0)
        
        return min(avg_toxicity * 2, 1.0)  # Amplify toxicity impact
    
    def _calculate_keyword_risk(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate risk based on suspicious keywords"""
        keyword_data = analysis_result.get('keyword_analysis', {})
        
        # Check for suspicious keywords in title and description
        title_keywords = keyword_data.get('title', [])
        desc_keywords = keyword_data.get('description', [])
        
        suspicious_count = len([k for k in title_keywords + desc_keywords 
                              if k in ['shocking', 'unbelievable', 'breaking', 'truth', 'secret']])
        
        return min(suspicious_count * 0.2, 1.0)
    
    def _calculate_comment_risk(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate risk based on comment patterns"""
        comment_analysis = analysis_result.get('comment_analysis', {})
        
        total_comments = comment_analysis.get('total_comments', 0)
        negative_count = comment_analysis.get('negative_count', 0)
        flagged_count = comment_analysis.get('flagged_count', 0)
        
        if total_comments == 0:
            return 0.0
        
        # High negative sentiment ratio
        negative_ratio = negative_count / total_comments
        
        # High flagged comment ratio
        flagged_ratio = flagged_count / total_comments
        
        # Combine ratios
        combined_risk = (negative_ratio * 0.6) + (flagged_ratio * 0.4)
        
        return min(combined_risk, 1.0)
    
    def _calculate_thumbnail_risk(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate risk based on thumbnail analysis"""
        thumbnail_data = analysis_result.get('thumbnail_analysis', {})
        suspicious_elements = thumbnail_data.get('suspicious_elements', [])
        
        # Count suspicious elements
        suspicious_count = len(suspicious_elements)
        
        return min(suspicious_count * 0.2, 1.0)

# Global instance
calculator = RiskCalculator()

def calculate_risk_score(analysis_result: Dict[str, Any]) -> float:
    """Public function to calculate risk score"""
    return calculator.calculate_risk_score(analysis_result)