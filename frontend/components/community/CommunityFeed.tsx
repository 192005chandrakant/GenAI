'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Search, 
  Plus, 
  MessageSquare, 
  Heart, 
  Share, 
  Flag, 
  MoreHorizontal,
  Image as ImageIcon,
  Video,
  FileText,
  Clock,
  User,
  TrendingUp,
  Filter,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

interface CommunityPost {
  id: string;
  title: string;
  content: string;
  post_type: 'discussion' | 'question' | 'resource' | 'fact-check' | 'experience';
  category: string;
  author_id: string;
  author_name: string;
  created_at: string;
  updated_at: string;
  tags: string[];
  media_urls: string[];
  is_fact_checked: boolean;
  fact_check_status: 'pending' | 'verified' | 'disputed' | 'false';
  moderation_status: 'approved' | 'pending' | 'flagged' | 'removed';
  engagement: {
    likes: number;
    comments: number;
    shares: number;
    views: number;
  };
  user_interaction?: {
    has_liked: boolean;
    has_bookmarked: boolean;
    has_reported: boolean;
  };
}

interface CommunityFeedProps {
  onCreatePost?: () => void;
  onEditPost?: (postData: any) => void;
  onViewPost?: (postId: string) => void;
  userRole?: 'user' | 'moderator' | 'admin';
}

export default function CommunityFeed({ 
  onCreatePost, 
  onViewPost,
  userRole = 'user'
}: CommunityFeedProps) {
  const [posts, setPosts] = useState<CommunityPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('recent');
  const [showFactChecked, setShowFactChecked] = useState(false);

  const categories = [
    'misinformation-awareness',
    'fact-checking',
    'media-literacy',
    'digital-citizenship',
    'news-analysis',
    'educational-resources'
  ];

  const postTypes = [
    { value: 'discussion', label: 'Discussion' },
    { value: 'question', label: 'Question' },
    { value: 'resource', label: 'Resource' },
    { value: 'fact-check', label: 'Fact Check' },
    { value: 'experience', label: 'Experience' }
  ];

  useEffect(() => {
    fetchPosts();
  }, [searchTerm, categoryFilter, typeFilter, sortBy, showFactChecked]);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        ...(searchTerm && { search: searchTerm }),
        ...(categoryFilter !== 'all' && { category: categoryFilter }),
        ...(typeFilter !== 'all' && { post_type: typeFilter }),
        sort_by: sortBy,
        ...(showFactChecked && { fact_checked_only: 'true' }),
        limit: '20'
      });

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-community/posts?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPosts(data.posts || []);
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (postId: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-community/posts/${postId}/interactions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interaction_type: 'like'
        }),
      });

      if (response.ok) {
        // Update local state
        setPosts(prev => prev.map(post => {
          if (post.id === postId) {
            const hasLiked = post.user_interaction?.has_liked;
            return {
              ...post,
              engagement: {
                ...post.engagement,
                likes: hasLiked ? post.engagement.likes - 1 : post.engagement.likes + 1
              },
              user_interaction: {
                ...post.user_interaction!,
                has_liked: !hasLiked
              }
            };
          }
          return post;
        }));
      }
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const handleShare = async (post: CommunityPost) => {
    if (navigator.share) {
      await navigator.share({
        title: post.title,
        text: post.content.slice(0, 100) + '...',
        url: `${window.location.origin}/community/posts/${post.id}`,
      });
    } else {
      await navigator.clipboard.writeText(`${window.location.origin}/community/posts/${post.id}`);
      // TODO: Show toast notification
    }

    // Track share
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-community/posts/${post.id}/interactions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interaction_type: 'share'
        }),
      });
    } catch (error) {
      console.error('Error tracking share:', error);
    }
  };

  const handleReport = async (postId: string) => {
    // TODO: Implement report modal
    console.log('Report post:', postId);
  };

  const getPostTypeColor = (type: string) => {
    switch (type) {
      case 'question': return 'bg-blue-100 text-blue-800';
      case 'discussion': return 'bg-green-100 text-green-800';
      case 'resource': return 'bg-purple-100 text-purple-800';
      case 'fact-check': return 'bg-orange-100 text-orange-800';
      case 'experience': return 'bg-pink-100 text-pink-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getFactCheckIcon = (status: string) => {
    switch (status) {
      case 'verified': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'disputed': return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'false': return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default: return null;
    }
  };

  const getMediaIcon = (url: string) => {
    if (url.includes('video') || url.includes('.mp4') || url.includes('.webm')) {
      return <Video className="h-4 w-4" />;
    }
    if (url.includes('image') || url.includes('.jpg') || url.includes('.png')) {
      return <ImageIcon className="h-4 w-4" />;
    }
    return <FileText className="h-4 w-4" />;
  };

  const formatCategory = (category: string) => {
    return category.split('-').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const formatPostType = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1).replace('-', ' ');
  };

  const formatTimeAgo = (dateString: string) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Community</h2>
          <p className="text-gray-600">
            Connect, share, and learn from the community about media literacy and fact-checking
          </p>
        </div>
        <Button onClick={onCreatePost} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Create Post
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Search */}
            <div className="relative lg:col-span-2">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search posts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {formatCategory(category)}
                </option>
              ))}
            </select>

            {/* Type Filter */}
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Types</option>
              {postTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>

            {/* Sort By */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="recent">Most Recent</option>
              <option value="popular">Most Popular</option>
              <option value="comments">Most Discussed</option>
              <option value="likes">Most Liked</option>
            </select>
          </div>

          {/* Additional Filters */}
          <div className="flex items-center gap-4 mt-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={showFactChecked}
                onChange={(e) => setShowFactChecked(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm">Fact-checked only</span>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Posts Feed */}
      {loading ? (
        <div className="space-y-6">
          {[...Array(3)].map((_, index) => (
            <Card key={index} className="animate-pulse">
              <CardHeader>
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/3"></div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : posts.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No posts found</h3>
            <p className="text-gray-600 mb-4">
              Be the first to start a discussion in the community!
            </p>
            <Button onClick={onCreatePost}>
              Create First Post
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {posts.map((post) => (
            <Card key={post.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                      <User className="h-5 w-5 text-gray-600" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium">{post.author_name}</span>
                        {post.is_fact_checked && getFactCheckIcon(post.fact_check_status)}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Clock className="h-3 w-3" />
                        <span>{formatTimeAgo(post.created_at)}</span>
                        <span>•</span>
                        <Badge className={getPostTypeColor(post.post_type)} variant="secondary">
                          {formatPostType(post.post_type)}
                        </Badge>
                        <span>•</span>
                        <span>{formatCategory(post.category)}</span>
                      </div>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div
                  className="cursor-pointer"
                  onClick={() => onViewPost?.(post.id)}
                >
                  <h3 className="font-semibold text-lg mb-2 hover:text-blue-600 transition-colors">
                    {post.title}
                  </h3>
                  <p className="text-gray-700 line-clamp-3">
                    {post.content}
                  </p>
                </div>

                {/* Media Preview */}
                {post.media_urls.length > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {post.media_urls.slice(0, 3).map((url, index) => (
                      <div key={index} className="relative bg-gray-100 rounded-lg h-24 flex items-center justify-center">
                        {getMediaIcon(url)}
                        {post.media_urls.length > 3 && index === 2 && (
                          <div className="absolute inset-0 bg-black bg-opacity-50 rounded-lg flex items-center justify-center text-white text-sm">
                            +{post.media_urls.length - 3} more
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Tags */}
                {post.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {post.tags.slice(0, 4).map(tag => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        #{tag}
                      </Badge>
                    ))}
                    {post.tags.length > 4 && (
                      <Badge variant="outline" className="text-xs">
                        +{post.tags.length - 4}
                      </Badge>
                    )}
                  </div>
                )}

                {/* Engagement */}
                <div className="flex items-center justify-between pt-3 border-t">
                  <div className="flex items-center gap-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleLike(post.id)}
                      className={post.user_interaction?.has_liked ? 'text-red-600' : ''}
                    >
                      <Heart className={`h-4 w-4 mr-1 ${post.user_interaction?.has_liked ? 'fill-current' : ''}`} />
                      {post.engagement.likes}
                    </Button>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onViewPost?.(post.id)}
                    >
                      <MessageSquare className="h-4 w-4 mr-1" />
                      {post.engagement.comments}
                    </Button>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleShare(post)}
                    >
                      <Share className="h-4 w-4 mr-1" />
                      {post.engagement.shares}
                    </Button>
                  </div>

                  <div className="flex items-center gap-2">
                    {post.engagement.views > 0 && (
                      <span className="text-xs text-gray-500">
                        {post.engagement.views} views
                      </span>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleReport(post.id)}
                    >
                      <Flag className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}