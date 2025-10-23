from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routes import auth, video, comment, report, admin, analytics
from app.middleware.cors import add_cors_middleware
from app.middleware.error_handler import add_error_handlers
from app.middleware.rate_limiter import add_rate_limiting

app = FastAPI(
    title="Fake News Detection API",
    description="API for detecting fake news in YouTube videos and comments",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json"
)

# Add middleware
add_cors_middleware(app)
add_error_handlers(app)
add_rate_limiting(app)

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