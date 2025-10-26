# Backend API Integration Guide

This frontend is ready for backend API integration. Your backend endpoints are already mapped and the frontend just needs to be connected.

## 🚀 Quick Integration Steps

### 1. Environment Setup

Create a `.env` file in the Frontend directory:

```env
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1

# Environment
REACT_APP_ENV=production

# Set to false when connecting to real API
REACT_APP_USE_MOCK_API=false
```

### 2. Backend API Mapping

Based on your backend README, here's how the frontend maps to your API endpoints:

#### ✅ Authentication Endpoints
| Frontend Method | Backend Endpoint | Status |
|----------------|------------------|--------|
| `apiService.register()` | `POST /api/v1/auth/register` | Ready |
| `apiService.login()` | `POST /api/v1/auth/login` | Ready |
| `apiService.refreshToken()` | `POST /api/v1/auth/refresh` | Ready |

#### ✅ Video Analysis Endpoints
| Frontend Method | Backend Endpoint | Status |
|----------------|------------------|--------|
| `apiService.analyzeVideo()` | `POST /api/v1/videos/analyze` | Ready |
| `apiService.getVideoAnalysis()` | `GET /api/v1/videos/{video_id}` | Ready |
| `apiService.getTrendingFakeContent()` | `GET /api/v1/videos/trending` | Ready |

#### ✅ Reports Endpoints
| Frontend Method | Backend Endpoint | Status |
|----------------|------------------|--------|
| `apiService.createReport()` | `POST /api/v1/reports/create` | Ready |
| `apiService.getReportsSummary()` | `GET /api/v1/reports/summary` | Ready |
| `apiService.getReport()` | `GET /api/v1/reports/{report_id}` | Ready |

#### ✅ Analytics Endpoints
| Frontend Method | Backend Endpoint | Status |
|----------------|------------------|--------|
| `apiService.getContentTrends()` | `GET /api/v1/analytics/trends` | Ready |
| `apiService.getRegionalStatistics()` | `GET /api/v1/analytics/regions` | Ready |
| `apiService.getCategoryAnalysis()` | `GET /api/v1/analytics/categories` | Ready |

## 📋 Expected Request/Response Formats

### Video Analysis Request
```typescript
{
  url: string; // YouTube video URL
}
```

### Video Analysis Response
```typescript
{
  videoId: string;
  title: string;
  thumbnail: string;
  isFake: boolean;
  confidence: number;
  thumbnailAnalysis: {
    score: number;
    flags: string[];
  };
  commentsAnalysis: {
    score: number;
    sentiment: string;
    totalComments: number;
  };
  metadata: {
    views: number;
    likes: number;
    uploadDate: string;
    category: string;
  };
}
```

### Authentication Request
```typescript
// Login
{
  email: string;
  password: string;
}

// Register
{
  name: string;
  email: string;
  password: string;
}
```

### Authentication Response
```typescript
{
  access_token: string;
  refresh_token: string;
  user: {
    id: string;
    name: string;
    email: string;
  };
}
```

## 🔧 Integration Instructions

### Step 1: Update Environment Variables
1. Copy `.env.example` to `.env`
2. Set `REACT_APP_API_BASE_URL` to your backend URL
3. Set `REACT_APP_USE_MOCK_API=false`

### Step 2: Update Components to Use API Service

The following components are already set up but need the API service imported and used:

#### Update `src/contexts/AuthContext.tsx`:
```typescript
import { apiService } from '@/services/api';

// In login method:
const response = await apiService.login({ email, password });
```

#### Update `src/pages/Analyze.tsx`:
```typescript
import { apiService, VideoAnalysisRequest } from '@/services/api';

// In handleAnalyze method:
const requestData: VideoAnalysisRequest = { url: youtubeUrl };
const result = await apiService.analyzeVideo(requestData);
```

### Step 3: Test the Integration

1. Start your backend server: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Test authentication (Sign In/Sign Up)
4. Test video analysis
5. Check browser console for any errors

## 🛠️ Current Frontend Features

### ✅ Implemented & Ready
- **Authentication System**: Complete login/signup with token management
- **Video Analysis**: Full UI with input validation and results display
- **Report Generation**: Download detailed reports as text files
- **Responsive Design**: Works on all devices (mobile, tablet, desktop)
- **Error Handling**: Proper error messages and loading states
- **Professional UI**: Modern design with shadcn/ui components

### 🔄 Ready for Backend Connection
- **Dashboard Analytics**: Connect to your analytics endpoints
- **Trending Videos**: Display trending fake content from your API
- **User Reports**: Submit and view reports using your reports API
- **Regional Statistics**: Show data from your regional analytics

## 🎯 What's Already Working

- ✅ **Mock API**: Everything works with fake data
- ✅ **UI Components**: All pages are complete and responsive
- ✅ **Routing**: Navigation between pages
- ✅ **State Management**: User authentication state
- ✅ **Form Validation**: Input validation and error handling
- ✅ **File Downloads**: Report generation feature

## 🚦 Testing Checklist

After connecting the real API, test these features:

- [ ] User registration with email/password
- [ ] User login with valid credentials
- [ ] Token refresh when expired
- [ ] Video URL analysis with valid YouTube URLs
- [ ] Error handling for invalid URLs
- [ ] Analysis results display
- [ ] Report download functionality
- [ ] Logout functionality
- [ ] Navigation between pages

## 🔍 Debugging Tips

1. **Check Browser Console**: Look for network errors
2. **Check Network Tab**: Verify API requests are being sent
3. **Verify CORS**: Make sure backend allows frontend origin
4. **Check Response Format**: Ensure backend returns expected JSON structure
5. **Token Issues**: Check if tokens are being stored/sent correctly

## 📞 Support

If you encounter any issues:
1. Check the browser console for errors
2. Verify the API endpoints match exactly
3. Ensure response formats match the TypeScript interfaces
4. Check CORS configuration on backend

The frontend is production-ready and just needs the API endpoints connected. All error handling, loading states, and user feedback are already implemented!