'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Filter, Calendar, X, Download, FileText, Search } from 'lucide-react';
import MainLayout from '../../../components/layout/MainLayout';
import CredibilityBadge from '../../../components/common/CredibilityBadge';
import { CheckResponse } from '../../../lib/api';

interface HistoryFilters {
  dateRange: 'all' | 'week' | 'month' | 'year';
  scoreRange: 'all' | 'high' | 'medium' | 'low';
  contentType: 'all' | 'text' | 'link' | 'image' | 'video';
}

interface HistoryItem extends Partial<CheckResponse> {
  date: string;
  contentType: 'text' | 'link' | 'image' | 'video';
  content: string;
}

const mockHistoryData: HistoryItem[] = Array(24)
  .fill(null)
  .map((_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - Math.floor(i / 2));
    
    // Generate some variety in the mock data
    const types = ['text', 'link', 'image', 'video'] as const;
    const contentType = types[i % types.length];
    
    const scoreRanges = [
      { min: 80, max: 99 }, // High (green)
      { min: 40, max: 79 }, // Medium (yellow)
      { min: 10, max: 39 }  // Low (red)
    ];
    
    // Cycle through different score ranges for variety
    const scoreRange = scoreRanges[i % 3];
    const score = Math.floor(Math.random() * (scoreRange.max - scoreRange.min + 1)) + scoreRange.min;
    
    // Generate mock content based on type
    let content = '';
    if (contentType === 'text') {
      content = 'This post claims that ' + ['vaccines cause autism', 'drinking hot water cures COVID-19', 'a new planet was discovered', 'the government is hiding alien technology'][i % 4];
    } else if (contentType === 'link') {
      content = ['https://example-news.com/breaking-story', 'https://social-platform.com/viral-post', 'https://medical-site.org/new-study', 'https://government.gov/official-statement'][i % 4];
    } else if (contentType === 'image') {
      content = ['Photo showing doctored crowd size', 'Manipulated image of political figure', 'Falsely captioned disaster photo', 'AI-generated celebrity image'][i % 4];
    } else {
      content = ['Deceptively edited interview clip', 'Out-of-context protest footage', 'Fake emergency broadcast', 'Deepfake celebrity video'][i % 4];
    }
    
    return {
      id: `check_${i + 100}`,
      score,
      badge: score >= 80 ? 'green' : score >= 40 ? 'yellow' : 'red',
      verdict: score >= 80 ? 'Likely Accurate' : score >= 40 ? 'Needs Context' : 'Likely Misleading',
      summary: content,
      date: date.toISOString(),
      contentType,
      content,
      metadata: {
        processingTime: Math.floor(Math.random() * 1000) + 1500,
        language: Math.random() > 0.3 ? 'en' : 'hi',
        modelVersion: '1.2.0',
        timestamp: date.toISOString(),
      },
    };
  });

export default function HistoryPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<HistoryFilters>({
    dateRange: 'all',
    scoreRange: 'all',
    contentType: 'all',
  });
  const [showFilters, setShowFilters] = useState(false);
  
  const toggleFilters = () => setShowFilters(!showFilters);
  
  const resetFilters = () => {
    setFilters({
      dateRange: 'all',
      scoreRange: 'all',
      contentType: 'all',
    });
  };
  
  // Apply filters to history data
  const filteredHistory = mockHistoryData.filter((item) => {
    // Search filter
    if (searchQuery && !item.content.toLowerCase().includes(searchQuery.toLowerCase()) && 
        !item.verdict?.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    
    // Date range filter
    if (filters.dateRange !== 'all') {
      const checkDate = new Date(item.date);
      const today = new Date();
      if (filters.dateRange === 'week' && (today.getTime() - checkDate.getTime()) > 7 * 24 * 60 * 60 * 1000) {
        return false;
      }
      if (filters.dateRange === 'month' && (today.getTime() - checkDate.getTime()) > 30 * 24 * 60 * 60 * 1000) {
        return false;
      }
      if (filters.dateRange === 'year' && (today.getTime() - checkDate.getTime()) > 365 * 24 * 60 * 60 * 1000) {
        return false;
      }
    }
    
    // Score range filter
    if (filters.scoreRange !== 'all') {
      if (filters.scoreRange === 'high' && (item.score || 0) < 80) return false;
      if (filters.scoreRange === 'medium' && ((item.score || 0) < 40 || (item.score || 0) >= 80)) return false;
      if (filters.scoreRange === 'low' && (item.score || 0) >= 40) return false;
    }
    
    // Content type filter
    if (filters.contentType !== 'all' && item.contentType !== filters.contentType) {
      return false;
    }
    
    return true;
  });

  const navigateToCheck = (checkId: string) => {
    router.push(`/analyze?id=${checkId}`);
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="mb-6">
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Check History</h1>
              <p className="text-gray-600">
                View and manage your previous fact checks
              </p>
            </div>
            
            <div className="flex gap-2">
              <button 
                onClick={toggleFilters}
                className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Filter className="w-4 h-4 mr-2" />
                Filters
              </button>
              
              <button className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <Download className="w-4 h-4 mr-2" />
                Export
              </button>
            </div>
          </div>
          
          {/* Search bar */}
          <div className="mt-6 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search your history..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          {/* Filters panel */}
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="mt-4 p-4 bg-white border border-gray-200 rounded-lg"
            >
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-lg font-medium text-gray-900">Filters</h3>
                <button 
                  onClick={toggleFilters}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
                  <select
                    className="w-full p-2 border border-gray-300 rounded-md"
                    value={filters.dateRange}
                    onChange={(e) => setFilters({...filters, dateRange: e.target.value as any})}
                  >
                    <option value="all">All Time</option>
                    <option value="week">Last 7 Days</option>
                    <option value="month">Last 30 Days</option>
                    <option value="year">Last Year</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Score Range</label>
                  <select
                    className="w-full p-2 border border-gray-300 rounded-md"
                    value={filters.scoreRange}
                    onChange={(e) => setFilters({...filters, scoreRange: e.target.value as any})}
                  >
                    <option value="all">All Scores</option>
                    <option value="high">High (80-100)</option>
                    <option value="medium">Medium (40-79)</option>
                    <option value="low">Low (0-39)</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
                  <select
                    className="w-full p-2 border border-gray-300 rounded-md"
                    value={filters.contentType}
                    onChange={(e) => setFilters({...filters, contentType: e.target.value as any})}
                  >
                    <option value="all">All Types</option>
                    <option value="text">Text</option>
                    <option value="link">Link</option>
                    <option value="image">Image</option>
                    <option value="video">Video</option>
                  </select>
                </div>
              </div>
              
              <div className="mt-4 flex justify-end">
                <button
                  onClick={resetFilters}
                  className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
                >
                  Reset Filters
                </button>
              </div>
            </motion.div>
          )}
        </div>
        
        {/* History List */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="hidden md:grid md:grid-cols-12 text-xs font-medium text-gray-500 bg-gray-50 p-4 border-b border-gray-200 rounded-t-xl">
            <div className="md:col-span-4">Content</div>
            <div className="md:col-span-2">Type</div>
            <div className="md:col-span-2">Date</div>
            <div className="md:col-span-2">Score</div>
            <div className="md:col-span-2">Verdict</div>
          </div>
          
          {filteredHistory.length > 0 ? (
            <div className="divide-y divide-gray-100">
              {filteredHistory.map((item) => (
                <div
                  key={item.id}
                  onClick={() => navigateToCheck(item.id!)}
                  className="p-4 md:grid md:grid-cols-12 md:items-center gap-4 hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <div className="md:col-span-4 mb-2 md:mb-0">
                    <p className="font-medium text-gray-900 line-clamp-1">{item.content}</p>
                    <p className="text-sm text-gray-500 hidden md:block">{item.summary}</p>
                  </div>
                  
                  <div className="md:col-span-2 flex items-center mb-2 md:mb-0">
                    <div className={`w-2 h-2 rounded-full mr-2 ${
                      item.contentType === 'text' ? 'bg-blue-500' :
                      item.contentType === 'link' ? 'bg-purple-500' :
                      item.contentType === 'image' ? 'bg-green-500' :
                      'bg-orange-500'
                    }`}></div>
                    <span className="text-sm text-gray-700 capitalize">{item.contentType}</span>
                  </div>
                  
                  <div className="md:col-span-2 flex items-center text-sm text-gray-500 mb-2 md:mb-0">
                    <Calendar className="w-4 h-4 mr-2 md:hidden" />
                    {new Date(item.date).toLocaleDateString()}
                  </div>
                  
                  <div className="md:col-span-2 mb-2 md:mb-0">
                    <CredibilityBadge score={item.score!} size="sm" />
                  </div>
                  
                  <div className="md:col-span-2">
                    <span className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${
                      item.badge === 'green' ? 'bg-green-100 text-green-800' :
                      item.badge === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {item.verdict}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <h3 className="text-lg font-medium text-gray-900 mb-1">No results found</h3>
              <p className="text-gray-500 mb-4">Try adjusting your search or filters</p>
              <button
                onClick={resetFilters}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Reset Filters
              </button>
            </div>
          )}
          
          {/* Pagination */}
          <div className="p-4 border-t border-gray-200 flex justify-between items-center">
            <span className="text-sm text-gray-600">
              Showing {filteredHistory.length} of {mockHistoryData.length} checks
            </span>
            
            <div className="flex items-center space-x-2">
              <button className="px-3 py-1 border border-gray-300 rounded text-gray-500 hover:bg-gray-50">
                Previous
              </button>
              <button className="px-3 py-1 bg-blue-50 border border-blue-200 rounded text-blue-600">
                1
              </button>
              <button className="px-3 py-1 border border-gray-300 rounded text-gray-500 hover:bg-gray-50">
                2
              </button>
              <button className="px-3 py-1 border border-gray-300 rounded text-gray-500 hover:bg-gray-50">
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
