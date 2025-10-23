#!/usr/bin/env python3
"""
Model Training Script
This script trains ML models using data from MongoDB and PySpark
"""

import sys
import os
import logging
from datetime import datetime
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.services.preprocessing import preprocess_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("FakeNewsModelTraining") \
            .master(settings.spark_master) \
            .getOrCreate()
        
        self.mongo_client = MongoClient(settings.mongodb_url)
        self.db = self.mongo_client[settings.mongodb_database]
        
        self.models = {}
    
    def load_training_data_with_spark(self):
        """Load training data using PySpark for large datasets"""
        logger.info("Loading training data with PySpark...")
        
        # Load comments data using Spark
        comments_df = self.spark.read.format("mongodb") \
            .option("collection", "comments") \
            .load()
        
        # Filter and prepare training data
        training_df = comments_df.select(
            "text",
            "sentiment_score",
            "sentiment_label",
            "toxicity_score"
        ).filter(
            col("text").isNotNull() & 
            (col("sentiment_label").isNotNull())
        )
        
        # Convert to Pandas for model training
        training_data = training_df.toPandas()
        
        logger.info(f"Loaded {len(training_data)} training samples")
        return training_data
    
    def load_training_data_with_pymongo(self):
        """Load training data using PyMongo for smaller datasets or real-time data"""
        logger.info("Loading training data with PyMongo...")
        
        # Use PyMongo aggregation to get training data
        pipeline = [
            {
                "$match": {
                    "text": {"$exists": True, "$ne": None},
                    "sentiment_label": {"$exists": True, "$ne": None}
                }
            },
            {
                "$project": {
                    "text": 1,
                    "sentiment_score": 1,
                    "sentiment_label": 1,
                    "toxicity_score": 1
                }
            }
        ]
        
        training_data = list(self.db.comments.aggregate(pipeline))
        logger.info(f"Loaded {len(training_data)} training samples with PyMongo")
        
        return pd.DataFrame(training_data)
    
    def train_sentiment_model(self, training_data):
        """Train sentiment analysis model"""
        logger.info("Training sentiment analysis model...")
        
        # Prepare features and labels
        texts = training_data['text'].apply(preprocess_text).tolist()
        labels = training_data['sentiment_label'].tolist()
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        # Vectorize texts
        X = vectorizer.fit_transform(texts)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Train model
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Sentiment model accuracy: {accuracy:.4f}")
        logger.info(f"Classification report:\n{classification_report(y_test, y_pred)}")
        
        # Save model and vectorizer
        self.models['sentiment_model'] = model
        self.models['sentiment_vectorizer'] = vectorizer
        
        joblib.dump(model, settings.sentiment_model_path)
        joblib.dump(vectorizer, "data/models/sentiment_vectorizer.pkl")
        
        logger.info(f"Sentiment model saved to {settings.sentiment_model_path}")
    
    def train_fake_news_model(self, training_data):
        """Train fake news detection model"""
        logger.info("Training fake news detection model...")
        
        # For this example, we'll create synthetic labels based on existing data
        # In practice, you'd have labeled fake news data
        texts = training_data['text'].apply(preprocess_text).tolist()
        
        # Create synthetic labels (this is just an example)
        # In reality, you'd need actual fake news labels
        labels = [1 if score > 0.5 else 0 for score in training_data['sentiment_score']]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words='english'
        )
        
        # Vectorize texts
        X = vectorizer.fit_transform(texts)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42
        )
        
        # Train model
        model = MultinomialNB(alpha=0.1)
        model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Fake news model accuracy: {accuracy:.4f}")
        
        # Save model
        self.models['fake_news_model'] = model
        self.models['fake_news_vectorizer'] = vectorizer
        
        joblib.dump(model, "data/models/fake_news_model.pkl")
        joblib.dump(vectorizer, "data/models/fake_news_vectorizer.pkl")
        
        logger.info("Fake news model saved successfully")
    
    def train_all_models(self):
        """Train all models using both PyMongo and PySpark"""
        logger.info("Starting model training process...")
        
        # Load data using PySpark (for large datasets)
        spark_training_data = self.load_training_data_with_spark()
        
        if len(spark_training_data) > 0:
            # Train models
            self.train_sentiment_model(spark_training_data)
            self.train_fake_news_model(spark_training_data)
        else:
            logger.warning("No training data found, using PyMongo to load data...")
            # Load data using PyMongo (for smaller datasets or real-time data)
            pymongo_training_data = self.load_training_data_with_pymongo()
            
            if len(pymongo_training_data) > 0:
                self.train_sentiment_model(pymongo_training_data)
                self.train_fake_news_model(pymongo_training_data)
            else:
                logger.error("No training data available from either source")
                return
        
        logger.info("Model training completed successfully")
    
    def cleanup(self):
        """Clean up connections"""
        self.spark.stop()
        self.mongo_client.close()
        logger.info("Connections closed")

def main():
    trainer = ModelTrainer()
    
    try:
        trainer.train_all_models()
    except Exception as e:
        logger.error(f"Error in model training: {e}")
        raise
    finally:
        trainer.cleanup()

if __name__ == "__main__":
    main()