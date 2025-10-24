#!/usr/bin/env python3
"""
Data Ingestion Script - MongoDB + PySpark Integration
This script demonstrates the use of both PyMongo and PySpark MapReduce for data processing
"""

import sys
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
import json
import asyncio
from pymongo import MongoClient
from pymongo.collection import Collection
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, sum as spark_sum, regexp_replace, lower, when
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, BooleanType, TimestampType
import pandas as pd
from dotenv import load_dotenv
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Add the app directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataIngestionManager:
    def __init__(self):
        self.mongo_client = None
        self.spark = None
        self.db = None
        self.collections = {}
        self.setup_connections()
    
    def setup_connections(self):
        """Initialize MongoDB and Spark connections"""
        # MongoDB connection using PyMongo
        self.mongo_client = MongoClient(settings.mongodb_url)
        self.db = self.mongo_client[settings.mongodb_database]
        
        # Get collections
        self.collections = {
            'users': self.db.users,
            'videos': self.db.videos,
            'comments': self.db.comments,
            'analyses': self.db.analyses,
            'reports': self.db.reports
        }
        
        logger.info(f"Connected to MongoDB: {settings.mongodb_database} using PyMongo")
        
        # Spark session for MapReduce operations
        self.spark = SparkSession.builder \
            .appName(settings.spark_app_name) \
            .master(settings.spark_master) \
            .config("spark.mongodb.input.uri", f"{settings.mongodb_url}/{settings.mongodb_database}") \
            .config("spark.mongodb.output.uri", f"{settings.mongodb_url}/{settings.mongodb_database}") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        logger.info(f"Spark session created for MapReduce: {settings.spark_app_name}")
    
    def load_json_dataset(self, json_file_path: str) -> List[Dict]:
        """Load JSON dataset using PyMongo for direct database operations"""
        logger.info(f"Loading JSON dataset from: {json_file_path}")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                if json_file_path.endswith('.jsonl') or json_file_path.endswith('.json'):
                    data = [json.loads(line) if line.strip() else json.loads(line) for line in file]
                else:
                    data = json.load(file)
            
            logger.info(f"Loaded {len(data)} records from {json_file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading JSON dataset: {e}")
            return []
    
    def bulk_insert_with_pymongo(self, collection_name: str, data: List[Dict]):
        """Use PyMongo for efficient bulk insertions"""
        collection = self.collections[collection_name]
        
        # Add timestamps for new records
        for record in data:
            record['created_at'] = datetime.utcnow()
            record['updated_at'] = datetime.utcnow()
        
        try:
            # Use PyMongo bulk insert for high-performance data loading
            result = collection.insert_many(data)
            logger.info(f"Successfully inserted {len(result.inserted_ids)} records into {collection_name} using PyMongo")
            return result.inserted_ids
            
        except Exception as e:
            logger.error(f"Error in PyMongo bulk insert: {e}")
            raise
    
    def process_and_analyze_with_spark(self):
        """Use PySpark for MapReduce analysis on large datasets"""
        logger.info("Starting PySpark MapReduce analysis...")
        
        try:
            # Read data from MongoDB into Spark DataFrames
            videos_df = self.spark.read.format("mongodb").option("collection", "videos").load()
            comments_df = self.spark.read.format("mongodb").option("collection", "comments").load()
            analyses_df = self.spark.read.format("mongodb").option("collection", "analyses").load()
            
            # ANALYSIS 1: PySpark MapReduce - Video Risk Analysis
            logger.info("Analysis 1: PySpark MapReduce - Video Risk Analysis")
            
            # Map: Calculate risk indicators for each video
            video_risk_analysis = videos_df.join(
                analyses_df, 
                videos_df.video_id == analyses_df.video_id, 
                "left"
            ).select(
                videos_df.video_id,
                videos_df.title,
                videos_df.channel_title,
                videos_df.view_count,
                videos_df.like_count,
                videos_df.comment_count,
                analyses_df.risk_score,
                analyses_df.fake_news_probability
            ).withColumn(
                "risk_category",
                when(col("risk_score") > 0.7, "High Risk")
                .when(col("risk_score") > 0.4, "Medium Risk")
                .otherwise("Low Risk")
            )
            
            # Reduce: Aggregate by risk category
            risk_summary = video_risk_analysis.groupBy("risk_category") \
                .agg(
                    count("*").alias("video_count"),
                    avg("risk_score").alias("avg_risk_score"),
                    avg("fake_news_probability").alias("avg_fake_prob"),
                    spark_sum("view_count").alias("total_views")
                ) \
                .orderBy("avg_risk_score", ascending=False)
            
            risk_summary.show()
            
            # ANALYSIS 2: PySpark MapReduce - Comment Sentiment Analysis
            logger.info("Analysis 2: PySpark MapReduce - Comment Sentiment Analysis")
            
            comment_sentiment_analysis = comments_df.groupBy("video_id", "sentiment_label") \
                .agg(
                    count("*").alias("comment_count"),
                    avg("sentiment_score").alias("avg_sentiment"),
                    avg("toxicity_score").alias("avg_toxicity")
                ) \
                .withColumn(
                    "sentiment_intensity",
                    when(col("avg_sentiment") > 0.5, "Strongly Positive")
                    .when(col("avg_sentiment") < -0.5, "Strongly Negative")
                    .otherwise("Neutral")
                )
            
            # Reduce: Get top videos by negative sentiment
            top_negative_videos = comment_sentiment_analysis.filter(
                col("sentiment_label") == "negative"
            ).orderBy("avg_sentiment", ascending=True).limit(10)
            
            top_negative_videos.show()
            
            # ANALYSIS 3: PySpark MapReduce - Fake News Patterns
            logger.info("Analysis 3: PySpark MapReduce - Fake News Patterns")
            
            fake_news_patterns = analyses_df.select(
                "video_id",
                "risk_score",
                "fake_news_probability",
                "red_flags",
                "analysis_summary"
            ).withColumn(
                "has_multiple_red_flags",
                col("red_flags").isNotNull() & (col("red_flags").size() > 2)
            ).filter(
                col("fake_news_probability") > 0.5
            )
            
            # Map: Identify common red flags
            pattern_analysis = fake_news_patterns.select(
                col("video_id"),
                col("risk_score"),
                explode(col("red_flags")).alias("red_flag")
            ).groupBy("red_flag") \
                .agg(
                    count("*").alias("occurrence_count"),
                    avg("risk_score").alias("avg_risk_score")
                ) \
                .orderBy("occurrence_count", ascending=False)
            
            pattern_analysis.show()
            
            # Save PySpark analysis results back to MongoDB
            self.save_spark_analysis_results(risk_summary, comment_sentiment_analysis, pattern_analysis)
            
            logger.info("PySpark MapReduce analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Error in PySpark MapReduce analysis: {e}")
            raise
    
    def save_spark_analysis_results(self, risk_summary, comment_sentiment_analysis, pattern_analysis):
        """Save PySpark analysis results to MongoDB using PyMongo"""
        try:
            # Convert Spark DataFrames to Pandas and then to MongoDB documents
            risk_summary_pd = risk_summary.toPandas()
            comment_sentiment_pd = comment_sentiment_analysis.toPandas()
            pattern_analysis_pd = pattern_analysis.toPandas()
            
            # Create analysis summary document using PyMongo
            analysis_summary = {
                "analysis_type": "pyspark_mapreduce_summary",
                "generated_at": datetime.utcnow(),
                "execution_time": datetime.utcnow().isoformat(),
                "risk_summary": risk_summary_pd.to_dict('records'),
                "comment_sentiment_analysis": comment_sentiment_pd.to_dict('records'),
                "fake_news_patterns": pattern_analysis_pd.to_dict('records')
            }
            
            # Insert using PyMongo
            result = self.db.analysis_summaries.insert_one(analysis_summary)
            logger.info(f"Analysis results saved to MongoDB with ID: {result.inserted_id}")
            
        except Exception as e:
            logger.error(f"Error saving PySpark results: {e}")
            raise
    
    def real_time_query_with_pymongo(self):
        """Use PyMongo for real-time queries and aggregations"""
        logger.info("Performing real-time queries with PyMongo...")
        
        # Query 1: Get recent high-risk videos
        recent_high_risk = list(self.collections['analyses'].find({
            "risk_score": {"$gt": 0.7},
            "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}
        }).sort("risk_score", -1).limit(10))
        
        logger.info(f"Found {len(recent_high_risk)} recent high-risk videos")
        
        # Query 2: Get videos with flagged comments
        videos_with_flagged_comments = list(self.collections['comments'].aggregate([
            {"$match": {"flagged": True}},
            {"$group": {
                "_id": "$video_id",
                "flagged_count": {"$sum": 1},
                "total_sentiment_score": {"$sum": "$sentiment_score"}
            }},
            {"$lookup": {
                "from": "videos",
                "localField": "_id",
                "foreignField": "video_id",
                "as": "video_info"
            }},
            {"$limit": 10}
        ]))
        
        logger.info(f"Found {len(videos_with_flagged_comments)} videos with flagged comments")
        
        # Query 3: Get top toxic comments for moderation
        top_toxic_comments = list(self.collections['comments'].find({
            "toxicity_score": {"$gt": 0.8}
        }).sort("toxicity_score", -1).limit(20))
        
        logger.info(f"Found {len(top_toxic_comments)} highly toxic comments")
        
        return {
            "recent_high_risk": recent_high_risk,
            "flagged_videos": videos_with_flagged_comments,
            "toxic_comments": top_toxic_comments
        }
    
    def hybrid_analysis_workflow(self):
        """
        HYBRID WORKFLOW: Combine PyMongo real-time queries with PySpark batch processing
        """
        logger.info("Starting Hybrid Analysis Workflow...")
        
        # Phase 1: Use PyMongo for quick data validation and preparation
        logger.info("Phase 1: PyMongo - Data validation and preparation")
        
        # Check if collections have data
        video_count = self.collections['videos'].count_documents({})
        comment_count = self.collections['comments'].count_documents({})
        
        if video_count == 0 or comment_count == 0:
            logger.warning("No data found. Please load data first.")
            return
        
        logger.info(f"Found {video_count} videos and {comment_count} comments")
        
        # Phase 2: Use PySpark for heavy MapReduce analysis
        logger.info("Phase 2: PySpark - Heavy batch analysis")
        self.process_and_analyze_with_spark()
        
        # Phase 3: Use PyMongo for real-time insights and alerts
        logger.info("Phase 3: PyMongo - Real-time insights and alerts")
        real_time_results = self.real_time_query_with_pymongo()
        
        # Phase 4: Generate alerts using PyMongo
        logger.info("Phase 4: PyMongo - Generating alerts")
        self.generate_alerts(real_time_results)
        
        logger.info("Hybrid Analysis Workflow completed successfully")
    
    def generate_alerts(self, real_time_results: Dict):
        """Generate alerts using PyMongo"""
        alerts = []
        
        # Alert for recent high-risk videos
        for analysis in real_time_results['recent_high_risk']:
            alert = {
                "type": "HIGH_RISK_VIDEO",
                "video_id": analysis.get('video_id'),
                "risk_score": analysis.get('risk_score'),
                "timestamp": datetime.utcnow(),
                "message": f"High risk video detected: {analysis.get('video_id')} with risk score {analysis.get('risk_score'):.2f}"
            }
            alerts.append(alert)
        
        # Alert for flagged comments
        for flagged_video in real_time_results['flagged_videos']:
            alert = {
                "type": "FLAGGED_COMMENTS",
                "video_id": flagged_video['_id'],
                "flagged_count": flagged_video['flagged_count'],
                "timestamp": datetime.utcnow(),
                "message": f"Video {flagged_video['_id']} has {flagged_video['flagged_count']} flagged comments"
            }
            alerts.append(alert)
        
        # Insert alerts using PyMongo
        if alerts:
            self.db.alerts.insert_many(alerts)
            logger.info(f"Generated {len(alerts)} alerts")
    
    def get_data_statistics(self):
        """Get data statistics using PyMongo"""
        stats = {
            "collections": {},
            "total_documents": 0
        }
        
        for name, collection in self.collections.items():
            count = collection.count_documents({})
            stats["collections"][name] = count
            stats["total_documents"] += count
        
        return stats
    
    def cleanup(self):
        """Clean up connections"""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("PyMongo connection closed")
        
        if self.spark:
            self.spark.stop()
            logger.info("PySpark session stopped")

def main():
    """Main function demonstrating the use of both PyMongo and PySpark"""
    manager = DataIngestionManager()
    
    try:
        logger.info("=" * 80)
        logger.info("FAKE NEWS DETECTION SYSTEM - DATA INGESTION & ANALYSIS")
        logger.info("=" * 80)
        
        # Example: Load and insert sample data using PyMongo
        sample_data = [
            {
                "video_id": "dQw4w9WgXcQ",
                "title": "Never Gonna Give You Up",
                "description": "Official music video",
                "channel_title": "RickAstleyVEVO",
                "view_count": 1234567890,
                "like_count": 54321098,
                "comment_count": 98765,
                "added_at": datetime.utcnow()
            }
        ]
        
        # Insert using PyMongo
        manager.bulk_insert_with_pymongo('videos', sample_data)
        
        # Perform hybrid analysis using both PyMongo and PySpark
        manager.hybrid_analysis_workflow()
        
        # Get final statistics
        stats = manager.get_data_statistics()
        logger.info(f"Final data statistics: {stats}")
        
        logger.info("=" * 80)
        logger.info("ANALYSIS COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise
    finally:
        manager.cleanup()

if __name__ == "__main__":
    main()