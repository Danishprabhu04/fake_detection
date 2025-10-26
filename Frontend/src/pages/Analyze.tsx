import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield,
  LogOut,
  Search,
  Loader2,
  CheckCircle2,
  XCircle,
  MessageSquare,
  Image as ImageIcon,
  Info,
  FileText,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/services/api';

interface AnalysisResult {
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

export const Analyze = () => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleLogout = () => {
    logout();
    navigate('/signin');
  };

  const validateYoutubeUrl = (url: string) => {
    const youtubeRegex =
      /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[\w-]{11}/;
    return youtubeRegex.test(url);
  };

  const handleAnalyze = async () => {
    if (!youtubeUrl) {
      toast({
        title: 'Error',
        description: 'Please enter a YouTube URL',
        variant: 'destructive',
      });
      return;
    }

    if (!validateYoutubeUrl(youtubeUrl)) {
      toast({
        title: 'Error',
        description: 'Please enter a valid YouTube URL',
        variant: 'destructive',
      });
      return;
    }

    setIsAnalyzing(true);

    try {
      // Call actual backend API
      const result = await apiService.analyzeVideoUrl(youtubeUrl);
      
      // Transform backend response to match frontend interface
      const analysisResult: AnalysisResult = {
        videoId: result.video_id,
        title: result.title,
        thumbnail: result.thumbnail_url || 'https://images.pexels.com/photos/1535162/pexels-photo-1535162.jpeg?auto=compress&cs=tinysrgb&w=400',
        isFake: result.is_fake,
        confidence: Math.round(result.fake_probability * 100),
        thumbnailAnalysis: {
          score: result.analysis_details?.thumbnail_score || 65,
          flags: result.analysis_details?.flags || ['Analysis in progress'],
        },
        commentsAnalysis: {
          score: result.analysis_details?.comment_score || 60,
          sentiment: result.analysis_details?.sentiment || 'Mixed',
          totalComments: result.analysis_details?.comment_count || 0,
        },
        metadata: {
          views: result.analysis_details?.view_count || 0,
          likes: result.analysis_details?.like_count || 0,
          uploadDate: result.analysis_details?.published_at || new Date().toISOString(),
          category: result.analysis_details?.category || 'Unknown',
        },
      };

      setAnalysisResult(analysisResult);
      
      toast({
        title: 'Analysis Complete',
        description: 'Video analysis has been completed successfully',
      });
    } catch (error) {
      console.error('Analysis failed:', error);
      toast({
        title: 'Analysis Failed',
        description: error instanceof Error ? error.message : 'Failed to analyze video. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!analysisResult || !youtubeUrl) return;

    try {
      // Save report to database
      await apiService.generateReport(youtubeUrl);
      
      // Create alert if video is fake
      if (analysisResult.isFake) {
        await apiService.createAlert(
          youtubeUrl,
          'fake_detected',
          analysisResult.confidence > 80 ? 'critical' : 'high'
        );
      }

      // Create detailed report content for download
      const reportContent = `
FAKE DETECTION SYSTEM - ANALYSIS REPORT
=====================================

Generated on: ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}

VIDEO INFORMATION
-----------------
Title: ${analysisResult.title}
Video ID: ${analysisResult.videoId}
Upload Date: ${analysisResult.metadata.uploadDate}
Category: ${analysisResult.metadata.category}

AUTHENTICITY ASSESSMENT
-----------------------
Status: ${analysisResult.isFake ? 'FAKE DETECTED' : 'AUTHENTIC'}
Overall Confidence: ${analysisResult.confidence}%
Confidence Level: ${analysisResult.confidence >= 80 ? 'High' : analysisResult.confidence >= 60 ? 'Medium' : 'Low'}

ENGAGEMENT METRICS
------------------
Total Views: ${analysisResult.metadata.views.toLocaleString()}
Total Likes: ${analysisResult.metadata.likes.toLocaleString()}
Total Comments: ${analysisResult.commentsAnalysis.totalComments.toLocaleString()}

THUMBNAIL ANALYSIS
------------------
Authenticity Score: ${analysisResult.thumbnailAnalysis.score}%
Analysis Findings:
${analysisResult.thumbnailAnalysis.flags.map(flag => `• ${flag}`).join('\n')}

COMMENTS ANALYSIS
-----------------
Sentiment Score: ${analysisResult.commentsAnalysis.score}%
Overall Sentiment: ${analysisResult.commentsAnalysis.sentiment}

SUMMARY
-------
This analysis was performed using advanced AI algorithms that examine multiple factors including video metadata, engagement patterns, comment sentiment, and visual elements. The confidence score reflects the system's certainty in the authenticity assessment based on these combined factors.

Note: This report is generated by an automated system and should be used as part of a comprehensive evaluation process.

---
Generated by Fake Detection System
© 2025 All rights reserved.
    `;

    // Create and download the file
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `fake-detection-report-${analysisResult.videoId}-${Date.now()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

      toast({
        title: 'Report Generated & Saved',
        description: 'Report has been saved to database and downloaded successfully',
      });
    } catch (error) {
      console.error('Report generation failed:', error);
      toast({
        title: 'Report Generation Error',
        description: error instanceof Error ? error.message : 'Failed to generate report',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <nav className="bg-white border-b border-slate-200 shadow-sm w-full">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-6 xl:px-8">
          <div className="flex justify-between items-center h-14 sm:h-16">
            <div
              className="flex items-center gap-1 sm:gap-2 cursor-pointer"
              onClick={() => navigate('/dashboard')}
            >
              <Shield className="h-6 w-6 sm:h-8 sm:w-8 text-blue-600" />
              <h1 className="text-lg sm:text-xl font-bold text-slate-800 truncate">Fake News Detection</h1>
            </div>
            <div className="flex items-center gap-1 sm:gap-2 md:gap-4">
              <span className="text-xs sm:text-sm text-slate-600 hidden md:block truncate">
                Welcome, {user?.username}
              </span>
              <Button variant="outline" onClick={handleLogout} className="gap-1 sm:gap-2 text-xs sm:text-sm px-2 sm:px-4 h-8 sm:h-10">
                <LogOut className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">Logout</span>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 xl:px-10 py-8 sm:py-12 lg:py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="text-center mb-8 sm:mb-12 lg:mb-16">
            <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 lg:p-10 max-w-4xl mx-auto">
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-4 sm:mb-6">
                YouTube Video Analyzer
              </h2>
              <p className="text-sm sm:text-base lg:text-lg text-slate-600 max-w-3xl mx-auto leading-relaxed">
                Our advanced AI-powered system analyzes YouTube videos to determine their authenticity. We 
                examine video metadata, comment patterns, engagement metrics, and visual elements to provide 
                comprehensive authenticity assessments.
              </p>
            </div>
          </div>

          <Card className="max-w-4xl mx-auto shadow-xl mb-8 sm:mb-12 bg-white border-0">
            <CardHeader className="p-6 sm:p-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-lg">
              <CardTitle className="text-xl sm:text-2xl font-bold text-slate-900 flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Search className="h-5 w-5 sm:h-6 sm:w-6 text-blue-600" />
                </div>
                Video Analysis
              </CardTitle>
              <CardDescription className="text-base sm:text-lg text-slate-600 mt-2">
                Paste the YouTube video link you want to analyze for authenticity
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6 sm:p-8">
              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
                <Input
                  type="text"
                  placeholder="https://www.youtube.com/watch?v=..."
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  className="flex-1 h-12 sm:h-14 text-base sm:text-lg border-2 border-slate-200 focus:border-blue-500 rounded-xl px-4"
                  disabled={isAnalyzing}
                />
                <Button 
                  onClick={handleAnalyze} 
                  disabled={isAnalyzing} 
                  className="gap-2 min-w-32 sm:min-w-40 h-12 sm:h-14 text-base sm:text-lg bg-blue-600 hover:bg-blue-700 rounded-xl px-6 sm:px-8 font-semibold"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="h-4 w-4 sm:h-5 sm:w-5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4 sm:h-5 sm:w-5" />
                      Analyze Video
                    </>
                  )}
                </Button>
              </div>
              {isAnalyzing && (
                <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-200">
                  <div className="flex items-center gap-3 text-blue-700">
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span className="font-medium">Processing your video analysis...</span>
                  </div>
                  <div className="mt-2 text-sm text-blue-600">
                    This may take a few moments while we analyze the video content, metadata, and comments.
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <AnimatePresence>
            {analysisResult && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
                className="max-w-5xl mx-auto space-y-4 sm:space-y-6"
              >
                <Card className="shadow-xl border-0 bg-white">
                  <CardHeader className="p-6 sm:p-8 bg-gradient-to-r from-slate-50 to-blue-50 rounded-t-lg">
                    <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-2xl sm:text-3xl mb-2 font-bold text-slate-900">
                          Analysis Results
                        </CardTitle>
                        <CardDescription className="text-base sm:text-lg text-slate-600 font-medium break-words">
                          {analysisResult.title}
                        </CardDescription>
                      </div>
                      <Badge
                        variant={analysisResult.isFake ? 'destructive' : 'default'}
                        className={`text-lg px-6 py-3 rounded-full font-bold shrink-0 ${
                          analysisResult.isFake 
                            ? 'bg-red-100 text-red-700 border-red-200' 
                            : 'bg-green-100 text-green-700 border-green-200'
                        }`}
                      >
                        {analysisResult.isFake ? (
                          <>
                            <XCircle className="h-5 w-5 mr-2" />
                            FAKE DETECTED
                          </>
                        ) : (
                          <>
                            <CheckCircle2 className="h-5 w-5 mr-2" />
                            AUTHENTIC
                          </>
                        )}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="p-6 sm:p-8">
                    <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-lg font-semibold text-slate-900">Overall Confidence Score</span>
                        <span className="text-2xl font-bold text-blue-600">{analysisResult.confidence}%</span>
                      </div>
                      <Progress 
                        value={analysisResult.confidence} 
                        className="h-4 bg-slate-200"
                      />
                      <div className="mt-3 text-sm text-slate-600">
                        {analysisResult.confidence >= 80 ? 'High confidence' : 
                         analysisResult.confidence >= 60 ? 'Medium confidence' : 'Low confidence'} 
                        {' '}in authenticity assessment
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
                  <Card className="shadow-xl border-0 bg-white">
                    <CardHeader className="p-6 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-t-lg">
                      <CardTitle className="flex items-center gap-3 text-xl font-bold text-slate-900">
                        <div className="p-2 bg-blue-100 rounded-lg">
                          <ImageIcon className="h-5 w-5 text-blue-600" />
                        </div>
                        Thumbnail Analysis
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6 p-6">
                      <img
                        src={analysisResult.thumbnail}
                        alt="Video thumbnail"
                        className="w-full rounded-xl max-h-48 sm:max-h-64 object-cover shadow-lg border border-slate-200"
                      />
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                        <div className="flex justify-between items-center mb-3">
                          <span className="text-base font-semibold text-slate-900">Authenticity Score</span>
                          <span className="text-xl font-bold text-blue-600">
                            {analysisResult.thumbnailAnalysis.score}%
                          </span>
                        </div>
                        <Progress value={analysisResult.thumbnailAnalysis.score} className="h-3 bg-slate-200" />
                      </div>
                      <div className="space-y-3">
                        <h4 className="font-semibold text-slate-900 text-base">Analysis Findings</h4>
                        {analysisResult.thumbnailAnalysis.flags.map((flag, index) => (
                          <div
                            key={index}
                            className="text-sm text-slate-600 flex items-start gap-3 p-3 bg-slate-50 rounded-lg"
                          >
                            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                            {flag}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="shadow-xl border-0 bg-white">
                    <CardHeader className="p-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-t-lg">
                      <CardTitle className="flex items-center gap-3 text-xl font-bold text-slate-900">
                        <div className="p-2 bg-green-100 rounded-lg">
                          <MessageSquare className="h-5 w-5 text-green-600" />
                        </div>
                        Comments Analysis
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6 p-6">
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                        <div className="flex justify-between items-center mb-3">
                          <span className="text-base font-semibold text-slate-900">Sentiment Score</span>
                          <span className="text-xl font-bold text-green-600">
                            {analysisResult.commentsAnalysis.score}%
                          </span>
                        </div>
                        <Progress value={analysisResult.commentsAnalysis.score} className="h-3 bg-slate-200" />
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="bg-gradient-to-r from-slate-50 to-blue-50 p-4 rounded-xl border border-slate-200">
                          <div className="text-sm text-slate-600 mb-2 font-medium">Overall Sentiment</div>
                          <div className="font-bold text-slate-900 text-lg">
                            {analysisResult.commentsAnalysis.sentiment}
                          </div>
                        </div>
                        <div className="bg-gradient-to-r from-slate-50 to-green-50 p-4 rounded-xl border border-slate-200">
                          <div className="text-sm text-slate-600 mb-2 font-medium">Total Comments</div>
                          <div className="font-bold text-slate-900 text-lg">
                            {analysisResult.commentsAnalysis.totalComments.toLocaleString()}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <Card className="shadow-xl border-0 bg-white">
                  <CardHeader className="p-6 bg-gradient-to-r from-orange-50 to-amber-50 rounded-t-lg">
                    <CardTitle className="flex items-center gap-3 text-xl font-bold text-slate-900">
                      <div className="p-2 bg-orange-100 rounded-lg">
                        <Info className="h-5 w-5 text-orange-600" />
                      </div>
                      Video Metadata
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 sm:gap-6">
                      <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-5 rounded-xl border border-blue-200">
                        <div className="text-sm text-slate-600 mb-2 font-medium">Total Views</div>
                        <div className="font-bold text-slate-900 text-xl break-all">
                          {analysisResult.metadata.views.toLocaleString()}
                        </div>
                      </div>
                      <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-5 rounded-xl border border-green-200">
                        <div className="text-sm text-slate-600 mb-2 font-medium">Likes</div>
                        <div className="font-bold text-slate-900 text-xl break-all">
                          {analysisResult.metadata.likes.toLocaleString()}
                        </div>
                      </div>
                      <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-5 rounded-xl border border-purple-200">
                        <div className="text-sm text-slate-600 mb-2 font-medium">Upload Date</div>
                        <div className="font-bold text-slate-900 text-xl">
                          {analysisResult.metadata.uploadDate}
                        </div>
                      </div>
                      <div className="bg-gradient-to-r from-orange-50 to-yellow-50 p-5 rounded-xl border border-orange-200">
                        <div className="text-sm text-slate-600 mb-2 font-medium">Category</div>
                        <div className="font-bold text-slate-900 text-xl break-words">
                          {analysisResult.metadata.category}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <div className="flex justify-center mt-8">
                  <Button
                    size="lg"
                    onClick={handleGenerateReport}
                    className="gap-3 text-lg px-8 py-4 h-auto bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 rounded-xl shadow-lg font-semibold"
                  >
                    <FileText className="h-5 w-5" />
                    Generate Detailed Report
                  </Button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </main>
    </div>
  );
};
