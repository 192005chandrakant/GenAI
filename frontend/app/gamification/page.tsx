'use client';

import GamificationDashboard from '@/components/ui/gamification-dashboard';
import { useRequireAuth } from '@/hooks';
import PageLayout from '../layouts/PageLayout';

export default function GamificationPage() {
  const { user, loading, isAuthenticated } = useRequireAuth();

  if (loading) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <GamificationDashboard />
    </PageLayout>
  );
}
