from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
from pathlib import Path
import logging

from app.routes import auth, video, comment, report, admin, analytics
from app.database import init_db

app = FastAPI(
    title="Fake News Detection API",
    description="API for detecting fake news in YouTube videos and comments",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json"
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML models
try:
    models_dir = Path("data/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_files = {
        'fake_news_detector': 'fake_news_detector.pkl',
        'text_vectorizer': 'text_vectorizer.pkl',
        'feature_columns': 'feature_columns.pkl'
    }
    
    models = {}
    for name, filename in model_files.items():
        file_path = models_dir / filename
        if file_path.exists():
            models[name] = joblib.load(file_path)
            logger.info(f"Loaded {name} from {filename}")
        else:
            logger.warning(f"Model file not found: {filename}")
            
except Exception as e:
    logger.error(f"Error loading models: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await init_db()

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(video.router, prefix="/api/v1/video", tags=["Video Analysis"])
app.include_router(comment.router, prefix="/api/v1/comment", tags=["Comment Analysis"])
app.include_router(report.router, prefix="/api/v1/report", tags=["Reports"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    return {"message": "Fake News Detection API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend-api"}