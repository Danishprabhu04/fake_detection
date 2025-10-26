# YouTube Fake Content Detection System

A robust system for detecting fake or misleading content on YouTube using ML/AI techniques, data analysis, and natural language processing.

## Project Overview

This system analyzes YouTube videos and their associated metadata to detect potentially fake or misleading content using:
- Video metadata analysis
- Comment sentiment analysis
- Category-based risk assessment
- Historical pattern detection
- Regional trend analysis

## Prerequisites

- Python 3.8+
- MongoDB
- Apache Spark
- YouTube Data API key
- 4GB+ RAM for model training
- uv package manager

## Project Structure

```
backend/
├── app/
│   ├── middleware/     # Request processing middleware
│   ├── models/        # Database models and schemas
│   ├── routes/        # API endpoints
│   ├── scripts/       # Data ingestion and setup scripts
│   ├── services/      # Business logic and ML services
│   ├── utils/         # Helper functions and utilities
│   └── tests/         # Unit and integration tests
├── data/
│   ├── downloads/     # Downloaded content
│   └── models/        # Trained ML models
└── logs/             # Application logs
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube_fake_detection.git
cd youtube_fake_detection/backend
```

2. Create and activate virtual environment:

```bash
uv init
uv pip install --upgrade pip

# Install individual packages
uv add fastapi uvicorn[standard] pymongo python-dotenv
uv add pydantic pydantic-settings
uv add passlib[bcrypt] python-jose[cryptography]
uv add python-multipart requests pyspark
uv add numpy pandas scikit-learn
uv add textblob nltk beautifulsoup4
uv add pillow tesseract youtube-transcript-api
uv add google-api-python-client google-auth google-auth-oauthlib
uv add pytesseract opencv-python
uv add seaborn matplotlib plotly
uv add wordcloud networkx

# Or install all requirements at once
uv add -r requirements.txt
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration:
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=fake_news_detection
YOUTUBE_API_KEY=your_youtube_api_key_here
SECRET_KEY=your-secret-key-here
```

## Data Pipeline Setup

1. Initialize MongoDB:
```bash
python tester.py mongodb_setup
```

2. Run data ingestion:
```bash
python tester.py data_ingestion
```

3. Train models (choose one based on your system):

Standard training:
```bash
python tester.py train_models
```

For systems with limited memory (2GB RAM):
```bash
python -X maxsize=2048MB tester.py train_models
```

With specific memory and optimization flags:
```bash
PYTHONMEM=2G SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True python tester.py train_models
```

## Starting the API Server

1. Development server:
```bash
uvicorn app.main:app --reload
```

2. Production server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Usage Examples

1. Register a new user:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
}'
```


2. Login and get token:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
-H "Content-Type: application/json" \
-d '{
    "username": "testuser",
    "password": "securepassword123"
}'
```

3. Analyze YouTube video:
```bash
curl -X POST "http://localhost:8000/api/v1/video/analyze-url" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}'
```

## Model Training Details

The system uses multiple models:
- Text Classification (Fake News Detection)
- Sentiment Analysis
- Comment Toxicity Detection
- Thumbnail Analysis

Training configurations:
- Batch size: 1000
- Max features: 1000
- Memory limit: 2048MB (configurable)
- Optimization: HashingVectorizer for memory efficiency

## Package Management with uv

Update dependencies:
```bash
uv pip freeze > requirements.txt  # Update requirements.txt
uv pip install -r requirements.txt --upgrade  # Upgrade all packages
```

Install new package:
```bash
uv add package_name
```

Remove package:
```bash
uv pip uninstall package_name
```

## Monitoring and Maintenance

1. Check model status:
```bash
python tester.py check_models
```

2. View MongoDB statistics:
```bash
mongosh
use fake_news_detection
db.stats()
```

3. View application logs:
```bash
tail -f logs/api.log
```

## Troubleshooting

1. If models fail to load:
```bash
python -m app.scripts.train_models --force
```

2. Reset database:
```bash
python -m app.scripts.mongodb_setup --reset
```

3. Clear model cache:
```bash
rm -rf data/models/*
python tester.py train_models
```

4. Memory issues during training:
```bash
# Reduce batch size
BATCH_SIZE=500 python tester.py train_models

# Limit memory usage
python -X maxsize=2048MB tester.py train_models
```

5. Package management issues:
```bash
# Reset virtual environment
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Your Name - Initial work - [YourGithub](https://github.com/yourusername)

## Acknowledgments

- YouTube Data API
- MongoDB Team
- FastAPI Community
- Astral (uv package manager)