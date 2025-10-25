#!/usr/bin/env python3
"""
Model Training Script
This script trains ML models using data from MongoDB and PySpark
"""

import sys
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
from pymongo import MongoClient
from app.config import settings
from app.services.preprocessing import preprocess_text
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.client = MongoClient(settings.mongodb_url)
        self.db = self.client[settings.mongodb_database]
        self.models_dir = Path(__file__).parent.parent.parent / "data" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def load_training_data(self):
        """Load and prepare training data from MongoDB"""
        logger.info("Loading data from MongoDB...")
        
        # Fetch all videos
        videos = list(self.db.videos.find({}, {
            'video_id': 1,
            'title': 1,
            'description': 1,
            'view_count': 1,
            'likes': 1,
            'dislikes': 1,
            'comment_count': 1,
            'tags': 1,
            'category_id': 1
        }))
        
        
        df = pd.DataFrame(videos)
        
        # Create features
        df['text'] = df['title'].fillna('') + ' ' + df['description'].fillna('')
        
        # Calculate engagement metrics
        df['like_ratio'] = df.apply(lambda x: x['likes']/(x['likes'] + x['dislikes']) 
                                   if x['likes'] + x['dislikes'] > 0 else 0, axis=1)
        df['engagement_rate'] = (df['likes'] + df['dislikes'] + df['comment_count']) / df['view_count'].clip(lower=1)
        
        # Create features for fake news detection
        df['features'] = df.apply(self._create_feature_vector, axis=1)
        
        logger.info(f"Loaded {len(df)} videos for training")
        return df

    def _create_feature_vector(self, row):
        """Create feature vector for each video"""
        features = {
            'like_ratio': row['like_ratio'],
            'engagement_rate': row['engagement_rate'],
            'has_description': 1 if pd.notna(row['description']) else 0,
            'title_length': len(str(row['title'])),
            'description_length': len(str(row['description'])) if pd.notna(row['description']) else 0,
            'view_count_log': np.log1p(row['view_count']),
            'comment_ratio': row['comment_count'] / row['view_count'] if row['view_count'] > 0 else 0
        }
        return features

    def train_models(self, df):
        """Train the fake news detection model"""
        logger.info("Starting model training...")
        
        # Prepare features
        X = pd.DataFrame(df['features'].tolist())
        
        # Create labels (example: using engagement metrics as proxy)
        # In real application, you would use actual labeled data
        y = (df['like_ratio'] > df['like_ratio'].median()).astype(int)
        
        # Text vectorization
        vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        text_features = vectorizer.fit_transform(df['text'])
        
        # Combine numerical and text features
        X_combined = np.hstack([X, text_features.toarray()])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X_combined, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Model Accuracy: {accuracy:.4f}")
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred))
        
        # Save models
        joblib.dump(model, self.models_dir / "fake_news_detector.pkl")
        joblib.dump(vectorizer, self.models_dir / "text_vectorizer.pkl")
        
        # Save feature columns
        feature_cols = list(X.columns)
        joblib.dump(feature_cols, self.models_dir / "feature_columns.pkl")
        
        logger.info("Models and features saved successfully")

    def cleanup(self):
        self.client.close()
        logger.info("MongoDB connection closed")

def main():
    try:
        trainer = ModelTrainer()
        
        # Load and prepare data
        df = trainer.load_training_data()
        
        # Train models
        trainer.train_models(df)
        
        logger.info("Training completed successfully")
        
    except Exception as e:
        logger.error(f"Error in model training: {e}")
        raise
    finally:
        if 'trainer' in locals():
            trainer.cleanup()

if __name__ == "__main__":
    main()