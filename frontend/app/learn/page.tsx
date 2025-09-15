'use client';

import { useState } from 'react';
import { useRequireAuth } from '@/hooks';
import PageLayout from '../layouts/PageLayout';
import LearningModulesList from '@/components/learning/LearningModulesList';
import LearningModuleForm from '@/components/learning/LearningModuleForm';
import LearningModuleViewer from '@/components/learning/LearningModuleViewer';
import { Loader2 } from 'lucide-react';

type ViewMode = 'list' | 'create' | 'edit' | 'view';

export default function LearnPage() {
  // Use authentication hook
  const { user, loading, isAuthenticated, userProfile } = useRequireAuth();
  
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [selectedModuleId, setSelectedModuleId] = useState<string | null>(null);
  const [selectedModuleData, setSelectedModuleData] = useState<any>(null);

  const handleCreateModule = () => {
    setViewMode('create');
    setSelectedModuleData(null);
  };

  const handleEditModule = (moduleData: any) => {
    setViewMode('edit');
    setSelectedModuleData(moduleData);
  };

  const handleViewModule = (moduleId: string) => {
    setSelectedModuleId(moduleId);
    setViewMode('view');
  };

  const handleBackToList = () => {
    setViewMode('list');
    setSelectedModuleId(null);
    setSelectedModuleData(null);
  };

  const handleModuleSubmit = async (moduleData: any) => {
    try {
      const endpoint = viewMode === 'create' 
        ? `${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-learning/modules`
        : `${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-learning/modules/${selectedModuleData?.id}`;
      
      const method = viewMode === 'create' ? 'POST' : 'PUT';

      const response = await fetch(endpoint, {
        method,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(moduleData),
      });

      if (response.ok) {
        // Success - go back to list
        handleBackToList();
        // TODO: Show success toast
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save module');
      }
    } catch (error) {
      console.error('Error saving module:', error);
      // TODO: Show error toast
    }
  };

  const handleModuleComplete = (moduleId: string) => {
    // TODO: Show completion celebration
    console.log('Module completed:', moduleId);
  };

  // Support both user and userProfile for role
  const getUserRole = () => {
    return (user as any)?.role || userProfile?.role || 'student';
  };

  if (loading) {
    return (
      <PageLayout>
        <div className="flex flex-col items-center justify-center py-16">
          <Loader2 className="w-12 h-12 text-blue-600 dark:text-blue-400 animate-spin mb-4" />
          <p className="text-lg font-medium text-gray-900 dark:text-white">Loading authentication...</p>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {viewMode === 'list' && (
          <LearningModulesList
            onCreateModule={handleCreateModule}
            onViewModule={handleViewModule}
            userRole={getUserRole()}
          />
        )}

        {(viewMode === 'create' || viewMode === 'edit') && (
          <LearningModuleForm
            onSubmit={handleModuleSubmit}
            onCancel={handleBackToList}
            initialData={selectedModuleData}
            mode={viewMode}
          />
        )}

        {viewMode === 'view' && selectedModuleId && (
          <LearningModuleViewer
            moduleId={selectedModuleId}
            onBack={handleBackToList}
            onComplete={handleModuleComplete}
          />
        )}
      </div>
    </PageLayout>
  );
}
