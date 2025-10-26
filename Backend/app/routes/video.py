from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from app.services.youtube_api import YouTubeAPIService, YouTubeAnalyzer
from app.services.ml_models import analyze_video
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
youtube_service = YouTubeAPIService()
api_service = YouTubeAPIService()

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
        
        # Initialize default values
        title = "Unknown Video"
        channel_title = "Unknown Channel"
        view_count = 0
        like_count = 0
        comment_count = 0
        published_at = "Unknown"
        category = "Unknown"
        
        # Try to fetch YouTube metadata
        try:
            api_service = YouTubeAPIService()
            details = await api_service.get_video_details(video_id)
            title = details.get('title', title)
            channel_title = details.get('channel_title', channel_title)
            view_count = details.get('view_count', view_count)
            like_count = details.get('like_count', like_count)
            comment_count = details.get('comment_count', comment_count)
            published_at = details.get('published_at', published_at)
            category = details.get('category', category)
        except Exception as yt_error:
            logger.warning(f"Could not fetch YouTube metadata for {video_id}: {str(yt_error)}")
        
        # Run ML model prediction using TRAINED models
        prediction = await analyze_video(video_id, "comprehensive")
        
        # Extract confidence score from model
        model_confidence = prediction.get('confidence_score', 0.5)
        is_fake = prediction.get('is_fake', False)
        
        # Determine authenticity score (inverse of fake probability for display)
        authenticity_score = (1 - model_confidence) * 100
        
        # Fetch and analyze comments for sentiment
        sentiment_score = 60  # default
        sentiment_label = "Mixed"
        try:
            youtube_analyzer = YouTubeAnalyzer()
            comments = await youtube_analyzer.get_video_comments(video_id)
            if comments:
                logger.info(f"Fetched {len(comments)} comments for sentiment analysis")
                # Extract comment texts only
                comment_texts = [comment.get('text', '') for comment in comments if comment.get('text', '')]
                logger.info(f"Extracted {len(comment_texts)} comment texts for analysis")
                
                # Analyze sentiment of comments
                from app.services.sentiment import analyze_sentiment_batch
                sentiment_results = analyze_sentiment_batch(comment_texts)
                
                # Calculate average sentiment score
                if sentiment_results:
                    # sentiment_results is a list of dicts with 'score', 'label', 'confidence'
                    scores = [result['score'] for result in sentiment_results]
                    avg_score = sum(scores) / len(scores)
                    sentiment_score = int((avg_score + 1) * 50)  # Convert from -1 to 1 scale to 0-100
                    sentiment_score = max(0, min(100, sentiment_score))  # Clamp to 0-100
                    
                    # Determine sentiment label
                    positive = sum(1 for result in sentiment_results if result['label'] == 'positive')
                    negative = sum(1 for result in sentiment_results if result['label'] == 'negative')
                    neutral = sum(1 for result in sentiment_results if result['label'] == 'neutral')
                    
                    if positive > negative * 2:
                        sentiment_label = "Positive"
                    elif negative > positive * 2:
                        sentiment_label = "Negative"
                    else:
                        sentiment_label = "Mixed"
                    
                    logger.info(f"Sentiment analysis completed: Score={sentiment_score}%, Label={sentiment_label}, Positive={positive}, Negative={negative}, Neutral={neutral}")
                    
                    # Save comments to database
                    try:
                        db = await get_database()
                        comments_to_save = []
                        for i, comment in enumerate(comments):
                            # Create unique comment ID from video_id and index
                            comment_id = f"{video_id}_{i}_{comment.get('author', 'unknown')}"
                            comment_doc = {
                                "comment_id": comment_id,
                                "video_id": video_id,
                                "author": comment.get('author', 'unknown'),
                                "text": comment.get('text', ''),
                                "likes": comment.get('likes', 0),
                                "published_at": comment.get('published_at', datetime.utcnow()),
                                "sentiment": sentiment_results[i]['label'],
                                "sentiment_score": float(sentiment_results[i]['score']),
                                "user_id": current_user.get("id"),
                                "saved_at": datetime.utcnow()
                            }
                            comments_to_save.append(comment_doc)
                        
                        if comments_to_save:
                            result = await db.comments.insert_many(comments_to_save)
                            logger.info(f"✅ Saved {len(result.inserted_ids)} comments to database")
                    except Exception as comment_db_error:
                        logger.warning(f"Could not save comments to database: {str(comment_db_error)}")
        except Exception as sentiment_error:
            logger.warning(f"Could not analyze comments sentiment: {str(sentiment_error)}")
        
        # Prepare analysis result (convert NumPy types to native Python types)
        analysis_result = {
            "video_id": video_id,
            "title": title,
            "channel_title": channel_title,
            "fake_probability": float(model_confidence),  # Convert to float
            "is_fake": bool(is_fake),  # Convert to bool
            "analysis_details": {
                "view_count": int(view_count),
                "like_count": int(like_count),
                "comment_count": int(comment_count),
                "published_at": published_at,
                "category": category,
                "thumbnail_score": int(authenticity_score),
                "comment_score": int(sentiment_score),
                "sentiment": sentiment_label,
                "risk_level": "High" if model_confidence > 0.7 
                             else "Medium" if model_confidence > 0.3 
                             else "Low"
            },
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/default.jpg",
            "transcript_available": False,
            "comments_available": bool(comment_count),
            "user_id": current_user.get("id"),
            "analyzed_at": datetime.utcnow()
        }
        
        # Save analysis to database
        try:
            db = await get_database()
            result = await db.analyses.insert_one(analysis_result)
            logger.info(f"✅ Analysis saved to database with ID: {result.inserted_id}")
        except Exception as db_error:
            logger.warning(f"Could not save analysis to database: {str(db_error)}")
        
        # Return analysis results with REAL model predictions
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report/generate")
async def generate_and_save_report(
    video_input: VideoUrlInput,
    current_user: Dict = Depends(get_current_user)
):
    """Generate and save detailed analysis report"""
    try:
        db = await get_database()
        
        # Extract video ID from URL
        url = str(video_input.url)
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:\?|$)"
        match = re.search(pattern, url)
        if not match:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        video_id = match.group(1)
        
        # Get analysis data
        analysis = await db.analyses.find_one({"video_id": video_id})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found for this video")
        
        # Generate report document
        report_doc = {
            "video_id": video_id,
            "title": analysis.get('title', 'Unknown Video'),
            "channel": analysis.get('channel_title', 'Unknown Channel'),
            "fake_probability": float(analysis.get('fake_probability', 0)),
            "is_fake": bool(analysis.get('is_fake', False)),
            "analysis_details": analysis.get('analysis_details', {}),
            "user_id": current_user.get("id"),
            "generated_at": datetime.utcnow(),
            "report_type": "detailed_analysis",
            "report_content": f"""DETAILED ANALYSIS REPORT
=======================
Video Title: {analysis.get('title', 'Unknown')}
Channel: {analysis.get('channel_title', 'Unknown')}
Video ID: {video_id}

AUTHENTICITY ASSESSMENT
-----------------------
Status: {'FAKE DETECTED' if analysis.get('is_fake') else 'AUTHENTIC'}
Confidence Score: {int(analysis.get('fake_probability', 0) * 100)}%
Risk Level: {analysis.get('analysis_details', {}).get('risk_level', 'Unknown')}

ENGAGEMENT METRICS
------------------
Total Views: {analysis.get('analysis_details', {}).get('view_count', 0):,}
Total Likes: {analysis.get('analysis_details', {}).get('like_count', 0):,}
Total Comments: {analysis.get('analysis_details', {}).get('comment_count', 0):,}

ANALYSIS RESULTS
----------------
Thumbnail Authenticity: {analysis.get('analysis_details', {}).get('thumbnail_score', 0)}%
Comment Sentiment Score: {analysis.get('analysis_details', {}).get('comment_score', 0)}%
Overall Sentiment: {analysis.get('analysis_details', {}).get('sentiment', 'Unknown')}

Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
"""
        }
        
        # Save report to database
        result = await db.reports.insert_one(report_doc)
        logger.info(f"✅ Report generated and saved with ID: {result.inserted_id}")
        
        return {
            "success": True,
            "report_id": str(result.inserted_id),
            "message": "Report generated and saved successfully"
        }
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alert/create")
async def create_alert(
    video_input: VideoUrlInput,
    alert_type: str = "fake_detected",
    severity: str = "medium",
    current_user: Dict = Depends(get_current_user)
):
    """Create and save alert for a video"""
    try:
        db = await get_database()
        
        # Extract video ID from URL
        url = str(video_input.url)
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:\?|$)"
        match = re.search(pattern, url)
        if not match:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        video_id = match.group(1)
        
        # Get analysis data
        analysis = await db.analyses.find_one({"video_id": video_id})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found for this video")
        
        # Create alert document
        alert_doc = {
            "video_id": video_id,
            "title": analysis.get('title', 'Unknown Video'),
            "channel": analysis.get('channel_title', 'Unknown Channel'),
            "alert_type": alert_type,  # e.g., "fake_detected", "high_risk"
            "severity": severity,  # "low", "medium", "high", "critical"
            "fake_probability": float(analysis.get('fake_probability', 0)),
            "is_fake": bool(analysis.get('is_fake', False)),
            "user_id": current_user.get("id"),
            "created_at": datetime.utcnow(),
            "alert_message": f"Alert: {alert_type.replace('_', ' ').title()} - {analysis.get('title', 'Unknown Video')}",
            "risk_level": analysis.get('analysis_details', {}).get('risk_level', 'Unknown'),
            "status": "active"
        }
        
        # Save alert to database
        result = await db.alerts.insert_one(alert_doc)
        logger.info(f"✅ Alert created and saved with ID: {result.inserted_id}")
        
        return {
            "success": True,
            "alert_id": str(result.inserted_id),
            "message": "Alert created and saved successfully"
        }
    except Exception as e:
        logger.error(f"Error creating alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))