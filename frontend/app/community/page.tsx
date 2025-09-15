'use client';

import { useState } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';
import PageLayout from '../layouts/PageLayout';
import CommunityFeed from '@/components/community/CommunityFeed';
import CommunityPostForm from '@/components/community/CommunityPostForm';
import { Loader2 } from 'lucide-react';
import { toast } from 'react-hot-toast';

type ViewMode = 'feed' | 'create' | 'edit' | 'view';

export default function CommunityPage() {
  // Use authentication hook
  const { user, loading } = useAuth();
  
  const [viewMode, setViewMode] = useState<ViewMode>('feed');
  const [selectedPostId, setSelectedPostId] = useState<string | null>(null);
  const [selectedPostData, setSelectedPostData] = useState<any>(null);

  const handleCreatePost = () => {
    setViewMode('create');
    setSelectedPostData(null);
  };

  const handleEditPost = (postData: any) => {
    setViewMode('edit');
    setSelectedPostData(postData);
  };

  const handleViewPost = (postId: string) => {
    setSelectedPostId(postId);
    setViewMode('view');
    console.log('View post:', postId);
  };

  const handleBackToFeed = () => {
    setViewMode('feed');
    setSelectedPostId(null);
    setSelectedPostData(null);
  };

  const handlePostSubmit = async (postData: any) => {
    try {
      const endpoint = viewMode === 'create' 
        ? `${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-community/posts`
        : `${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-community/posts/${selectedPostData?.id}`;
      
      const method = viewMode === 'create' ? 'POST' : 'PUT';

      const response = await fetch(endpoint, {
        method,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
      });

      if (response.ok) {
        handleBackToFeed();
        toast.success('Post saved successfully!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save post');
      }
    } catch (error) {
      console.error('Error saving post:', error);
      toast.error('Failed to save post. Please try again.');
    }
  };

  const getUserRole = () => {
    return (user as any)?.role || 'user';
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
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Main content area */}
        {viewMode === 'feed' && (
          <CommunityFeed 
            onCreatePost={handleCreatePost}
            onEditPost={handleEditPost}
            onViewPost={handleViewPost}
            userRole={getUserRole()}
          />
        )}

        {/* Post creation/editing */}
        {(viewMode === 'create' || viewMode === 'edit') && (
          <CommunityPostForm
            mode={viewMode}
            initialData={selectedPostData}
            onSubmit={handlePostSubmit}
            onCancel={handleBackToFeed}
            userRole={getUserRole()}
          />
        )}

        {/* Individual post view */}
        {viewMode === 'view' && selectedPostId && (
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Post View</h2>
            <p className="text-gray-600 mb-4">Individual post view coming soon...</p>
            <button
              onClick={handleBackToFeed}
              className="text-blue-600 hover:text-blue-800"
            >
              ← Back to Community
            </button>
          </div>
        )}
      </div>
    </PageLayout>
  );
}