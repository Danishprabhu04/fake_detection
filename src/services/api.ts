// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

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

  // Authentication endpoints (matches your backend)
  async register(data: AuthRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data: Omit<AuthRequest, 'name'>): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async refreshToken(): Promise<AuthResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    return this.request<AuthResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  // Video Analysis endpoints (matches your backend)
  async analyzeVideo(data: VideoAnalysisRequest): Promise<VideoAnalysisResponse> {
    return this.request<VideoAnalysisResponse>('/videos/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getVideoAnalysis(videoId: string): Promise<VideoAnalysisResponse> {
    return this.request<VideoAnalysisResponse>(`/videos/${videoId}`);
  }

  async getTrendingFakeContent(): Promise<TrendingVideo[]> {
    return this.request<TrendingVideo[]>('/videos/trending');
  }

  // Reports endpoints (matches your backend)
  async createReport(data: any): Promise<any> {
    return this.request('/reports/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getReportsSummary(): Promise<any> {
    return this.request('/reports/summary');
  }

  async getReport(reportId: string): Promise<any> {
    return this.request(`/reports/${reportId}`);
  }

  // Analytics endpoints (matches your backend)
  async getContentTrends(): Promise<any> {
    return this.request('/analytics/trends');
  }

  async getRegionalStatistics(): Promise<any> {
    return this.request('/analytics/regions');
  }

  async getCategoryAnalysis(): Promise<any> {
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