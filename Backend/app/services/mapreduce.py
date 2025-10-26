from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, sum as spark_sum, when, regexp_replace, lower
from pyspark.sql.functions import explode  # Add this import
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MapReduceService:
    def __init__(self, spark_session: SparkSession):
        self.spark = spark_session
    
    def analyze_video_risk_patterns(self, videos_df, analyses_df):
        """Analyze risk patterns using MapReduce"""
        try:
            # Join videos and analyses
            combined_df = videos_df.join(
                analyses_df,
                videos_df.video_id == analyses_df.video_id,
                "inner"
            ).select(
                videos_df.video_id,
                videos_df.title,
                videos_df.channel_title,
                videos_df.view_count,
                videos_df.like_count,
                analyses_df.risk_score,
                analyses_df.fake_news_probability
            )
            
            # Map: Categorize risk levels
            risk_categorized = combined_df.withColumn(
                "risk_category",
                when(col("risk_score") > 0.7, "High Risk")
                .when(col("risk_score") > 0.4, "Medium Risk")
                .otherwise("Low Risk")
            )
            
            # Reduce: Aggregate by risk category
            risk_summary = risk_categorized.groupBy("risk_category") \
                .agg(
                    count("*").alias("video_count"),
                    avg("risk_score").alias("avg_risk_score"),
                    avg("fake_news_probability").alias("avg_fake_prob"),
                    spark_sum("view_count").alias("total_views")
                ) \
                .orderBy("avg_risk_score", ascending=False)
            
            return risk_summary
            
        except Exception as e:
            logger.error(f"Error in video risk analysis: {e}")
            raise
    
    def analyze_comment_sentiment_patterns(self, comments_df):
        """Analyze comment sentiment patterns using MapReduce"""
        try:
            # Map: Process comment sentiment
            sentiment_analysis = comments_df.groupBy("video_id", "sentiment_label") \
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
            
            return sentiment_analysis
            
        except Exception as e:
            logger.error(f"Error in comment sentiment analysis: {e}")
            raise
    
    def analyze_fake_news_indicators(self, analyses_df):
        """Analyze fake news indicators using MapReduce"""
        try:
            # Filter high-risk analyses
            high_risk_analyses = analyses_df.filter(
                col("fake_news_probability") > 0.5
            )
            
            # Map: Extract red flags
            red_flag_analysis = high_risk_analyses.select(
                "video_id",
                "fake_news_probability",
                explode(col("red_flags")).alias("red_flag")  # Fixed import
            ).groupBy("red_flag") \
                .agg(
                    count("*").alias("occurrence_count"),
                    avg("fake_news_probability").alias("avg_fake_prob")
                ) \
                .orderBy("occurrence_count", ascending=False)
            
            return red_flag_analysis
            
        except Exception as e:
            logger.error(f"Error in fake news indicator analysis: {e}")
            raise

# Helper function to create Spark session
def get_spark_session():
    """Create and return Spark session"""
    from app.config import settings
    
    spark = SparkSession.builder \
        .appName(settings.spark_app_name) \
        .master(settings.spark_master) \
        .config("spark.mongodb.input.uri", f"{settings.mongodb_url}/{settings.mongodb_database}") \
        .config("spark.mongodb.output.uri", f"{settings.mongodb_url}/{settings.mongodb_database}") \
        .getOrCreate()
    
    return spark