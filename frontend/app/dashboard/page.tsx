'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { 
  BarChart3, 
  PieChart, 
  Activity, 
  Award, 
  Clock, 
  CheckCircle2, 
  TrendingUp, 
  MapPin, 
  FileText, 
  UserCircle,
  Settings,
  Loader2
} from 'lucide-react';
import MainLayout from '../../components/layout/MainLayout';
import apiClient, { CheckResponse } from '../../lib/api';
import { toast } from 'react-hot-toast';
import CredibilityBadge from '../../components/common/CredibilityBadge';
import { useRequireAuth, useUserProfile } from '@/hooks';
import { useAnalysisStore } from '@/lib/store';

interface DashboardStats {
  totalChecks: number;
  averageScore: number;
  totalPoints: number;
  userLevel: number;
  recentChecks: CheckResponse[];
  checksByCategory: {
    category: string;
    count: number;
    percentage: number;
  }[];
  topMisinformationTypes: {
    type: string;
    count: number;
    percentage: number;
  }[];
  checkedSources: {
    domain: string;
    count: number;
    avgTrustScore: number;
  }[];
  userRank: number;
  totalUsers: number;
  pointsToNextLevel: number;
  nextLevelProgress: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const { session, status } = useRequireAuth();
  const { user } = useUserProfile();
  const { analysisHistory, addToHistory } = useAnalysisStore();
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activeTimeframe, setActiveTimeframe] = useState<'week' | 'month' | 'year'>('week');

  // Fetch dashboard stats
  useEffect(() => {
    const fetchDashboardData = async () => {
      if (status !== 'authenticated') return;
      
      setIsLoading(true);
      try {
        // Fetch user history
        const userHistory = await apiClient.getUserHistory(10, 0);
        
        // Add history items to the global store
        userHistory.forEach(check => addToHistory(check));
        
        // Fetch analytics data
        const analyticsTimeframe = activeTimeframe === 'year' ? 'month' : activeTimeframe;
        const analyticsData = await apiClient.getAnalytics(analyticsTimeframe === 'week' ? 'week' : 'month');
        
        // Get achievements
        const achievements = await apiClient.getAchievements();
        
        // Get leaderboard
        const leaderboard = await apiClient.getLeaderboard(activeTimeframe === 'year' ? 'all' : activeTimeframe);
        
        // Calculate user rank
        const userRank = leaderboard.findIndex(entry => entry.id === user?.id) + 1;
        
        // Process data into our stats format
        const stats: DashboardStats = {
          totalChecks: analyticsData.totalChecks || 0,
          averageScore: analyticsData.averageScore || 0,
          totalPoints: user?.points || 0,
          userLevel: user?.level || 1,
          recentChecks: userHistory.slice(0, 3),
          checksByCategory: analyticsData.contentTypes?.map(type => ({
            category: type.name,
            count: type.count,
            percentage: type.percentage
          })) || [],
          topMisinformationTypes: analyticsData.misinformationTypes?.map(type => ({
            type: type.name,
            count: type.count,
            percentage: type.percentage
          })) || [],
          checkedSources: analyticsData.sources?.map(source => ({
            domain: source.domain,
            count: source.count,
            avgTrustScore: source.trustScore
          })) || [],
          userRank: userRank || 0,
          totalUsers: leaderboard.length,
          // Calculate next level info
          pointsToNextLevel: 1000 * (user?.level || 1) - (user?.points || 0),
          nextLevelProgress: ((user?.points || 0) % 1000) / 10 // as percentage
        };
        
        setStats(stats);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        toast.error('Failed to load dashboard data');
        
        // Fallback to local history data
        if (analysisHistory.length > 0) {
          setStats({
            totalChecks: analysisHistory.length,
            averageScore: analysisHistory.reduce((sum, check) => sum + check.score, 0) / analysisHistory.length,
            totalPoints: user?.points || 0,
            userLevel: user?.level || 1,
            recentChecks: analysisHistory.slice(0, 3),
            checksByCategory: [],
            topMisinformationTypes: [],
            checkedSources: [],
            userRank: 0,
            totalUsers: 0,
            pointsToNextLevel: 100,
            nextLevelProgress: 50
          });
        }
      } finally {
        setIsLoading(false);
      }
    };
    
    if (status === 'authenticated') {
      fetchDashboardData();
    }
  }, [status, activeTimeframe, user, addToHistory, analysisHistory]);

  const navigateToCheck = (checkId: string) => {
    router.push(`/analyze?id=${checkId}`);
  };

  if (status === 'loading') {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center py-16">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
          <p className="text-lg font-medium text-gray-900">Loading dashboard...</p>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* Dashboard Header */}
        <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-1">Dashboard</h1>
            <p className="text-gray-600">
              {user ? `Welcome back, ${user.full_name.split(' ')[0]}! ` : ''}
              Monitor your fact-checking activity and track your progress.
            </p>
          </div>
          
          {/* Timeframe Selection */}
          <div className="mt-4 md:mt-0 flex space-x-2">
            <button
              onClick={() => setActiveTimeframe('week')}
              className={`px-4 py-2 rounded-lg ${
                activeTimeframe === 'week'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              Week
            </button>
            <button
              onClick={() => setActiveTimeframe('month')}
              className={`px-4 py-2 rounded-lg ${
                activeTimeframe === 'month'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              Month
            </button>
            <button
              onClick={() => setActiveTimeframe('year')}
              className={`px-4 py-2 rounded-lg ${
                activeTimeframe === 'year'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              Year
            </button>
          </div>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
            <p className="text-lg font-medium text-gray-900">Loading dashboard data...</p>
          </div>
        ) : stats ? (
          <>
            {/* Key Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
              >
                <div className="flex justify-between items-center">
                  <h2 className="text-gray-600 font-medium">Total Checks</h2>
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <FileText className="w-5 h-5 text-blue-600" />
                  </div>
                </div>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalChecks}</p>
                <div className="text-sm text-green-600 flex items-center mt-2">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  <span>+12% from last {activeTimeframe}</span>
                </div>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
              >
                <div className="flex justify-between items-center">
                  <h2 className="text-gray-600 font-medium">Average Score</h2>
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Activity className="w-5 h-5 text-green-600" />
                  </div>
                </div>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.averageScore}</p>
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        stats.averageScore >= 80 ? 'bg-green-500' :
                        stats.averageScore >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${stats.averageScore}%` }}
                    ></div>
                  </div>
                </div>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
              >
                <div className="flex justify-between items-center">
                  <h2 className="text-gray-600 font-medium">Total Points</h2>
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Award className="w-5 h-5 text-purple-600" />
                  </div>
                </div>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalPoints}</p>
                <div className="text-sm text-gray-600 flex items-center mt-2">
                  <UserCircle className="w-4 h-4 mr-1" />
                  <span>Level {stats.userLevel}</span>
                  <span className="mx-1">•</span>
                  <span>Rank #{stats.userRank}</span>
                </div>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.3 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
              >
                <div className="flex justify-between items-center">
                  <h2 className="text-gray-600 font-medium">Next Level</h2>
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <Clock className="w-5 h-5 text-yellow-600" />
                  </div>
                </div>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.pointsToNextLevel}</p>
                <div className="text-sm text-gray-600 mt-2">
                  <span>Points needed for Level {stats.userLevel + 1}</span>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                    <div 
                      className="h-2 rounded-full bg-blue-500"
                      style={{ width: `${stats.nextLevelProgress}%` }}
                    ></div>
                  </div>
                </div>
              </motion.div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              {/* Recent Checks */}
              <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">Recent Checks</h2>
                  <button
                    onClick={() => router.push('/dashboard/history')}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    View All
                  </button>
                </div>
                
                <div className="space-y-4">
                  {stats.recentChecks && stats.recentChecks.length > 0 ? (
                    stats.recentChecks.map((check) => (
                      <div 
                        key={check.id}
                        className="p-4 border border-gray-100 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                        onClick={() => navigateToCheck(check.id)}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex-grow">
                            <h3 className="font-medium text-gray-900">{check.verdict}</h3>
                            <p className="text-sm text-gray-600 line-clamp-1">{check.summary}</p>
                          </div>
                          <CredibilityBadge score={check.score} size="sm" showLabel={false} />
                        </div>
                        <div className="flex text-xs text-gray-500">
                          <span>{new Date(check.metadata.timestamp).toLocaleDateString()}</span>
                          <span className="mx-1">•</span>
                          <span>{check.metadata.language.toUpperCase()}</span>
                          <span className="mx-1">•</span>
                          <span>{check.metadata.processingTime}ms</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <p>No recent checks found.</p>
                      <button
                        onClick={() => router.push('/analyze')}
                        className="mt-4 btn btn-sm btn-primary"
                      >
                        Analyze Content
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Check Types Distribution */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">Content Types</h2>
                  <PieChart className="w-5 h-5 text-gray-500" />
                </div>
                
                <div className="space-y-4">
                  {stats.checksByCategory && stats.checksByCategory.length > 0 ? (
                    stats.checksByCategory.map((category) => (
                      <div key={category.category}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-700">{category.category}</span>
                          <span className="text-gray-700 font-medium">{category.count}</span>
                        </div>
                        <div className="w-full bg-gray-100 rounded-full h-2">
                          <div 
                            className="h-2 rounded-full bg-blue-500"
                            style={{ width: `${category.percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-4 text-gray-500">
                      <p>No content type data available yet.</p>
                    </div>
                  )}
                </div>
                
                <hr className="my-6 border-gray-200" />
                
                <div>
                  <h3 className="text-gray-700 font-medium mb-4">Top Misinformation Types</h3>
                  <div className="space-y-3">
                    {stats.topMisinformationTypes && stats.topMisinformationTypes.length > 0 ? (
                      stats.topMisinformationTypes.map((type) => (
                        <div key={type.type} className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">{type.type}</span>
                          <span className="text-xs font-medium bg-gray-100 text-gray-700 px-2 py-1 rounded-full">
                            {type.count}
                          </span>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-4 text-gray-500">
                        <p>No misinformation type data available yet.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              {/* Checked Sources */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">Top Checked Sources</h2>
                  <BarChart3 className="w-5 h-5 text-gray-500" />
                </div>
                
                <div className="space-y-4">
                  {stats.checkedSources && stats.checkedSources.length > 0 ? (
                    stats.checkedSources.map((source) => (
                      <div key={source.domain} className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-800">{source.domain}</p>
                          <p className="text-xs text-gray-500">Checked {source.count} times</p>
                        </div>
                        <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                          source.avgTrustScore >= 80 ? 'bg-green-100 text-green-800' :
                          source.avgTrustScore >= 40 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {source.avgTrustScore}% trusted
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-4 text-gray-500">
                      <p>No source data available yet.</p>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Regional Insights */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">Regional Insights</h2>
                  <MapPin className="w-5 h-5 text-gray-500" />
                </div>
                
                <div className="text-center text-gray-500 py-6">
                  <p className="mb-4">Regional insights visualization coming soon.</p>
                  <p className="text-sm">Track misinformation trends across different regions.</p>
                  <button
                    onClick={() => toast.success('Feature coming in the next update!')}
                    className="mt-4 btn btn-sm btn-outline"
                  >
                    Get Notified
                  </button>
                </div>
              </div>
              
              {/* Achievement Progress */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">Achievements</h2>
                  <Award className="w-5 h-5 text-gray-500" />
                </div>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700">Fact Finder</span>
                      <span className="text-gray-700">5/10</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div className="h-2 rounded-full bg-green-500" style={{ width: '50%' }}></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700">Media Detective</span>
                      <span className="text-gray-700">3/5</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div className="h-2 rounded-full bg-green-500" style={{ width: '60%' }}></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700">Community Guardian</span>
                      <span className="text-gray-700">2/5</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div className="h-2 rounded-full bg-green-500" style={{ width: '40%' }}></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700">Master Educator</span>
                      <span className="text-gray-700">1/5</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div className="h-2 rounded-full bg-green-500" style={{ width: '20%' }}></div>
                    </div>
                  </div>
                </div>
                
                <button
                  onClick={() => router.push('/dashboard/achievements')}
                  className="mt-6 text-center w-full py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                >
                  View All Achievements
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-16">
            <p className="text-lg text-gray-700">Failed to load dashboard data. Please try again.</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 btn btn-primary btn-md"
            >
              Reload Page
            </button>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
