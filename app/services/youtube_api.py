import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings
from app.services.sentiment import analyze_sentiment
from app.services.keyword_detector import detect_keywords

logger = logging.getLogger(__name__)

class YouTubeAPIService:
    def __init__(self):
        self.api_key = settings.youtube_api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    async def get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video details from YouTube API"""
        if not self.api_key:
            logger.error("YouTube API key not configured")
            return None
            
        try:
            url = f"{self.base_url}/videos"
            params = {
                'part': 'snippet,statistics,contentDetails',
                'id': video_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('items'):
                return None
                
            item = data['items'][0]
            snippet = item['snippet']
            statistics = item['statistics']
            content_details = item['contentDetails']
            
            video_details = {
                'video_id': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_title': snippet['channelTitle'],
                'publish_date': datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                'duration': content_details['duration'],
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'dislike_count': int(statistics.get('dislikeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'thumbnail_url': snippet['thumbnails']['high']['url'],
                'tags': snippet.get('tags', []),
                'category': snippet.get('categoryId', ''),
                'language': snippet.get('defaultLanguage', 'en'),
                'added_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            return video_details
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching video details: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    async def get_video_comments(self, video_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get comments for a video"""
        if not self.api_key:
            logger.error("YouTube API key not configured")
            return None
            
        try:
            comments = []
            next_page_token = None
            
            while True:
                url = f"{self.base_url}/commentThreads"
                params = {
                    'part': 'snippet,replies',
                    'videoId': video_id,
                    'maxResults': 100,
                    'key': self.api_key
                }
                
                if next_page_token:
                    params['pageToken'] = next_page_token
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                for item in data.get('items', []):
                    snippet = item['snippet']['topLevelComment']['snippet']
                    
                    comment = {
                        'video_id': video_id,
                        'comment_id': item['id'],
                        'author': snippet['authorDisplayName'],
                        'text': snippet['textDisplay'],
                        'likes': int(snippet.get('likeCount', 0)),
                        'replies': len(item.get('replies', {}).get('comments', [])),
                        'published_at': datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                        'updated_at': datetime.utcnow(),
                        'sentiment_score': None,
                        'sentiment_label': None,
                        'toxicity_score': None,
                        'keywords': [],
                        'flagged': False,
                        'flag_reasons': []
                    }
                    
                    # Analyze sentiment
                    sentiment_result = analyze_sentiment(comment['text'])
                    comment['sentiment_score'] = sentiment_result['score']
                    comment['sentiment_label'] = sentiment_result['label']
                    
                    # Detect keywords
                    keywords = detect_keywords(comment['text'])
                    comment['keywords'] = keywords
                    
                    comments.append(comment)
                
                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break
            
            return comments
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching comments: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    async def get_video_transcript(self, video_id: str) -> Optional[str]:
        """Get video transcript (requires YouTube Transcript API)"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = ' '.join([item['text'] for item in transcript_list])
            
            return transcript
        except Exception as e:
            logger.error(f"Error getting transcript: {e}")
            return None