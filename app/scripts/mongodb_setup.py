#!/usr/bin/env python3
"""
MongoDB Setup Script
This script sets up MongoDB collections and indexes using PyMongo
"""

import sys
import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MongoDBSetup:
    def __init__(self):
        self.client = MongoClient(settings.mongodb_url)
        self.db = self.client[settings.mongodb_database]
    
    def create_collections_and_indexes(self):
        """Create collections and set up indexes using PyMongo"""
        logger.info(f"Setting up MongoDB collections and indexes in: {settings.mongodb_database}")
        
        # Create users collection with indexes
        users_collection = self.db.users
        try:
            users_collection.create_index("email", unique=True, name="email_unique")
            users_collection.create_index("username", unique=True, name="username_unique")
            users_collection.create_index("created_at", name="created_at_idx")
            logger.info("Users collection indexes created")
        except Exception as e:
            logger.warning(f"Users indexes might already exist: {e}")
        
        # Create videos collection with indexes
        videos_collection = self.db.videos
        try:
            videos_collection.create_index("video_id", unique=True, name="video_id_unique")
            videos_collection.create_index("created_at", name="videos_created_at_idx")
            videos_collection.create_index([("title", "text"), ("description", "text")], name="videos_text_idx")
            videos_collection.create_index("channel_title", name="channel_title_idx")
            videos_collection.create_index("category", name="category_idx")
            logger.info("Videos collection indexes created")
        except Exception as e:
            logger.warning(f"Videos indexes might already exist: {e}")
        
        # Create comments collection with indexes
        comments_collection = self.db.comments
        try:
            comments_collection.create_index("comment_id", unique=True, name="comment_id_unique")
            comments_collection.create_index("video_id", name="video_id_idx")
            comments_collection.create_index("author", name="author_idx")
            comments_collection.create_index("published_at", name="comment_published_at_idx")
            comments_collection.create_index("sentiment_score", name="sentiment_score_idx")
            comments_collection.create_index("toxicity_score", name="toxicity_score_idx")
            comments_collection.create_index("flagged", name="flagged_idx")
            logger.info("Comments collection indexes created")
        except Exception as e:
            logger.warning(f"Comments indexes might already exist: {e}")
        
        # Create analyses collection with indexes
        analyses_collection = self.db.analyses
        try:
            analyses_collection.create_index("video_id", name="analysis_video_id_idx")
            analyses_collection.create_index("risk_score", name="risk_score_idx")
            analyses_collection.create_index("fake_news_probability", name="fake_news_prob_idx")
            analyses_collection.create_index("created_at", name="analysis_created_at_idx")
            logger.info("Analyses collection indexes created")
        except Exception as e:
            logger.warning(f"Analyses indexes might already exist: {e}")
        
        # Create reports collection with indexes
        reports_collection = self.db.reports
        try:
            reports_collection.create_index("video_id", name="report_video_id_idx")
            reports_collection.create_index("generated_at", name="report_generated_at_idx")
            reports_collection.create_index("risk_level", name="risk_level_idx")
            logger.info("Reports collection indexes created")
        except Exception as e:
            logger.warning(f"Reports indexes might already exist: {e}")
        
        # Create additional collections for analysis results
        self.db.analysis_summaries.create_index("generated_at", name="summary_generated_at_idx")
        self.db.alerts.create_index("timestamp", name="alert_timestamp_idx")
        self.db.alerts.create_index("type", name="alert_type_idx")
        
        logger.info("All collections and indexes created successfully")
    
    def insert_sample_data(self):
        """Insert sample data using PyMongo"""
        logger.info("Inserting sample data...")
        
        # Sample user
        sample_user = {
            "username": "admin",
            "email": "admin@fake-news-detection.com",
            "password": "hashed_password_here",
            "is_active": True,
            "is_admin": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        try:
            result = self.db.users.insert_one(sample_user)
            logger.info(f"Sample user inserted with ID: {result.inserted_id}")
        except DuplicateKeyError:
            logger.info("Sample user already exists")
        
        logger.info("Sample data insertion completed")
    
    def get_database_stats(self):
        """Get database statistics using PyMongo"""
        stats = self.db.command("dbStats")
        collection_stats = {}
        
        for collection_name in self.db.list_collection_names():
            collection_stats[collection_name] = self.db.command("collStats", collection_name)
        
        return {
            "database_stats": stats,
            "collection_stats": collection_stats
        }
    
    def cleanup(self):
        """Clean up connections"""
        self.client.close()
        logger.info("MongoDB connection closed")

def main():
    setup = MongoDBSetup()
    
    try:
        setup.create_collections_and_indexes()
        setup.insert_sample_data()
        
        stats = setup.get_database_stats()
        logger.info(f"Database stats: {stats['database_stats']['dataSize']} bytes")
        
    except Exception as e:
        logger.error(f"Error in MongoDB setup: {e}")
        raise
    finally:
        setup.cleanup()

if __name__ == "__main__":
    main()