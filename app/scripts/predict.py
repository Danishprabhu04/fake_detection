import joblib
import pandas as pd
import numpy as np
from googleapiclient.discovery import build
from app.config import settings
from pathlib import Path

def get_video_details(video_id: str):
    """Fetch video details from YouTube API"""
    youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)
    
    # Get video details
    video_response = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
    ).execute()
    
    if not video_response['items']:
        raise ValueError("Video not found")
        
    video = video_response['items'][0]
    
    return {
        'video_id': video_id,
        'title': video['snippet']['title'],
        'description': video['snippet'].get('description', ''),
        'view_count': int(video['statistics'].get('viewCount', 0)),
        'likes': int(video['statistics'].get('likeCount', 0)),
        'dislikes': 0,  # YouTube no longer provides dislike counts
        'comment_count': int(video['statistics'].get('commentCount', 0))
    }

def predict_fake_news(video_url: str):
    """Predict if a YouTube video is fake news"""
    # Extract video ID from URL
    video_id = video_url.split('v=')[-1].split('&')[0]
    
    # Load models and features
    models_dir = Path(__file__).parent.parent.parent / "data" / "models"
    model = joblib.load(models_dir / "fake_news_detector.pkl")
    vectorizer = joblib.load(models_dir / "text_vectorizer.pkl")
    feature_cols = joblib.load(models_dir / "feature_columns.pkl")
    
    # Get video details
    video = get_video_details(video_id)
    
    # Create features
    features = {
        'like_ratio': video['likes'] / (video['likes'] + video['dislikes']) if video['likes'] + video['dislikes'] > 0 else 0,
        'engagement_rate': (video['likes'] + video['comment_count']) / video['view_count'] if video['view_count'] > 0 else 0,
        'has_description': 1 if video['description'] else 0,
        'title_length': len(video['title']),
        'description_length': len(video['description']),
        'view_count_log': np.log1p(video['view_count']),
        'comment_ratio': video['comment_count'] / video['view_count'] if video['view_count'] > 0 else 0
    }
    
    # Prepare text features
    text = f"{video['title']} {video['description']}"
    text_features = vectorizer.transform([text])
    
    # Combine features
    X = np.hstack([pd.DataFrame([features])[feature_cols], text_features.toarray()])
    
    # Make prediction
    prediction = model.predict_proba(X)[0]
    
    return {
        'is_fake': bool(prediction[1] > 0.5),
        'confidence': float(max(prediction)),
        'video_details': video
    }