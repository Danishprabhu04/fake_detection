// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Types for API requests and responses
export interface VideoAnalysisRequest {
  url: string;
}

export interface VideoAnalysisResponse {
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

export interface AuthRequest {
  email: string;
  password: string;
  name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: {
    id: string;
    name: string;
    email: string;
  };
}

export interface TrendingVideo {
  videoId: string;
  title: string;
  views: number;
  riskScore: number;
  category: string;
}

export interface AnalyticsData {
  trends: any[];
  regions: any[];
  categories: any[];
}

// API Service Class
class ApiService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication endpoints (matches backend auth.py routes)
  async register(data: { username: string; email: string; password: string }): Promise<any> {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data: { username: string; password: string }): Promise<any> {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCurrentUser(): Promise<any> {
    return this.request('/auth/me');
  }

  // Video Analysis endpoints (matches backend video.py routes)
  async analyzeVideoUrl(url: string): Promise<any> {
    return this.request('/video/analyze-url', {
      method: 'POST',
      body: JSON.stringify({ url }),
    });
  }

  async addVideo(videoId: string): Promise<any> {
    return this.request('/video', {
      method: 'POST',
      body: JSON.stringify({ video_id: videoId }),
    });
  }

  async getVideo(videoId: string): Promise<any> {
    return this.request(`/video/${videoId}`);
  }

  async getVideos(skip: number = 0, limit: number = 50, search?: string): Promise<any> {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (search) params.append('search', search);
    
    return this.request(`/video?${params.toString()}`);
  }

  async analyzeVideo(videoId: string, analysisType: string = 'comprehensive'): Promise<any> {
    return this.request(`/video/${videoId}/analyze`, {
      method: 'POST',
      body: JSON.stringify({ analysis_type: analysisType }),
    });
  }

  async getVideoAnalysis(videoId: string): Promise<any> {
    return this.request(`/video/${videoId}/analysis`);
  }

  async generateReport(url: string): Promise<any> {
    return this.request('/video/report/generate', {
      method: 'POST',
      body: JSON.stringify({ url }),
    });
  }

  async createAlert(url: string, alertType: string = 'fake_detected', severity: string = 'medium'): Promise<any> {
    return this.request('/video/alert/create', {
      method: 'POST',
      body: JSON.stringify({ url, alert_type: alertType, severity }),
    });
  }

  // Comment Analysis endpoints (matches backend comment.py routes)
  async analyzeComment(commentText: string, videoId: string): Promise<any> {
    return this.request('/comment/analyze', {
      method: 'POST',
      body: JSON.stringify({ text: commentText, video_id: videoId }),
    });
  }

  async getComments(videoId: string, skip: number = 0, limit: number = 50): Promise<any> {
    const params = new URLSearchParams();
    params.append('video_id', videoId);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    
    return this.request(`/comment?${params.toString()}`);
  }

  // Report endpoints (matches backend report.py routes)
  async createReport(data: any): Promise<any> {
    return this.request('/report', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getReports(skip: number = 0, limit: number = 50): Promise<any> {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    
    return this.request(`/report?${params.toString()}`);
  }

  async getReport(reportId: string): Promise<any> {
    return this.request(`/report/${reportId}`);
  }

  // Analytics endpoints (matches backend analytics.py routes)
  async getAnalytics(): Promise<any> {
    return this.request('/analytics');
  }

  async getTrends(): Promise<any> {
    return this.request('/analytics/trends');
  }

  async getRegionalStats(): Promise<any> {
    return this.request('/analytics/regions');
  }

  async getCategoryStats(): Promise<any> {
    return this.request('/analytics/categories');
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Mock service for development (your friend can use this for testing)
export const mockApiService = {
  async analyzeVideo(data: VideoAnalysisRequest): Promise<VideoAnalysisResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    return {
      videoId: 'dQw4w9WgXcQ',
      title: 'Sample YouTube Video Analysis',
      thumbnail: 'https://images.pexels.com/photos/1535162/pexels-photo-1535162.jpeg?auto=compress&cs=tinysrgb&w=400',
      isFake: Math.random() > 0.5,
      confidence: Math.floor(Math.random() * 30) + 70,
      thumbnailAnalysis: {
        score: Math.floor(Math.random() * 40) + 60,
        flags: ['Clickbait elements detected', 'Authentic visual composition'],
      },
      commentsAnalysis: {
        score: Math.floor(Math.random() * 40) + 60,
        sentiment: 'Mixed',
        totalComments: Math.floor(Math.random() * 10000) + 1000,
      },
      metadata: {
        views: Math.floor(Math.random() * 10000000) + 100000,
        likes: Math.floor(Math.random() * 100000) + 1000,
        uploadDate: '2024-01-15',
        category: 'Science & Technology',
      },
    };
  },

  async login(data: Omit<AuthRequest, 'name'>): Promise<AuthResponse> {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return {
      access_token: 'mock_access_token',
      refresh_token: 'mock_refresh_token',
      user: {
        id: '1',
        name: data.email.split('@')[0],
        email: data.email,
      },
    };
  },

  async register(data: AuthRequest): Promise<AuthResponse> {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return {
      access_token: 'mock_access_token',
      refresh_token: 'mock_refresh_token',
      user: {
        id: '1',
        name: data.name || 'Test User',
        email: data.email,
      },
    };
  },
};