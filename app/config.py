from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "fake_news_detection"
    
    # JWT Configuration
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # YouTube API
    youtube_api_key: Optional[str] = None
    
    # Google Cloud Vision API
    google_application_credentials: Optional[str] = None
    
    # Tesseract Path
    tesseract_path: Optional[str] = "/usr/bin/tesseract"
    
    # ML Model Paths
    sentiment_model_path: str = "data/models/sentiment_model.pkl"
    keyword_model_path: str = "data/models/keyword_model.pkl"
    
    # Spark Configuration
    spark_master: str = "local[*]"
    spark_app_name: str = "FakeNewsDetection"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()