import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, LogOut, Search, ChevronDown, Brain, MessageSquare, BarChart3, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { useAuth } from '@/contexts/AuthContext';

export const Dashboard = () => {
  const [showFaq, setShowFaq] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/signin');
  };

  const faqs = [
    {
      question: 'How does the system detect fake videos?',
      answer:
        'Our system uses advanced AI and machine learning algorithms to analyze multiple aspects of a YouTube video including metadata, comment sentiment, engagement patterns, category-based risk assessment, and historical patterns. We combine these signals to provide a comprehensive analysis of content authenticity.',
    },
    {
      question: 'Is my data safe?',
      answer:
        'Absolutely! We take data security seriously. We only analyze publicly available YouTube data and do not store any personal information. All analysis is performed securely, and we follow industry best practices for data protection and privacy.',
    },
    {
      question: 'Can it analyze any YouTube link?',
      answer:
        'Yes! Our system can analyze any publicly available YouTube video. Simply paste the video URL into our analyzer, and we will process the video metadata, comments, engagement metrics, and other signals to determine its authenticity.',
    },
    {
      question: 'How accurate is the detection system?',
      answer:
        'Our system leverages multiple data sources and advanced ML models to provide high accuracy. However, no automated system is perfect. We provide confidence scores and detailed analysis so you can make informed decisions. The system is continuously improved with new data and feedback.',
    },
    {
      question: 'What factors are considered in the analysis?',
      answer:
        'We analyze video metadata, upload patterns, comment sentiment and authenticity, engagement metrics, category-specific risk factors, regional trends, historical content patterns, and comparison with known fake content signatures.',
    },
  ];

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-50 via-blue-50/30 to-white flex flex-col">
      <nav className="bg-white/95 backdrop-blur-sm border-b border-slate-200 shadow-sm w-full sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-6 xl:px-8">
          <div className="flex justify-between items-center h-16 sm:h-18">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="flex items-center gap-2 sm:gap-3 cursor-pointer hover:opacity-80 transition-opacity">
                <div className="p-1 sm:p-2 bg-blue-100 rounded-lg">
                  <Shield className="h-6 w-6 sm:h-7 sm:w-7 text-blue-600" />
                </div>
                <div>
                  <h1 className="text-lg sm:text-xl font-bold text-slate-800">Fake News Detection</h1>
                  <p className="text-xs text-slate-500 hidden sm:block">AI-Powered Analysis</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3 sm:gap-4">
              <div className="hidden md:flex flex-col text-right">
                <span className="text-sm font-medium text-slate-700">
                  {user?.name}
                </span>
                <span className="text-xs text-slate-500">Dashboard</span>
              </div>
              <Button variant="outline" onClick={handleLogout} className="gap-1 sm:gap-2 text-xs sm:text-sm px-3 sm:px-4 h-9 sm:h-10 border-slate-300 hover:bg-slate-50">
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
          className="text-center mb-8 sm:mb-12 lg:mb-16"
        >
          <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 lg:p-10 max-w-4xl mx-auto">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-4 sm:mb-6">
              Welcome to Youtube Fake News Detection
            </h2>
            <p className="text-sm sm:text-base lg:text-lg text-slate-600 leading-relaxed mb-6 sm:mb-8">
              Our advanced AI-powered system analyzes YouTube videos to determine their authenticity. 
              We examine video metadata, comment patterns, engagement metrics, and visual elements 
              to provide comprehensive authenticity assessments.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button
                onClick={() => navigate('/analyze')} 
                size="lg"
                className="gap-2 text-sm sm:text-base px-6 sm:px-8 py-3 sm:py-4 bg-blue-600 hover:bg-blue-700"
              >
                <Search className="h-4 w-4 sm:h-5 sm:w-5" />
                Start Analysis
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => setShowFaq(!showFaq)}
                className="gap-2 text-sm sm:text-base px-6 sm:px-8 py-3 sm:py-4"
              >
                Learn More
                <ChevronDown
                  className={`h-4 w-4 sm:h-5 sm:w-5 transition-transform ${showFaq ? 'rotate-180' : ''}`}
                />
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Feature Cards Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mb-8 sm:mb-12 lg:mb-16"
        >
          <h3 className="text-xl sm:text-2xl font-bold text-slate-900 mb-6 sm:mb-8 text-center">
            Our Detection Capabilities
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            <Card className="bg-white shadow-lg border-0 hover:shadow-xl transition-shadow duration-300">
              <CardHeader className="text-center pb-3">
                <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                  <Brain className="h-6 w-6 text-blue-600" />
                </div>
                <CardTitle className="text-lg font-semibold">AI Analysis</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <CardDescription className="text-sm leading-relaxed">
                  Advanced machine learning algorithms analyze video authenticity patterns
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="bg-white shadow-lg border-0 hover:shadow-xl transition-shadow duration-300">
              <CardHeader className="text-center pb-3">
                <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
                  <MessageSquare className="h-6 w-6 text-green-600" />
                </div>
                <CardTitle className="text-lg font-semibold">Comment Analysis</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <CardDescription className="text-sm leading-relaxed">
                  Sentiment analysis of comments to detect suspicious engagement patterns
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="bg-white shadow-lg border-0 hover:shadow-xl transition-shadow duration-300">
              <CardHeader className="text-center pb-3">
                <div className="mx-auto w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-3">
                  <BarChart3 className="h-6 w-6 text-purple-600" />
                </div>
                <CardTitle className="text-lg font-semibold">Metadata Check</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <CardDescription className="text-sm leading-relaxed">
                  Comprehensive analysis of video metadata and engagement metrics
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="bg-white shadow-lg border-0 hover:shadow-xl transition-shadow duration-300">
              <CardHeader className="text-center pb-3">
                <div className="mx-auto w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mb-3">
                  <Eye className="h-6 w-6 text-orange-600" />
                </div>
                <CardTitle className="text-lg font-semibold">Visual Detection</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <CardDescription className="text-sm leading-relaxed">
                  Thumbnail and visual content analysis for authenticity verification
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </motion.div>

        <AnimatePresence>
          {showFaq && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.4 }}
              className="max-w-5xl mx-auto px-2 sm:px-4"
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="bg-white rounded-2xl shadow-lg p-6 sm:p-8"
              >
                <h3 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900 mb-6 sm:mb-8 text-center">
                  Frequently Asked Questions
                </h3>
                <div className="space-y-4 sm:space-y-6">
                  {faqs.map((faq, index) => (
                    <Accordion key={index} type="single" collapsible>
                      <AccordionItem
                        value={`item-${index}`}
                        className="border border-slate-200 bg-white rounded-xl overflow-hidden shadow-sm accordion-item-white"
                      >
                        <AccordionTrigger className="text-left hover:no-underline px-4 sm:px-6 py-4 sm:py-5 bg-white hover:bg-white transition-colors accordion-trigger-white">
                          <span className="font-semibold text-slate-800 text-sm sm:text-base lg:text-lg pr-4">
                            {faq.question}
                          </span>
                        </AccordionTrigger>
                        <AccordionContent className="px-4 sm:px-6 pb-4 sm:pb-5 pt-0 bg-white accordion-content-white">
                          <div className="text-slate-600 leading-relaxed text-sm sm:text-base border-t border-slate-200 pt-4">
                            {faq.answer}
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    </Accordion>
                  ))}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-auto">
        <div className="w-full py-6 px-0">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pl-4 pr-4 sm:pl-6 sm:pr-6">
            <div className="flex items-center gap-2 -ml-2">
              <Shield className="h-5 w-5 text-blue-600" />
              <span className="text-sm font-medium text-slate-600">
                © 2025 Fake Detection System. All rights reserved.
              </span>
            </div>
            <div className="flex items-center gap-4 text-sm text-slate-600 -mr-2">
              <span>Privacy Policy</span>
              <span>•</span>
              <span>Terms of Service</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
