from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.models.user import User
from app.models.video import Video
from app.models.comment import Comment
from app.models.analysis import AnalysisResult
from app.models.report import Report
import logging

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient = None
db = None

async def get_database():
    """Get database instance"""
    return db

async def init_db():
    """Initialize database connection and create indexes"""
    global client, db
    
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.mongodb_database]
        
        # Create indexes
        await create_indexes()
        
        logger.info(f"Connected to MongoDB: {settings.mongodb_database}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def create_indexes():
    """Create database indexes for better performance"""
    # User indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)
    
    # Video indexes
    await db.videos.create_index("video_id", unique=True)
    await db.videos.create_index("created_at")
    await db.videos.create_index([("title", "text"), ("description", "text")])
    
    # Comment indexes
    await db.comments.create_index("video_id")
    await db.comments.create_index("author")
    await db.comments.create_index("created_at")
    
    # Analysis indexes
    await db.analyses.create_index("video_id")
    await db.analyses.create_index("created_at")
    
    # Report indexes
    await db.reports.create_index("video_id")
    await db.reports.create_index("created_at")
    
    logger.info("Database indexes created successfully")

async def close_db():
    """Close database connection"""
    global client
    if client:
        client.close()