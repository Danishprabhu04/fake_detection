# YouTube Fake News Detection System 🎥🔍

A comprehensive AI-powered system to analyze YouTube videos and detect fake news content using machine learning models, sentiment analysis, and engagement metrics.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database Structure](#database-structure)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

The YouTube Fake News Detection System is a full-stack application that leverages machine learning to analyze YouTube videos and determine their authenticity. It examines multiple factors including:

- **Video Metadata**: Views, likes, upload date, category
- **Content Analysis**: ML model predictions on video title and description
- **Sentiment Analysis**: Analysis of YouTube comments
- **Thumbnail Analysis**: Visual authenticity scoring
- **Risk Assessment**: Comprehensive risk level determination

## ✨ Features

### Backend Features
- ✅ User authentication with JWT tokens
- ✅ Trained RandomForestClassifier ML model for fake news detection
- ✅ Real-time YouTube API integration
- ✅ Sentiment analysis from YouTube comments
- ✅ Comprehensive video analysis pipeline
- ✅ Report generation and storage
- ✅ Alert creation for fake content detection
- ✅ MongoDB database for persistent storage
- ✅ RESTful API with async/await support
- ✅ CORS support for frontend integration

### Frontend Features
- ✅ User-friendly React interface
- ✅ Real-time video analysis
- ✅ Beautiful responsive design with Tailwind CSS
- ✅ Interactive analysis results visualization
- ✅ Report generation and download
- ✅ User authentication with JWT
- ✅ Protected routes and pages
- ✅ Toast notifications for user feedback
- ✅ Mobile-responsive UI

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React + Vite)                   │
│                  (localhost:5173)                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   SignIn     │  │   SignUp     │  │   Analyze    │      │
│  │   Page       │  │   Page       │  │   Page       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                │                    │              │
└─────────┼────────────────┼────────────────────┼──────────────┘
          │                │                    │
          └────────────────┼────────────────────┘
                           │
                    REST API Calls
                    (HTTP/JSON)
                           │
┌─────────────────────────────────────────────────────────────┐
│              Backend (FastAPI)                              │
│              (localhost:8000)                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │            API Routes                             │    │
│  │  ├─ /auth/register (User Registration)           │    │
│  │  ├─ /auth/login (User Authentication)            │    │
│  │  ├─ /video/analyze-url (Video Analysis)          │    │
│  │  ├─ /video/report/generate (Report Generation)   │    │
│  │  └─ /video/alert/create (Alert Creation)         │    │
│  └────────────────────────────────────────────────────┘    │
│                       │                                      │
│  ┌────────────────────┼──────────────────────┐             │
│  │                    │                      │              │
│  ▼                    ▼                      ▼              │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│ │ ML Models    │ │ YouTube API  │ │ Sentiment    │        │
│ │ (Trained)    │ │ Integration  │ │ Analysis     │        │
│ └──────────────┘ └──────────────┘ └──────────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                        │
                MongoDB Database
                   (localhost:27017)
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    ┌────────┐    ┌──────────┐    ┌──────────┐
    │ users  │    │analyses  │    │comments  │
    └────────┘    └──────────┘    └──────────┘
        │               │               │
        ├───────────────┼───────────────┤
        │               │               │
        ▼               ▼               ▼
    ┌────────┐    ┌──────────┐    ┌──────────┐
    │reports │    │ alerts   │    │ videos   │
    └────────┘    └──────────┘    └──────────┘
```

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11, macOS, or Linux
- **Python**: 3.11+
- **Node.js**: 16+
- **MongoDB**: 5.0+
- **Java**: 11+ (for PySpark ML models)

### Required Software
- Git
- npm or pnpm (Node package manager)
- Python virtual environment (venv)

## 🚀 Installation

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Fake_Detection.git
cd Fake_Detection/Backend
```

2. **Create Python virtual environment**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file**
```bash
# Create .env file in Backend directory
MONGODB_URL=mongodb://localhost:27017/fake_news_detection
YOUTUBE_API_KEY=your_youtube_api_key_here
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend Setup

1. **Navigate to Frontend directory**
```bash
cd ../Frontend
```

2. **Install Node dependencies**
```bash
npm install
# or
pnpm install
```

3. **Create `.env.local` file**
```bash
# Create .env.local file in Frontend directory
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## ⚙️ Configuration

### Backend Configuration

**`.env` file variables:**
```
MONGODB_URL              - MongoDB connection string
YOUTUBE_API_KEY          - YouTube Data API v3 key
SECRET_KEY               - JWT secret key (generate with: openssl rand -hex 32)
ALGORITHM                - JWT algorithm (HS256)
ACCESS_TOKEN_EXPIRE_MINUTES - Token expiration time
```

### Frontend Configuration

**`.env.local` file variables:**
```
VITE_API_BASE_URL        - Backend API base URL
```

### MongoDB Setup

1. **Start MongoDB service**
```bash
# Windows
mongod

# macOS (using Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

2. **Create MongoDB indexes**
```bash
# In MongoDB shell
use fake_news_detection

# Create unique index on comment_id
db.comments.createIndex({ comment_id: 1 }, { unique: true })

# Create index on video_id
db.analyses.createIndex({ video_id: 1 })
db.comments.createIndex({ video_id: 1 })
db.reports.createIndex({ video_id: 1 })
db.alerts.createIndex({ video_id: 1 })
```

## 🏃 Running the Application

### Start MongoDB
```bash
# Ensure MongoDB is running on localhost:27017
mongod
```

### Start Backend Server
```bash
cd Backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: **http://localhost:8000**

### Start Frontend Development Server
```bash
cd Frontend
npm run dev
# or
pnpm dev
```

Frontend will be available at: **http://localhost:5173**

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "id": "user_id",
  "username": "john_doe",
  "email": "john@example.com"
}
```

#### Login User
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword123"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

### Video Analysis Endpoints

#### Analyze YouTube Video
```http
POST /api/v1/video/analyze-url
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}

Response: 200 OK
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "channel_title": "Channel Name",
  "fake_probability": 0.35,
  "is_fake": false,
  "analysis_details": {
    "view_count": 1000000,
    "like_count": 50000,
    "comment_count": 10000,
    "published_at": "2023-10-13T14:07:20Z",
    "category": "Entertainment",
    "thumbnail_score": 70,
    "comment_score": 65,
    "sentiment": "Mixed",
    "risk_level": "Low"
  },
  "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/default.jpg",
  "comments_available": true
}
```

#### Generate Report
```http
POST /api/v1/video/report/generate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}

Response: 200 OK
{
  "success": true,
  "report_id": "report_mongodb_id",
  "message": "Report generated and saved successfully"
}
```

#### Create Alert
```http
POST /api/v1/video/alert/create
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "alert_type": "fake_detected",
  "severity": "high"
}

Response: 200 OK
{
  "success": true,
  "alert_id": "alert_mongodb_id",
  "message": "Alert created and saved successfully"
}
```

## 🗄️ Database Structure

### Collections

#### users
```json
{
  "_id": ObjectId,
  "username": "string",
  "email": "string",
  "hashed_password": "string",
  "is_admin": boolean,
  "created_at": timestamp
}
```

#### analyses
```json
{
  "_id": ObjectId,
  "video_id": "string",
  "title": "string",
  "channel_title": "string",
  "fake_probability": number,
  "is_fake": boolean,
  "analysis_details": {
    "view_count": number,
    "like_count": number,
    "comment_count": number,
    "published_at": string,
    "category": string,
    "thumbnail_score": number,
    "comment_score": number,
    "sentiment": "string",
    "risk_level": "string"
  },
  "user_id": "string",
  "analyzed_at": timestamp
}
```

#### comments
```json
{
  "_id": ObjectId,
  "comment_id": "string (unique)",
  "video_id": "string",
  "author": "string",
  "text": "string",
  "likes": number,
  "published_at": timestamp,
  "sentiment": "string",
  "sentiment_score": number,
  "user_id": "string",
  "saved_at": timestamp
}
```

#### reports
```json
{
  "_id": ObjectId,
  "video_id": "string",
  "title": "string",
  "channel": "string",
  "fake_probability": number,
  "is_fake": boolean,
  "user_id": "string",
  "generated_at": timestamp,
  "report_type": "string",
  "report_content": "string"
}
```

#### alerts
```json
{
  "_id": ObjectId,
  "video_id": "string",
  "title": "string",
  "channel": "string",
  "alert_type": "string",
  "severity": "string",
  "fake_probability": number,
  "is_fake": boolean,
  "user_id": "string",
  "created_at": timestamp,
  "alert_message": "string",
  "risk_level": "string",
  "status": "active"
}
```

## 📁 Project Structure

```
Fake_Detection/
├── Backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration settings
│   │   ├── database.py             # MongoDB connection
│   │   ├── middleware/
│   │   │   ├── cors.py            # CORS middleware
│   │   │   ├── error_handler.py   # Error handling
│   │   │   └── rate_limiter.py    # Rate limiting
│   │   ├── models/
│   │   │   ├── user.py            # User data models
│   │   │   ├── video.py           # Video data models
│   │   │   ├── analysis.py        # Analysis data models
│   │   │   ├── comment.py         # Comment data models
│   │   │   └── report.py          # Report data models
│   │   ├── routes/
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── video.py           # Video analysis endpoints
│   │   │   ├── comment.py         # Comment analysis endpoints
│   │   │   ├── report.py          # Report endpoints
│   │   │   ├── analytics.py       # Analytics endpoints
│   │   │   └── admin.py           # Admin endpoints
│   │   ├── services/
│   │   │   ├── youtube_api.py    # YouTube API integration
│   │   │   ├── ml_models.py      # ML model inference
│   │   │   ├── sentiment.py      # Sentiment analysis
│   │   │   ├── preprocessing.py  # Text preprocessing
│   │   │   └── risk_calculator.py# Risk scoring
│   │   ├── scripts/
│   │   │   ├── train_models.py   # Model training
│   │   │   └── setup_models.py   # Model setup
│   │   └── utils/
│   │       ├── auth.py           # Authentication utilities
│   │       ├── validators.py     # Validation functions
│   │       └── logger.py         # Logging configuration
│   ├── .env                       # Environment variables
│   ├── requirements.txt           # Python dependencies
│   └── pyproject.toml             # Python project configuration
│
├── Frontend/
│   ├── src/
│   │   ├── main.tsx              # React entry point
│   │   ├── App.tsx               # Main App component
│   │   ├── pages/
│   │   │   ├── SignIn.tsx        # Login page
│   │   │   ├── SignUp.tsx        # Registration page
│   │   │   ├── Dashboard.tsx     # Dashboard page
│   │   │   └── Analyze.tsx       # Video analysis page
│   │   ├── components/
│   │   │   ├── ProtectedRoute.tsx# Route protection component
│   │   │   └── ui/               # UI components
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx   # Authentication context
│   │   ├── services/
│   │   │   └── api.ts            # API service client
│   │   ├── hooks/
│   │   │   └── use-toast.ts      # Toast notification hook
│   │   └── lib/
│   │       └── utils.ts          # Utility functions
│   ├── .env.local                # Environment variables
│   ├── package.json              # Node.js dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   ├── vite.config.ts            # Vite configuration
│   └── tailwind.config.js        # Tailwind CSS configuration
│
└── README.md                     # This file
```

## 🛠️ Technologies Used

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database
- **Motor** - Async MongoDB driver
- **scikit-learn** - Machine learning library
- **PySpark** - Distributed computing
- **NLTK** - Natural language processing
- **OpenCV** - Computer vision
- **pytesseract** - OCR (Optical Character Recognition)
- **python-jose** - JWT token handling
- **bcrypt** - Password hashing
- **pydantic** - Data validation

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **lucide-react** - Icons
- **React Router** - Routing
- **Axios** - HTTP client

### Infrastructure
- **Node.js** - JavaScript runtime
- **Python 3.13** - Programming language
- **Docker** - Containerization (optional)

## 📊 Model Information

### ML Model
- **Type**: RandomForestClassifier
- **Training Data**: Fake news detection dataset
- **Features**: 1000 TF-IDF features
- **Accuracy**: Trained on comprehensive dataset

### Vectorizer
- **Type**: HashingVectorizer
- **Features**: 1000
- **Hash Function**: MD5

## 🔐 Security Features

- ✅ JWT token-based authentication
- ✅ Password hashing with bcrypt
- ✅ CORS protection
- ✅ Rate limiting
- ✅ Input validation with Pydantic
- ✅ Secure environment variables
- ✅ Protected routes and endpoints

## 📝 API Usage Examples

### Complete User Flow

1. **Register User**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure123"
  }'
```

2. **Login User**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure123"
  }'
```

3. **Analyze Video**
```bash
curl -X POST http://localhost:8000/api/v1/video/analyze-url \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'
```

4. **Generate Report**
```bash
curl -X POST http://localhost:8000/api/v1/video/report/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'
```

## 🐛 Troubleshooting

### Common Issues

**MongoDB Connection Error**
- Ensure MongoDB is running: `mongod`
- Check MONGODB_URL in `.env`
- Verify connection string format

**YouTube API Key Error**
- Get API key from [Google Cloud Console](https://console.cloud.google.com)
- Enable YouTube Data API v3
- Add key to `.env` file

**Port Already in Use**
- Change port in backend: `--port 8001`
- Change port in frontend: `vite --port 5174`

**Module Not Found**
- Reinstall dependencies: `pip install -r requirements.txt`
- Clear cache: `rm -rf .venv && python -m venv .venv`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request
