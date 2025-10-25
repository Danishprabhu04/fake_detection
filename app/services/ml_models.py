import logging
import joblib
from pathlib import Path
import numpy as np
from typing import Dict, Any
from datetime import datetime
from googleapiclient.discovery import build
from app.config import settings
from app.services.preprocessing import preprocess_text

# Configure logging
logger = logging.getLogger(__name__)

# Define constants
MODELS_DIR = Path("data/models")

async def analyze_video(video_id: str, analysis_type: str) -> Dict[str, Any]:
    """Analyze video content for fake news detection"""
    try:
        # Load trained models
        model_path = MODELS_DIR / "fake_news_detector.pkl"
        vectorizer_path = MODELS_DIR / "text_vectorizer.pkl"
        
        if not model_path.exists() or not vectorizer_path.exists():
            raise FileNotFoundError("Model files not found. Please train models first.")
            
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        
        # Get video details from YouTube
        video_details = await get_video_details(video_id)
        
        # Prepare text for analysis
        text_content = f"{video_details['title']} {video_details['description']}"
        processed_text = preprocess_text(text_content)
        
        # Vectorize text
        features = vectorizer.transform([processed_text])
        
        # Get prediction
        probability = model.predict_proba(features)[0][1]
        is_fake = probability > 0.5
        
        # Prepare analysis result
        result = {
            "video_id": video_id,
            "analysis_type": analysis_type,
            "is_fake": is_fake,
            "confidence_score": float(probability),
            "risk_score": float(probability),
            "analyzed_at": datetime.utcnow(),
            "analysis_version": "1.0",
            "details": {
                "content_score": round(1 - probability, 2),
                "risk_level": "High" if probability > 0.7 else "Medium" if probability > 0.3 else "Low"
            }
        }
        
        logger.info(f"Analysis completed for video {video_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing video {video_id}: {str(e)}")
        raise

async def get_video_details(video_id: str) -> Dict[str, Any]:
    """Fetch video details from YouTube Data API"""
    try:
        youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)
        
        response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()
        
        if not response['items']:
            raise ValueError(f"Video {video_id} not found")
            
        video = response['items'][0]
        snippet = video['snippet']
        stats = video['statistics']
        
        return {
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'channel_title': snippet.get('channelTitle', ''),
            'publish_date': snippet.get('publishedAt', ''),
            'view_count': int(stats.get('viewCount', 0)),
            'like_count': int(stats.get('likeCount', 0)),
            'comment_count': int(stats.get('commentCount', 0))
        }
        
    except Exception as e:
        logger.error(f"Error fetching video details: {str(e)}")
        raise