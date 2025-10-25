from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from app.services.youtube_api import YouTubeAPIService, YouTubeAnalyzer
from app.services.ml_models import analyze_video, predict_fake_news
from app.database import get_database
from app.utils.auth import get_current_user
from app.models.user import User
import logging
import re
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

class VideoCreate(BaseModel):
    video_id: str

class VideoResponse(BaseModel):
    video_id: str
    title: str
    description: str
    channel_title: str
    publish_date: str
    duration: str
    view_count: int
    like_count: int
    dislike_count: int
    comment_count: int
    thumbnail_url: str
    tags: List[str]
    category: str
    language: str
    added_at: str
    updated_at: str

class AnalysisCreate(BaseModel):
    analysis_type: str

class AnalysisResponse(BaseModel):
    video_id: str
    risk_score: float
    is_fake: bool
    details: Dict[str, Any]

class URLIn(BaseModel):
    url: HttpUrl

class URLAnalysisOut(BaseModel):
    status: str
    video_id: str
    title: str
    channel_title: str
    is_fake: bool
    confidence: float
    analyzed_at: str

class VideoUrlInput(BaseModel):
    url: HttpUrl

class VideoAnalysisResponse(BaseModel):
    video_id: str
    title: str
    channel_title: str
    fake_probability: float
    is_fake: bool
    analysis_details: Dict[str, Any]
    thumbnail_url: Optional[str]
    transcript_available: bool
    comments_available: bool

youtube_analyzer = YouTubeAnalyzer()

@router.post("/", response_model=VideoResponse)
async def add_video(
    video_data: VideoCreate,
    current_user: User = Depends(get_current_user)
):
    """Add a new video for analysis"""
    db = await get_database()
    
    # Get video details from YouTube API
    youtube_service = YouTubeAPIService()
    video_details = await youtube_service.get_video_details(video_data.video_id)
    
    if not video_details:
        raise HTTPException(
            status_code=404,
            detail=f"Video {video_data.video_id} not found on YouTube"
        )
    
    # Create video document
    video_doc = {
        "video_id": video_details["video_id"],
        "title": video_details["title"],
        "description": video_details["description"],
        "channel_title": video_details["channel_title"],
        "publish_date": video_details["publish_date"],
        "duration": video_details["duration"],
        "view_count": video_details["view_count"],
        "like_count": video_details["like_count"],
        "dislike_count": video_details["dislike_count"],
        "comment_count": video_details["comment_count"],
        "thumbnail_url": video_details["thumbnail_url"],
        "tags": video_details["tags"],
        "category": video_details["category"],
        "language": video_details["language"],
        "added_at": video_details["added_at"],
        "updated_at": video_details["updated_at"]
    }
    
    # Insert video
    result = await db.videos.insert_one(video_doc)
    
    # Extract and store comments
    comments = await youtube_service.get_video_comments(video_data.video_id)
    if comments:
        await db.comments.insert_many(comments)
    
    # Update comment count in video document
    await db.videos.update_one(
        {"_id": result.inserted_id},
        {"$set": {"comment_count": len(comments) if comments else 0}}
    )
    
    logger.info(f"Video added: {video_data.video_id}")
    return VideoResponse(**video_doc)

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    """Get video by ID"""
    db = await get_database()
    
    video = await db.videos.find_one({"video_id": video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return VideoResponse(**video)

@router.get("/", response_model=List[VideoResponse])
async def get_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    """Get list of videos with optional search"""
    db = await get_database()
    
    query = {}
    if search:
        query = {"$or": [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]}
    
    videos = await db.videos.find(query).skip(skip).limit(limit).to_list(None)
    
    return [VideoResponse(**video) for video in videos]

@router.post("/{video_id}/analyze", response_model=AnalysisResponse)
async def analyze_video_endpoint(
    video_id: str,
    analysis_data: AnalysisCreate,
    current_user: User = Depends(get_current_user)
):
    """Analyze a video for fake news detection"""
    db = await get_database()
    
    # Check if video exists
    video = await db.videos.find_one({"video_id": video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Perform analysis
    analysis_result = await analyze_video(video_id, analysis_data.analysis_type)
    
    # Store analysis result
    analysis_doc = analysis_result.dict()
    result = await db.analyses.insert_one(analysis_doc)
    
    logger.info(f"Video analyzed: {video_id}, Risk Score: {analysis_result.risk_score}")
    return AnalysisResponse(**analysis_result.dict())

@router.get("/{video_id}/analysis", response_model=AnalysisResponse)
async def get_video_analysis(video_id: str):
    """Get analysis results for a video"""
    db = await get_database()
    
    analysis = await db.analyses.find_one({"video_id": video_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return AnalysisResponse(**analysis)

@router.post("/analyze-url", response_model=VideoAnalysisResponse)
async def analyze_video_url(
    video_input: VideoUrlInput,
    current_user: Dict = Depends(get_current_user)
):
    """Analyze YouTube video for fake content"""
    try:
        # Extract video ID from URL
        url = str(video_input.url)
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:\?|$)"
        match = re.search(pattern, url)
        if not match:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        video_id = match.group(1)
        
        # Get video details
        details = await youtube_service.get_video_details(video_id)
        comments = await youtube_service.get_comments(video_id)
        transcript = await youtube_service.get_transcript(video_id)
        
        # Run prediction
        prediction = predict_fake_news(
            title=details['title'],
            description=details['description'],
            comments=[c['text'] for c in comments]
        )
        
        return {
            "video_id": video_id,
            "title": details['title'],
            "channel_title": details['channel_title'],
            "fake_probability": prediction['probability'],
            "is_fake": prediction['is_fake'],
            "analysis_details": {
                "view_count": details['view_count'],
                "like_count": details['like_count'],
                "comment_count": details['comment_count'],
                "published_at": details['published_at'],
                "risk_level": "High" if prediction['probability'] > 0.7 
                             else "Medium" if prediction['probability'] > 0.3 
                             else "Low"
            },
            "thumbnail_url": details['thumbnail_url'],
            "transcript_available": bool(transcript),
            "comments_available": bool(comments)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))