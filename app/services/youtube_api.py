import os
import logging
from typing import Dict, List, Any
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from app.config import settings

logger = logging.getLogger(__name__)

class YouTubeAPIService:
    def __init__(self):
        self.api = build('youtube', 'v3', developerKey=settings.youtube_api_key)
        self.download_dir = "data/downloads"
        os.makedirs(self.download_dir, exist_ok=True)

    async def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """Get basic video information"""
        try:
            response = self.api.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()

            if not response.get('items'):
                raise ValueError(f"Video {video_id} not found")

            video = response['items'][0]
            snippet = video['snippet']
            stats = video['statistics']

            return {
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'view_count': int(stats.get('viewCount', 0)),
                'like_count': int(stats.get('likeCount', 0)),
                'comment_count': int(stats.get('commentCount', 0)),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', '')
            }
        except Exception as e:
            logger.error(f"Error fetching video details: {str(e)}")
            raise

class YouTubeAnalyzer:
    def __init__(self):
        self.api_service = YouTubeAPIService()
        self.download_dir = "data/downloads"
        os.makedirs(self.download_dir, exist_ok=True)

    async def analyze_video(self, video_id: str) -> Dict[str, Any]:
        """Analyze a video comprehensively"""
        try:
            # Get basic video details
            details = await self.api_service.get_video_details(video_id)
            
            # Get comments if available
            comments = await self.get_video_comments(video_id)
            
            # Get transcript if available
            transcript = await self.get_video_transcript(video_id)
            
            # Download thumbnail
            thumbnail_path = await self.download_thumbnail(
                video_id, 
                details['thumbnail_url']
            )

            return {
                **details,
                'comments': comments,
                'transcript': transcript,
                'thumbnail_path': thumbnail_path,
                'analysis_metadata': {
                    'has_comments': bool(comments),
                    'has_transcript': bool(transcript),
                    'comment_count': len(comments),
                    'transcript_length': len(transcript) if transcript else 0
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing video: {str(e)}")
            raise

    async def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict]:
        """Fetch video comments"""
        try:
            comments = []
            request = self.api_service.api.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                textFormat="plainText"
            )

            while request and len(comments) < max_results:
                response = request.execute()
                
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'likes': comment['likeCount'],
                        'published_at': comment['publishedAt']
                    })

                request = self.api_service.api.commentThreads().list_next(request, response)

            return comments

        except Exception as e:
            logger.warning(f"Error fetching comments: {str(e)}")
            return []

    async def get_video_transcript(self, video_id: str) -> List[Dict]:
        """Fetch video transcript"""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except Exception as e:
            logger.warning(f"Error fetching transcript: {str(e)}")
            return []

    async def download_thumbnail(self, video_id: str, url: str) -> str:
        """Download thumbnail image"""
        try:
            if not url:
                return ""
                
            file_path = f"{self.download_dir}/{video_id}_thumbnail.jpg"
            response = requests.get(url)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return file_path
        except Exception as e:
            logger.error(f"Error downloading thumbnail: {str(e)}")
            return ""

# Create singleton instances
youtube_service = YouTubeAPIService()
youtube_analyzer = YouTubeAnalyzer()