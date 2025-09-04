'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { FileSearch, Loader2, AlertTriangle } from 'lucide-react';
import UploadZone from '../../components/common/UploadZone';
import apiClient, { CheckResponse, CheckRequest } from '../../lib/api';
import ResultCard from '../../components/common/ResultCard';
import { detectLanguage } from '../../lib/utils';
import { toast } from 'react-hot-toast';
import { useRequireAuth, useContentChecker, usePageView } from '@/hooks';
import { useAnalysisStore } from '@/lib/store';
import PageLayout from '../layouts/PageLayout';

function AnalyzePageContent() {
  // Use custom hooks
  const { session, status } = useRequireAuth();
  const { checkContent, isLoading: isChecking } = useContentChecker();
  const { currentAnalysis, setCurrentAnalysis } = useAnalysisStore();
  
  // Set up page tracking
  usePageView('Content Analysis');
  
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<CheckResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const checkId = searchParams.get('id');

  // Fetch check result if ID is provided in URL
  useEffect(() => {
    const fetchCheckResult = async (id: string) => {
      if (status !== 'authenticated') return;
      
      setIsLoading(true);
      setError(null);
      try {
        const data = await apiClient.getCheck(id);
        setResult(data);
        setCurrentAnalysis(data);
      } catch (error: any) {
        console.error('Failed to fetch check result:', error);
        setError('Failed to fetch the analysis result. Please try again.');
        toast.error('Failed to fetch the analysis result. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    if (checkId && !result && !isLoading && status === 'authenticated') {
      fetchCheckResult(checkId);
    }
    
    // Use current analysis from store if available
    if (currentAnalysis && !result) {
      setResult(currentAnalysis);
    }
  }, [checkId, result, isLoading, currentAnalysis, setCurrentAnalysis, status]);

  const handleFileAccepted = async (file: File) => {
    try {
      const checkResult = await checkContent('image', file);
      setResult(checkResult);
    } catch (error: any) {
      setError(error.message || 'Failed to analyze the file. Please try again.');
    }
  };

  const handleTextInput = async (text: string) => {
    try {
      const checkResult = await checkContent('text', text, detectLanguage(text));
      setResult(checkResult);
    } catch (error: any) {
      setError(error.message || 'Failed to analyze the text. Please try again.');
    }
  };

  const handleUrlInput = async (url: string) => {
    try {
      const checkResult = await checkContent('url', url);
      setResult(checkResult);
    } catch (error: any) {
      setError(error.message || 'Failed to analyze the URL. Please try again.');
    }
  };

  const handleShare = () => {
    if (result) {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Link copied to clipboard!');
    }
  };

  const handleDownload = () => {
    if (!result) return;
    
    // Create a downloadable JSON file
    const jsonContent = JSON.stringify(result, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.href = url;
    link.download = `check_${result.id}.json`;
    document.body.appendChild(link);
    link.click();
    
    setTimeout(() => {
      URL.revokeObjectURL(url);
      document.body.removeChild(link);
    }, 100);
  };

  const resetAnalysis = () => {
    setResult(null);
    router.push('/analyze', { scroll: false });
  };

  if (status === 'loading') {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <Loader2 className="w-12 h-12 text-blue-600 dark:text-blue-400 animate-spin mb-4" />
        <p className="text-lg font-medium text-gray-900 dark:text-gray-100">Loading authentication...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {!result ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
            <div className="text-center mb-10">
              <h1 className="text-3xl font-bold text-gray-900 mb-3">Analyze Content</h1>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Upload text, images, or provide a URL to analyze for potential misinformation.
                Get AI-powered insights and evidence in seconds.
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded">
                <div className="flex items-center">
                  <AlertTriangle className="w-5 h-5 text-red-400 mr-2" />
                  <p className="text-red-800">{error}</p>
                </div>
              </div>
            )}

            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 relative">
              <UploadZone
                onFileAccepted={handleFileAccepted}
                onTextInput={handleTextInput}
                onUrlInput={handleUrlInput}
                isLoading={isLoading || isChecking}
              />
            </div>

            <div className="mt-8 text-center text-gray-600">
              <p className="flex items-center justify-center text-sm">
                <FileSearch className="w-4 h-4 mr-1" />
                MisinfoGuard analyzes content across multiple languages and formats
              </p>
            </div>
          </motion.div>
        ) : (
          <div className="mb-8">
            <div className="mb-6">
              <button
                onClick={resetAnalysis}
                className="text-blue-600 hover:text-blue-800 flex items-center"
              >
                ← Back to Analysis
              </button>
            </div>
            
            <ResultCard
              result={result}
              onShare={handleShare}
              onDownload={handleDownload}
            />
          </div>
        )}

        {(isLoading || isChecking) && checkId && (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-10 h-10 text-blue-600 animate-spin mb-4" />
            <p className="text-xl font-medium text-gray-900">Loading analysis results...</p>
            <p className="text-gray-600 mt-2">This should only take a moment</p>
          </div>
        )}
      </div>
    );
}

export default function AnalyzePage() {
  return (
    <PageLayout>
      <Suspense fallback={
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="w-10 h-10 text-blue-600 dark:text-blue-400 animate-spin mb-4" />
          <p className="text-xl font-medium text-gray-900 dark:text-gray-100">Loading...</p>
        </div>
      }>
        <AnalyzePageContent />
      </Suspense>
    </PageLayout>
  );
}
