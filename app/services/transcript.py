from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TranscriptService:
    def __init__(self):
        pass
    
    async def get_video_transcript(self, video_id: str) -> Optional[str]:
        """Get video transcript using YouTube Transcript API"""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = ' '.join([item['text'] for item in transcript_list])
            return transcript
        except Exception as e:
            logger.error(f"Error getting transcript for video {video_id}: {e}")
            return None
    
    def analyze_transcript(self, transcript: str) -> Dict[str, Any]:
        """Analyze transcript content"""
        if not transcript:
            return {
                "sentiment": {"score": 0.0, "label": "neutral"},
                "keywords": [],
                "length": 0,
                "word_count": 0
            }
        
        from app.services.sentiment import analyze_sentiment
        from app.services.keyword_detector import detect_keywords
        
        sentiment = analyze_sentiment(transcript)
        keywords = detect_keywords(transcript)
        
        return {
            "sentiment": sentiment,
            "keywords": keywords,
            "length": len(transcript),
            "word_count": len(transcript.split())
        }

# Global instance
transcript_service = TranscriptService()

async def get_video_transcript(video_id: str) -> Optional[str]:
    """Public function to get video transcript"""
    return await transcript_service.get_video_transcript(video_id)