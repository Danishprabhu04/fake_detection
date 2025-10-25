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
from sklearn.feature_extraction.text import HashingVectorizer  # Changed from TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
from pymongo import MongoClient
from app.config import settings
from app.services.preprocessing import preprocess_text
from pathlib import Path
import gc  # For garbage collection

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
        self.batch_size = 1000  # Process data in batches
        self.max_features = 1000  # Reduced from 5000

    def load_training_data(self):
        """Load and prepare training data from MongoDB in batches"""
        logger.info("Loading data from MongoDB...")
        
        # Use cursor instead of loading all data at once
        cursor = self.db.videos.find(
            {},
            {
                'video_id': 1,
                'title': 1,
                'description': 1,
                'view_count': 1,
                'likes': 1,
                'dislikes': 1,
                'comment_count': 1
            }
        ).batch_size(self.batch_size)

        # Process in batches
        all_features = []
        all_texts = []
        batch = []
        
        for i, video in enumerate(cursor):
            batch.append(video)
            
            if len(batch) >= self.batch_size:
                features, texts = self._process_batch(batch)
                all_features.extend(features)
                all_texts.extend(texts)
                batch = []
                gc.collect()  # Force garbage collection
                logger.info(f"Processed {i+1} videos...")

        # Process remaining items
        if batch:
            features, texts = self._process_batch(batch)
            all_features.extend(features)
            all_texts.extend(texts)

        return pd.DataFrame(all_features), all_texts

    def _process_batch(self, batch):
        """Process a batch of videos"""
        df = pd.DataFrame(batch)
        
        features = []
        texts = []
        
        for _, row in df.iterrows():
            # Create feature vector
            feature = {
                'like_ratio': (row['likes']/(row['likes'] + row.get('dislikes', 0))) 
                             if row['likes'] + row.get('dislikes', 0) > 0 else 0,
                'engagement_rate': (row['likes'] + row.get('dislikes', 0) + row['comment_count']) 
                                 / max(row['view_count'], 1),
                'has_description': 1 if pd.notna(row.get('description')) else 0,
                'title_length': len(str(row.get('title', ''))),
                'description_length': len(str(row.get('description', ''))),
                'view_count_log': np.log1p(row['view_count']),
                'comment_ratio': row['comment_count'] / max(row['view_count'], 1)
            }
            features.append(feature)
            
            # Combine text
            text = f"{row.get('title', '')} {row.get('description', '')}"
            texts.append(text)
            
        return features, texts

    def train_models(self, features_df, texts):
        """Train with memory-efficient approach"""
        logger.info("Starting model training...")
        
        # Use HashingVectorizer instead of TfidfVectorizer (more memory efficient)
        vectorizer = HashingVectorizer(
            n_features=self.max_features,
            stop_words='english'
        )
        
        # Transform text features in batches
        text_features = vectorizer.transform(texts)
        
        # Create labels (using simplified approach)
        y = (features_df['like_ratio'] > features_df['like_ratio'].median()).astype(int)
        
        # Combine features
        X = np.hstack([features_df.values, text_features.toarray()])
        
        # Clear memory
        del text_features
        gc.collect()
        
        # Use smaller number of trees and reduced max_depth
        model = RandomForestClassifier(
            n_estimators=50,  # Reduced from 100
            max_depth=10,     # Added max_depth
            n_jobs=-1,        # Use all CPU cores
            random_state=42
        )
        
        # Train and evaluate
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        model.fit(X_train, y_train)
        
        # Save models
        joblib.dump(model, self.models_dir / "fake_news_detector.pkl")
        joblib.dump(vectorizer, self.models_dir / "text_vectorizer.pkl")
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Model Accuracy: {accuracy:.4f}")
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred))
        
        logger.info("Models and features saved successfully")

    def cleanup(self):
        self.client.close()
        logger.info("MongoDB connection closed")

def main():
    try:
        trainer = ModelTrainer()
        
        # Load and prepare data
        df, texts = trainer.load_training_data()
        
        # Train models
        trainer.train_models(df, texts)
        
        logger.info("Training completed successfully")
        
    except Exception as e:
        logger.error(f"Error in model training: {e}")
        raise
    finally:
        if 'trainer' in locals():
            trainer.cleanup()

if __name__ == "__main__":
    main()