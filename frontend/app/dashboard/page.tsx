'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';
import { useRouter } from 'next/navigation';
import { Loader2, FileText, Award, BarChart3, BookOpen } from 'lucide-react';
import WelcomeBanner from '../../components/dashboard/WelcomeBanner';
import StatCard from '../../components/dashboard/StatCard';
import RecentActivity from '../../components/dashboard/RecentActivity';
import Achievements from '../../components/dashboard/Achievements';
import Leaderboard from '../../components/dashboard/Leaderboard';
import LearningProgress from '../../components/dashboard/LearningProgress';
import apiClient from '@/lib/api';
import { toast } from 'react-hot-toast';

// Define dashboard data structure
interface DashboardData {
  stats: {
    total_checks: number;
    points: number;
    leaderboard_rank: number;
    courses_completed: number;
    stats_change: {
      checks_change: string;
      points_change: string;
      rank_change: string;
      courses_change: string;
    }
  };
  recent_activity: Array<{
    id: string;
    verdict: string;
    summary: string;
    score: number;
    date: string;
  }>;
  achievements: Array<{
    id: string;
    name: string;
    icon: string;
    color: string;
    description: string;
    achieved: boolean;
    progress?: number;
  }>;
  learning_progress: Array<{
    id: string;
    title: string;
    progress: number;
  }>;
}

export default function DashboardPage() {
  const { user, userProfile, loading } = useAuth();
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(true);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login');
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setIsLoadingData(true);
      const data = await apiClient.getDashboardData();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Failed to load dashboard data. Please try again.');
      
      // Set default data structure on error
      setDashboardData({
        stats: {
          total_checks: 0,
          points: 0,
          leaderboard_rank: 0,
          courses_completed: 0,
          stats_change: {
            checks_change: '+0%',
            points_change: '+0',
            rank_change: '0',
            courses_change: '+0'
          }
        },
        recent_activity: [],
        achievements: [],
        learning_progress: []
      });
    } finally {
      setIsLoadingData(false);
    }
  };

  if (loading || !user || isLoadingData) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
      </div>
    );
  }

  // Properly typed stats with guaranteed changeType values
  const stats = [
    {
      title: 'Total Checks',
      value: dashboardData?.stats?.total_checks?.toString() || '0',
      icon: FileText,
      change: dashboardData?.stats?.stats_change?.checks_change || '0%',
      changeType: (dashboardData?.stats?.stats_change?.checks_change?.startsWith('+') ? 'increase' : 'decrease') as 'increase' | 'decrease',
    },
    {
      title: 'Total Points',
      value: dashboardData?.stats?.points?.toLocaleString() || '0',
      icon: Award,
      change: dashboardData?.stats?.stats_change?.points_change || '0',
      changeType: (dashboardData?.stats?.stats_change?.points_change?.startsWith('+') ? 'increase' : 'decrease') as 'increase' | 'decrease',
    },
    {
      title: 'Leaderboard Rank',
      value: `#${dashboardData?.stats?.leaderboard_rank || '0'}`,
      icon: BarChart3,
      change: dashboardData?.stats?.stats_change?.rank_change || '0',
      changeType: (dashboardData?.stats?.stats_change?.rank_change?.startsWith('-') ? 'increase' : 'decrease') as 'increase' | 'decrease',
    },
    {
      title: 'Courses Completed',
      value: dashboardData?.stats?.courses_completed?.toString() || '0',
      icon: BookOpen,
      change: dashboardData?.stats?.stats_change?.courses_change || '0',
      changeType: (dashboardData?.stats?.stats_change?.courses_change?.startsWith('+') ? 'increase' : 'decrease') as 'increase' | 'decrease',
    },
  ];

  // Extract user info safely
  const userName = userProfile?.full_name?.split(' ')[0] || user?.displayName?.split(' ')[0] || 'User';
  // Extract user ID safely
  const userId = userProfile?.id || user?.uid || '';

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <WelcomeBanner name={userName} />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 my-8">
          {stats.map((stat, index) => (
            <StatCard key={index} {...stat} />
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <RecentActivity 
              activities={dashboardData?.recent_activity || []} 
            />
          </div>
          <div className="space-y-6">
            <Achievements 
              achievements={dashboardData?.achievements || []} 
            />
            <Leaderboard 
              currentUserId={userId} 
            />
          </div>
        </div>

        <div className="mt-6">
          <LearningProgress 
            modules={dashboardData?.learning_progress || []} 
          />
        </div>
      </div>
    </div>
  );
}