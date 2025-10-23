from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.models.comment import CommentResponse
from app.models.analysis import AnalysisResponse
from app.database import get_database
from app.utils.auth import get_current_user
from app.models.user import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{video_id}", response_model=List[CommentResponse])
async def get_video_comments(
    video_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sort_by: str = Query("published_at", enum=["published_at", "likes", "sentiment_score"]),
    order: str = Query("desc", enum=["asc", "desc"])
):
    """Get comments for a specific video"""
    db = await get_database()
    
    sort_direction = -1 if order == "desc" else 1
    sort_param = [(sort_by, sort_direction)]
    
    comments = await db.comments.find(
        {"video_id": video_id}
    ).sort(sort_param).skip(skip).limit(limit).to_list(None)
    
    return [CommentResponse(**comment) for comment in comments]

@router.get("/{video_id}/analysis", response_model=AnalysisResponse)
async def get_comment_analysis(video_id: str):
    """Get analysis results for comments of a video"""
    db = await get_database()
    
    analysis = await db.analyses.find_one({
        "video_id": video_id,
        "analysis_type": "comments"
    })
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Comment analysis not found")
    
    return AnalysisResponse(**analysis)

@router.put("/{comment_id}/flag")
async def flag_comment(
    comment_id: str,
    reasons: List[str],
    current_user: User = Depends(get_current_user)
):
    """Flag a comment for review"""
    db = await get_database()
    
    comment = await db.comments.find_one({"comment_id": comment_id})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    await db.comments.update_one(
        {"comment_id": comment_id},
        {
            "$set": {
                "flagged": True,
                "flag_reasons": reasons,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"Comment flagged: {comment_id}, Reasons: {reasons}")
    return {"message": "Comment flagged successfully"}

@router.get("/{video_id}/sentiment-analysis")
async def get_video_sentiment_analysis(video_id: str):
    """Get sentiment analysis summary for video comments"""
    db = await get_database()
    
    # Aggregate sentiment data
    pipeline = [
        {"$match": {"video_id": video_id}},
        {
            "$group": {
                "_id": None,
                "total_comments": {"$sum": 1},
                "positive_count": {
                    "$sum": {"$cond": [{"$eq": ["$sentiment_label", "positive"]}, 1, 0]}
                },
                "negative_count": {
                    "$sum": {"$cond": [{"$eq": ["$sentiment_label", "negative"]}, 1, 0]}
                },
                "neutral_count": {
                    "$sum": {"$cond": [{"$eq": ["$sentiment_label", "neutral"]}, 1, 0]}
                },
                "avg_sentiment_score": {"$avg": "$sentiment_score"},
                "avg_toxicity_score": {"$avg": "$toxicity_score"}
            }
        }
    ]
    
    result = await db.comments.aggregate(pipeline).to_list(None)
    
    if not result:
        return {
            "total_comments": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "avg_sentiment_score": 0.0,
            "avg_toxicity_score": 0.0
        }
    
    return result[0]