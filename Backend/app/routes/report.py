from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.report import ReportCreate, ReportResponse
from app.database import get_database
from app.utils.auth import get_current_user
from app.models.user import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=ReportResponse)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new report"""
    db = await get_database()
    
    # Check if video exists
    video = await db.videos.find_one({"video_id": report_data.video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Get analysis for the video
    analysis = await db.analyses.find_one({"video_id": report_data.video_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Create report document
    report_doc = {
        "video_id": report_data.video_id,
        "report_type": report_data.report_type,
        "title": f"Analysis Report - {video['title']}",
        "content": f"Comprehensive analysis of video: {video['title']}",
        "summary": analysis.get('analysis_summary', ''),
        "risk_level": "high" if analysis.get('risk_score', 0) > 0.7 else "medium" if analysis.get('risk_score', 0) > 0.4 else "low",
        "generated_by": str(current_user.id) if current_user else "system",
        "generated_at": datetime.utcnow(),
        "format": report_data.format,
        "data": {
            "analysis": analysis,
            "video_info": video
        }
    }
    
    # Insert report
    result = await db.reports.insert_one(report_doc)
    
    logger.info(f"Report created for video: {report_data.video_id}")
    return ReportResponse(**report_doc)

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    """Get report by ID"""
    db = await get_database()
    
    report = await db.reports.find_one({"_id": ObjectId(report_id)})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return ReportResponse(**report)

@router.get("/video/{video_id}", response_model=List[ReportResponse])
async def get_video_reports(video_id: str):
    """Get all reports for a video"""
    db = await get_database()
    
    reports = await db.reports.find({"video_id": video_id}).to_list(None)
    
    return [ReportResponse(**report) for report in reports]