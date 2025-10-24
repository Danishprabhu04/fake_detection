# YouTube Fake Content Detection System

A robust system for detecting fake or misleading content on YouTube using ML/AI techniques, data analysis, and natural language processing.

## Project Overview

This system analyzes YouTube videos and their associated metadata to detect potentially fake or misleading content using:
- Video metadata analysis
- Comment sentiment analysis
- Category-based risk assessment
- Historical pattern detection
- Regional trend analysis

## Project Structure

```
backend/
├── app/
│   ├── middleware/      # Request processing middleware
│   ├── models/         # Database models and schemas
│   ├── routes/         # API endpoints
│   ├── scripts/        # Data ingestion and setup scripts
│   ├── services/       # Business logic and ML services
│   ├── utils/          # Helper functions and utilities
│   └── tests/          # Unit and integration tests
├── data/              # Processed data and ML models
└── logs/              # Application logs
```

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **ML Framework**: PySpark, scikit-learn
- **Data Processing**: Pandas, NumPy
- **Text Analysis**: NLTK, spaCy

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube_fake_detection.git
cd youtube_fake_detection/backend
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database setup:
```bash
python tester.py mongodb_setup
```

6. Ingest initial data:
```bash
python tester.py data_ingestion
```

## Data Pipeline

1. **Data Ingestion**
   - CSV files processing (video metadata)
   - JSON files processing (category data)
   - Data validation and cleaning
   - MongoDB storage

2. **Data Preprocessing**
   - Text normalization
   - Feature engineering
   - Sentiment analysis
   - Pattern detection

3. **Analysis**
   - Risk score calculation
   - Trend analysis
   - Anomaly detection
   - Regional pattern identification

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token

### Video Analysis
- `POST /api/v1/videos/analyze` - Analyze video content
- `GET /api/v1/videos/{video_id}` - Get video analysis
- `GET /api/v1/videos/trending` - Get trending fake content

### Reports
- `POST /api/v1/reports/create` - Submit content report
- `GET /api/v1/reports/summary` - Get reports summary
- `GET /api/v1/reports/{report_id}` - Get specific report

### Analytics
- `GET /api/v1/analytics/trends` - Get content trends
- `GET /api/v1/analytics/regions` - Get regional statistics
- `GET /api/v1/analytics/categories` - Get category-wise analysis

## Development Workflow

1. **Environment Setup**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Run Tests**
   ```bash
   pytest app/tests/
   ```

## Database Collections

- `{region}_videos` - Video metadata by region
- `{region}_categories` - Category data by region
- `users` - User accounts
- `reports` - User submitted reports
- `analysis_results` - ML analysis results

## Scripts

- `tester.py` - Central script runner
- `data_ingestion.py` - Data import and processing
- `setup_models.py` - ML model initialization
- `mongodb_setup.py` - Database initialization

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