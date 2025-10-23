from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.database import get_database
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/dashboard")
async def get_dashboard_analytics():
    """Get dashboard analytics"""
    db = await get_database()
    
    # Get basic statistics
    total_videos = await db.videos.count_documents({})
    total_comments = await db.comments.count_documents({})
    total_analyses = await db.analyses.count_documents({})
    
    # Get risk distribution
    risk_pipeline = [
        {
            "$group": {
                "_id": {
                    "$switch": {
                        "branches": [
                            {"case": {"$gte": ["$risk_score", 0.7]}, "then": "High Risk"},
                            {"case": {"$gte": ["$risk_score", 0.4]}, "then": "Medium Risk"},
                            {"case": {"$gte": ["$risk_score", 0.0]}, "then": "Low Risk"}
                        ]
                    }
                },
                "count": {"$sum": 1}
            }
        }
    ]
    
    risk_distribution = await db.analyses.aggregate(risk_pipeline).to_list(None)
    
    # Get recent analyses
    recent_analyses = await db.analyses.find({}).sort("created_at", -1).limit(5).to_list(None)
    
    analytics = {
        "total_videos": total_videos,
        "total_comments": total_comments,
        "total_analyses": total_analyses,
        "risk_distribution": risk_distribution,
        "recent_analyses": recent_analyses,
        "last_updated": "2023-01-01T00:00:00Z"  # This would be dynamic in real implementation
    }
    
    return analytics

@router.get("/sentiment-overview")
async def get_sentiment_overview():
    """Get sentiment analysis overview"""
    db = await get_database()
    
    # Aggregate sentiment data from comments
    sentiment_pipeline = [
        {
            "$group": {
                "_id": "$sentiment_label",
                "count": {"$sum": 1},
                "avg_score": {"$avg": "$sentiment_score"}
            }
        }
    ]
    
    sentiment_data = await db.comments.aggregate(sentiment_pipeline).to_list(None)
    
    return {
        "sentiment_distribution": sentiment_data,
        "total_analyzed_comments": await db.comments.count_documents({"sentiment_score": {"$exists": True}})
    }