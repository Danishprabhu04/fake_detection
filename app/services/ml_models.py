import pickle
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import logging
from app.config import settings
from app.services.preprocessing import preprocess_text
from app.services.sentiment import analyze_sentiment
from app.services.keyword_detector import detect_keywords
from app.services.risk_calculator import calculate_risk_score

logger = logging.getLogger(__name__)

class MLModelService:
    def __init__(self):
        self.sentiment_model = None
        self.keyword_model = None
        self.fake_news_model = None
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            # Load sentiment model
            self.sentiment_model = joblib.load(settings.sentiment_model_path)
            logger.info("Sentiment model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading sentiment model: {e}")
            self.sentiment_model = None
        
        try:
            # Load keyword model
            self.keyword_model = joblib.load(settings.keyword_model_path)
            logger.info("Keyword model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading keyword model: {e}")
            self.keyword_model = None
    
    def train_sentiment_model(self, texts: list, labels: list):
        """Train sentiment analysis model"""
        try:
            # Preprocess texts
            processed_texts = [preprocess_text(text) for text in texts]
            
            # Create pipeline
            pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
                ('classifier', MultinomialNB())
            ])
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                processed_texts, labels, test_size=0.2, random_state=42
            )
            
            # Train model
            pipeline.fit(X_train, y_train)
            
            # Evaluate
            y_pred = pipeline.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            logger.info(f"Sentiment model trained with accuracy: {accuracy:.4f}")
            
            # Save model
            joblib.dump(pipeline, settings.sentiment_model_path)
            self.sentiment_model = pipeline
            
            return accuracy
        except Exception as e:
            logger.error(f"Error training sentiment model: {e}")
            return 0.0
    
    def predict_fake_news(self, text: str) -> Dict[str, Any]:
        """Predict if text contains fake news"""
        if not self.fake_news_model:
            return {"probability": 0.5, "confidence": 0.5}
        
        try:
            processed_text = preprocess_text(text)
            probability = self.fake_news_model.predict_proba([processed_text])[0][1]
            confidence = max(self.fake_news_model.predict_proba([processed_text])[0])
            
            return {
                "probability": float(probability),
                "confidence": float(confidence)
            }
        except Exception as e:
            logger.error(f"Error predicting fake news: {e}")
            return {"probability": 0.5, "confidence": 0.5}

# Global instance
ml_service = MLModelService()

async def analyze_video(video_id: str, analysis_type: str = "combined") -> Dict[str, Any]:
    """Perform comprehensive video analysis"""
    from app.database import get_database
    from app.services.youtube_api import YouTubeAPIService
    from app.services.thumbnail_analysis import analyze_thumbnail
    
    db = await get_database()
    youtube_service = YouTubeAPIService()
    
    # Get video document
    video = await db.videos.find_one({"video_id": video_id})
    if not video:
        raise ValueError(f"Video {video_id} not found")
    
    analysis_result = {
        "video_id": video_id,
        "analysis_type": analysis_type,
        "risk_score": 0.0,
        "confidence_score": 0.0,
        "fake_news_probability": 0.0,
        "sentiment_analysis": {},
        "keyword_analysis": {},
        "thumbnail_analysis": {},
        "transcript_analysis": {},
        "comment_analysis": {},
        "red_flags": [],
        "sources_verified": False,
        "fact_check_results": [],
        "analysis_summary": "",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Analyze video content
    if analysis_type in ["video", "combined"]:
        # Analyze title and description
        title_sentiment = analyze_sentiment(video["title"])
        desc_sentiment = analyze_sentiment(video["description"] or "")
        
        analysis_result["sentiment_analysis"]["title"] = title_sentiment
        analysis_result["sentiment_analysis"]["description"] = desc_sentiment
        
        # Extract keywords from title and description
        title_keywords = detect_keywords(video["title"])
        desc_keywords = detect_keywords(video["description"] or "")
        
        analysis_result["keyword_analysis"]["title"] = title_keywords
        analysis_result["keyword_analysis"]["description"] = desc_keywords
        
        # Analyze thumbnail
        if video.get("thumbnail_url"):
            thumbnail_result = await analyze_thumbnail(video["thumbnail_url"])
            analysis_result["thumbnail_analysis"] = thumbnail_result
    
    # Get and analyze transcript
    from app.services.transcript import get_video_transcript
    transcript = await get_video_transcript(video_id)
    if transcript:
        transcript_sentiment = analyze_sentiment(transcript)
        transcript_keywords = detect_keywords(transcript)
        
        analysis_result["transcript_analysis"]["sentiment"] = transcript_sentiment
        analysis_result["transcript_analysis"]["keywords"] = transcript_keywords
    
    # Analyze comments
    if analysis_type in ["comments", "combined"]:
        comments = await db.comments.find({"video_id": video_id}).to_list(None)
        
        if comments:
            # Aggregate comment analysis
            total_comments = len(comments)
            positive_comments = sum(1 for c in comments if c.get('sentiment_label') == 'positive')
            negative_comments = sum(1 for c in comments if c.get('sentiment_label') == 'negative')
            flagged_comments = sum(1 for c in comments if c.get('flagged', False))
            
            avg_sentiment = sum(c.get('sentiment_score', 0) for c in comments) / total_comments if total_comments > 0 else 0
            avg_toxicity = sum(c.get('toxicity_score', 0) for c in comments) / total_comments if total_comments > 0 else 0
            
            analysis_result["comment_analysis"] = {
                "total_comments": total_comments,
                "positive_count": positive_comments,
                "negative_count": negative_comments,
                "flagged_count": flagged_comments,
                "average_sentiment": avg_sentiment,
                "average_toxicity": avg_toxicity,
                "top_keywords": []
            }
    
    # Calculate overall risk score
    risk_score = calculate_risk_score(analysis_result)
    analysis_result["risk_score"] = risk_score
    
    # Generate red flags
    red_flags = []
    if risk_score > 0.7:
        red_flags.append("High risk score detected")
    if analysis_result["comment_analysis"].get("flagged_count", 0) > 0:
        red_flags.append(f"{analysis_result['comment_analysis']['flagged_count']} flagged comments")
    if analysis_result["comment_analysis"].get("negative_count", 0) > analysis_result["comment_analysis"].get("positive_count", 0):
        red_flags.append("More negative than positive comments")
    
    analysis_result["red_flags"] = red_flags
    
    # Generate summary
    summary_parts = []
    if analysis_result["risk_score"] > 0.8:
        summary_parts.append("HIGH RISK: Potential fake news detected")
    elif analysis_result["risk_score"] > 0.6:
        summary_parts.append("MODERATE RISK: Possible fake news indicators")
    else:
        summary_parts.append("LOW RISK: No major concerns detected")
    
    if red_flags:
        summary_parts.append(f"Red flags: {', '.join(red_flags[:2])}")
    
    analysis_result["analysis_summary"] = ". ".join(summary_parts)
    
    return analysis_result

def authenticate_user(db, username: str, password: str):
    """Authenticate user - simplified version for now"""
    import asyncio
    
    async def _get_user():
        user = await db.users.find_one({"username": username})
        if user:
            from app.utils.auth import verify_password
            if verify_password(password, user["password"]):
                return user
        return None
    
    # For now, return None to avoid async issues in this context
    # In production, this would be handled properly
    return None