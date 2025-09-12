'use client';

import { useEffect } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';
import { useRouter } from 'next/navigation';
import { Loader2, FileText, Award, BarChart3, BookOpen } from 'lucide-react';
import WelcomeBanner from '../../components/dashboard/WelcomeBanner';
import StatCard from '../../components/dashboard/StatCard';
import RecentActivity from '../../components/dashboard/RecentActivity';
import Achievements from '../../components/dashboard/Achievements';
import Leaderboard from '../../components/dashboard/Leaderboard';
import LearningProgress from '../../components/dashboard/LearningProgress';

export default function DashboardPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login');
    }
  }, [user, loading, router]);

  if (loading || !user) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
      </div>
    );
  }

  type StatData = {
    title: string;
    value: string;
    icon: React.ElementType;
    change: string;
    changeType: 'increase' | 'decrease';
  };

  const stats: StatData[] = [
    {
      title: 'Total Checks',
      value: '42',
      icon: FileText,
      change: '+12%',
      changeType: 'increase',
    },
    {
      title: 'Total Points',
      value: '1,280',
      icon: Award,
      change: '+80',
      changeType: 'increase',
    },
    {
      title: 'Leaderboard Rank',
      value: '#12',
      icon: BarChart3,
      change: '-2',
      changeType: 'decrease',
    },
    {
      title: 'Courses Completed',
      value: '5',
      icon: BookOpen,
      change: '+1',
      changeType: 'increase',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <WelcomeBanner name={user.displayName?.split(' ')[0] || 'User'} />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 my-8">
          {stats.map((stat, index) => (
            <StatCard key={index} {...stat} />
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <RecentActivity />
          </div>
          <div className="space-y-6">
            <Achievements />
            <Leaderboard />
          </div>
        </div>

        <div className="mt-6">
          <LearningProgress />
        </div>
      </div>
    </div>
  );
}