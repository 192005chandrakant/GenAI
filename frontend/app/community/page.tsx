'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, TrendingUp, Award, Filter, Search, MessageCircle, Loader2, ThumbsUp, Eye, Flag, Share2 } from 'lucide-react';
import MainLayout from '../../components/layout/MainLayout';
import { formatTimestamp } from '../../lib/utils';
import CredibilityBadge from '../../components/common/CredibilityBadge';
import { toast } from 'react-hot-toast';
import { useRequireAuth, usePageView } from '@/hooks';
import apiClient from '@/lib/api';

interface CommunityPost {
  id: string;
  title: string;
  content: string;
  user: {
    id: string;
    name: string;
    avatar: string;
    level: number;
  };
  credibilityScore: number;
  timestamp: string;
  tags: string[];
  comments: number;
  likes: number;
  views: number;
  verified: boolean;
}

// Mock data
const mockPosts: CommunityPost[] = [
  {
    id: 'post_1',
    title: 'Analysis of viral WhatsApp message about COVID-19 vaccines',
    content: 'I received this message claiming COVID vaccines contain microchips. I ran it through MisinfoGuard and here are the results...',
    user: {
      id: 'user_1',
      name: 'Aarav Patel',
      avatar: '/avatars/user1.jpg',
      level: 4,
    },
    credibilityScore: 15,
    timestamp: '2025-08-30T14:23:00Z',
    tags: ['covid', 'vaccine', 'whatsapp'],
    comments: 24,
    likes: 38,
    views: 142,
    verified: true,
  },
  {
    id: 'post_2',
    title: 'Fact-checking the viral flood images from Mumbai',
    content: 'Many images of flooding in Mumbai are being shared that are actually from past years or other locations. Here\'s how to identify them...',
    user: {
      id: 'user_2',
      name: 'Priya Singh',
      avatar: '/avatars/user2.jpg',
      level: 7,
    },
    credibilityScore: 87,
    timestamp: '2025-09-01T09:45:00Z',
    tags: ['floods', 'mumbai', 'images', 'verification'],
    comments: 42,
    likes: 76,
    views: 253,
    verified: true,
  },
  {
    id: 'post_3',
    title: 'Detecting AI-generated images in political campaigns',
    content: 'I\'ve noticed an increase in AI-generated images being used in local political campaigns. Here\'s a guide to spot them...',
    user: {
      id: 'user_3',
      name: 'Vikram Desai',
      avatar: '/avatars/user3.jpg',
      level: 5,
    },
    credibilityScore: 72,
    timestamp: '2025-09-02T17:15:00Z',
    tags: ['ai', 'deepfakes', 'politics', 'elections'],
    comments: 31,
    likes: 54,
    views: 198,
    verified: false,
  },
  {
    id: 'post_4',
    title: 'Misleading economic statistics in recent news coverage',
    content: 'I analyzed how certain media outlets are misrepresenting economic data with misleading charts and statistics...',
    user: {
      id: 'user_4',
      name: 'Amrita Verma',
      avatar: '/avatars/user4.jpg',
      level: 9,
    },
    credibilityScore: 91,
    timestamp: '2025-09-01T11:30:00Z',
    tags: ['economics', 'statistics', 'media', 'data visualization'],
    comments: 57,
    likes: 112,
    views: 327,
    verified: true,
  },
  {
    id: 'post_5',
    title: 'Anatomy of a viral conspiracy theory',
    content: 'I tracked how a conspiracy theory about 5G technology spread through various social media platforms in India...',
    user: {
      id: 'user_5',
      name: 'Rahul Sharma',
      avatar: '/avatars/user5.jpg',
      level: 6,
    },
    credibilityScore: 84,
    timestamp: '2025-08-29T13:40:00Z',
    tags: ['conspiracy', '5g', 'social media', 'viral content'],
    comments: 68,
    likes: 93,
    views: 271,
    verified: true,
  },
  {
    id: 'post_6',
    title: 'Help needed: Is this video from a recent earthquake authentic?',
    content: 'Someone shared this video claiming it\'s from yesterday\'s earthquake, but something feels off about it...',
    user: {
      id: 'user_6',
      name: 'Neha Kapoor',
      avatar: '/avatars/user6.jpg',
      level: 3,
    },
    credibilityScore: 45,
    timestamp: '2025-09-02T16:10:00Z',
    tags: ['earthquake', 'video', 'verification request'],
    comments: 19,
    likes: 22,
    views: 94,
    verified: false,
  },
];

type FilterOption = 'all' | 'trending' | 'verified' | 'needshelp';

export default function CommunityPage() {
  // Use authentication hook
  const { session, status } = useRequireAuth();
  
  // Set up page tracking
  usePageView('Community Insights');
  
  const [posts, setPosts] = useState<CommunityPost[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<FilterOption>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // Fetch community posts
  useEffect(() => {
    const fetchPosts = async () => {
      if (status !== 'authenticated') return;
      
      setIsLoading(true);
      setError(null);
      try {
        // Try to fetch from API
        try {
          // const data = await apiClient.getCommunityPosts();
          // setPosts(data);
          throw new Error('API endpoint not implemented yet');
        } catch (apiError) {
          console.warn('Failed to fetch from API, using mock data:', apiError);
          // Fallback to mock data
          setPosts(mockPosts);
        }
      } catch (error: any) {
        console.error('Failed to fetch community posts:', error);
        setError(error.message || 'Failed to load community content');
        toast.error('Failed to load community content');
      } finally {
        setIsLoading(false);
      }
    };
    
    if (status === 'authenticated') {
      fetchPosts();
    }
  }, [status]);

  // All unique tags
  const allTags = Array.from(
    new Set(posts.flatMap(post => post.tags))
  ).sort();

  // Filter posts based on active filter, search query, and selected tags
  const filteredPosts = posts.filter(post => {
    // Filter by search query
    const matchesSearch = 
      searchQuery === '' || 
      post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    // Filter by selected tags
    const matchesTags = 
      selectedTags.length === 0 || 
      selectedTags.some(tag => post.tags.includes(tag));
    
    // Filter by active filter
    let matchesFilter = true;
    if (activeFilter === 'trending') {
      matchesFilter = post.views > 200 || post.likes > 50;
    } else if (activeFilter === 'verified') {
      matchesFilter = post.verified;
    } else if (activeFilter === 'needshelp') {
      matchesFilter = post.credibilityScore < 60 && post.comments < 20;
    }
    
    return matchesSearch && matchesTags && matchesFilter;
  });

  const toggleTag = (tag: string) => {
    setSelectedTags(prev => 
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  if (status === 'loading') {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center py-16">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
          <p className="text-lg font-medium text-gray-900">Loading authentication...</p>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <section className="mb-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center"
          >
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Community Insights
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Join our community of fact-checkers and misinformation fighters. Share your findings,
              ask questions, and collaborate to build a more informed society.
            </p>
          </motion.div>
        </section>
        
        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <div className="ml-auto pl-3">
                <div className="-mx-1.5 -my-1.5">
                  <button 
                    type="button"
                    onClick={() => setError(null)}
                    className="inline-flex bg-red-50 rounded-md p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    <span className="sr-only">Dismiss</span>
                    <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filter and Search Section */}
        <section className="mb-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
              <div className="flex space-x-2">
                <button
                  onClick={() => setActiveFilter('all')}
                  className={`flex items-center px-4 py-2 rounded-lg ${
                    activeFilter === 'all'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Users className="w-4 h-4 mr-2" />
                  <span>All Posts</span>
                </button>
                <button
                  onClick={() => setActiveFilter('trending')}
                  className={`flex items-center px-4 py-2 rounded-lg ${
                    activeFilter === 'trending'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <TrendingUp className="w-4 h-4 mr-2" />
                  <span>Trending</span>
                </button>
                <button
                  onClick={() => setActiveFilter('verified')}
                  className={`flex items-center px-4 py-2 rounded-lg ${
                    activeFilter === 'verified'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Award className="w-4 h-4 mr-2" />
                  <span>Verified</span>
                </button>
                <button
                  onClick={() => setActiveFilter('needshelp')}
                  className={`flex items-center px-4 py-2 rounded-lg ${
                    activeFilter === 'needshelp'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <MessageCircle className="w-4 h-4 mr-2" />
                  <span>Needs Help</span>
                </button>
              </div>
              
              <div className="w-full md:w-auto relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  placeholder="Search community posts..."
                  className="block w-full md:w-64 pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>

            {/* Tags Filter */}
            {allTags.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center flex-wrap gap-2">
                  <div className="flex items-center mr-2">
                    <Filter className="w-4 h-4 text-gray-500 mr-1" />
                    <span className="text-sm text-gray-700">Topics:</span>
                  </div>
                  {allTags.map(tag => (
                    <button
                      key={tag}
                      onClick={() => toggleTag(tag)}
                      className={`px-3 py-1 text-xs rounded-full ${
                        selectedTags.includes(tag)
                          ? 'bg-blue-100 text-blue-800 border border-blue-300'
                          : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Community Posts */}
        <section>
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-16">
              <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
              <p className="text-lg font-medium text-gray-900">Loading community posts...</p>
            </div>
          ) : filteredPosts.length > 0 ? (
            <div className="space-y-6">
              {filteredPosts.map(post => (
                <motion.div
                  key={post.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden"
                >
                  <div className="p-6">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center mb-4">
                        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                          {post.user.avatar ? (
                            <img
                              src={post.user.avatar}
                              alt={post.user.name}
                              className="w-10 h-10 rounded-full"
                            />
                          ) : (
                            <span className="text-blue-600 font-medium">
                              {post.user.name.charAt(0)}
                            </span>
                          )}
                        </div>
                        <div>
                          <div className="flex items-center">
                            <span className="font-medium text-gray-900">{post.user.name}</span>
                            <span className="ml-2 bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-full">
                              Level {post.user.level}
                            </span>
                            {post.verified && (
                              <span className="ml-2 bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded-full flex items-center">
                                <Award className="w-3 h-3 mr-1" />
                                Verified
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-500">
                            {formatTimestamp(post.timestamp)}
                          </p>
                        </div>
                      </div>
                      
                      <CredibilityBadge score={post.credibilityScore} size="md" />
                    </div>
                    
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{post.title}</h3>
                    <p className="text-gray-700 mb-4 line-clamp-2">{post.content}</p>
                    
                    <div className="flex flex-wrap gap-2 mb-4">
                      {post.tags.map(tag => (
                        <span
                          key={tag}
                          className="px-3 py-1 text-xs rounded-full bg-gray-100 text-gray-700"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex space-x-4">
                        <button className="flex items-center text-gray-600 hover:text-blue-600">
                          <ThumbsUp className="w-4 h-4 mr-1" />
                          <span>{post.likes}</span>
                        </button>
                        <button className="flex items-center text-gray-600 hover:text-blue-600">
                          <MessageCircle className="w-4 h-4 mr-1" />
                          <span>{post.comments}</span>
                        </button>
                        <div className="flex items-center text-gray-500">
                          <Eye className="w-4 h-4 mr-1" />
                          <span>{post.views}</span>
                        </div>
                      </div>
                      
                      <div className="flex space-x-2">
                        <button className="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-100">
                          <Flag className="w-4 h-4" />
                        </button>
                        <button className="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-100">
                          <Share2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="bg-gray-100 rounded-full p-4 mb-4">
                <Search className="w-10 h-10 text-gray-500" />
              </div>
              <h3 className="text-xl font-medium text-gray-900 mb-2">No matching posts found</h3>
              <p className="text-gray-600 max-w-md">
                Try adjusting your search terms or filters to find what you're looking for.
              </p>
              <button className="mt-4 btn btn-primary btn-md">Create a New Post</button>
            </div>
          )}
        </section>

        {/* Floating Action Button */}
        <div className="fixed bottom-8 right-8">
          <button className="btn btn-primary btn-lg rounded-full shadow-lg flex items-center">
            <span className="text-xl mr-2">+</span> New Post
          </button>
        </div>
      </div>
    </MainLayout>
  );
}
