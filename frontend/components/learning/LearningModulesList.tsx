'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Search, 
  Plus, 
  Eye, 
  Clock, 
  Users, 
  Star, 
  BookOpen, 
  Video, 
  Image,
  FileText,
  Shield,
  TrendingUp,
  Filter
} from 'lucide-react';

interface LearningModule {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  content_type: 'text' | 'video' | 'interactive' | 'mixed';
  estimated_duration: number;
  is_published: boolean;
  metadata?: {
    tags: string[];
    fact_check_score: number;
    media_urls: string[];
  };
  created_at: string;
  created_by: string;
  progress?: {
    completion_percentage: number;
    is_completed: boolean;
  };
  stats?: {
    total_users: number;
    avg_completion_rate: number;
    avg_rating: number;
  };
}

interface LearningModulesListProps {
  onCreateModule?: () => void;
  onViewModule?: (moduleId: string) => void;
  userRole?: 'student' | 'educator' | 'admin';
}

export default function LearningModulesList({ 
  onCreateModule, 
  onViewModule,
  userRole = 'student'
}: LearningModulesListProps) {
  const [modules, setModules] = useState<LearningModule[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [difficultyFilter, setDifficultyFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');

  const categories = [
    'misinformation-awareness',
    'fact-checking',
    'media-literacy',
    'digital-citizenship',
    'critical-thinking',
    'source-verification'
  ];

  const difficulties = ['beginner', 'intermediate', 'advanced'];

  useEffect(() => {
    fetchLearningModules();
  }, [searchTerm, categoryFilter, difficultyFilter, sortBy]);

  const fetchLearningModules = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        ...(searchTerm && { search: searchTerm }),
        ...(categoryFilter !== 'all' && { category: categoryFilter }),
        ...(difficultyFilter !== 'all' && { difficulty: difficultyFilter }),
        sort_by: sortBy,
        limit: '20'
      });

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-learning/modules?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setModules(data.modules || []);
      }
    } catch (error) {
      console.error('Error fetching learning modules:', error);
    } finally {
      setLoading(false);
    }
  };

  const getContentTypeIcon = (contentType: string) => {
    switch (contentType) {
      case 'video': return <Video className="h-4 w-4" />;
      case 'text': return <FileText className="h-4 w-4" />;
      case 'interactive': return <BookOpen className="h-4 w-4" />;
      default: return <Image className="h-4 w-4" />;
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  };

  const formatCategory = (category: string) => {
    return category.split('-').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Learning Modules</h2>
          <p className="text-gray-600">
            Discover educational content to enhance your media literacy and fact-checking skills
          </p>
        </div>
        {(userRole === 'educator' || userRole === 'admin') && (
          <Button onClick={onCreateModule} className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Create Module
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search modules..."
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

            {/* Difficulty Filter */}
            <select
              value={difficultyFilter}
              onChange={(e) => setDifficultyFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Difficulties</option>
              {difficulties.map(difficulty => (
                <option key={difficulty} value={difficulty}>
                  {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                </option>
              ))}
            </select>

            {/* Sort By */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="created_at">Latest</option>
              <option value="title">Title</option>
              <option value="popularity">Popularity</option>
              <option value="rating">Rating</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Modules Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, index) => (
            <Card key={index} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                  <div className="flex gap-2">
                    <div className="h-6 bg-gray-200 rounded w-16"></div>
                    <div className="h-6 bg-gray-200 rounded w-16"></div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : modules.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No modules found</h3>
            <p className="text-gray-600 mb-4">
              Try adjusting your search terms or filters to find learning modules.
            </p>
            {(userRole === 'educator' || userRole === 'admin') && (
              <Button onClick={onCreateModule}>
                Create First Module
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module) => (
            <Card key={module.id} className="hover:shadow-lg transition-shadow cursor-pointer group">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg mb-2 group-hover:text-blue-600 transition-colors">
                      {module.title}
                    </CardTitle>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      {getContentTypeIcon(module.content_type)}
                      <span>{formatCategory(module.category)}</span>
                    </div>
                  </div>
                  {(module.metadata?.fact_check_score ?? 0) >= 90 && (
                    <Shield className="h-5 w-5 text-green-600" />
                  )}
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <p className="text-gray-600 text-sm line-clamp-3">
                  {module.description}
                </p>

                {/* Progress Bar (if user has progress) */}
                {module.progress && (
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs text-gray-600">
                      <span>Progress</span>
                      <span>{module.progress.completion_percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${module.progress.completion_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                {/* Tags */}
                <div className="flex flex-wrap gap-1">
                  <Badge className={getDifficultyColor(module.difficulty)}>
                    {module.difficulty}
                  </Badge>
                  {(module.metadata?.tags ?? []).slice(0, 2).map(tag => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {((module.metadata?.tags?.length ?? 0) > 2) && (
                    <Badge variant="outline" className="text-xs">
                      +{(module.metadata?.tags?.length ?? 0) - 2}
                    </Badge>
                  )}
                </div>

                {/* Stats */}
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      <span>{formatDuration(module.estimated_duration)}</span>
                    </div>
                    {module.stats && (
                      <div className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        <span>{module.stats.total_users}</span>
                      </div>
                    )}
                  </div>
                  {module.stats && module.stats.avg_rating > 0 && (
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span>{module.stats.avg_rating.toFixed(1)}</span>
                    </div>
                  )}
                </div>

                {/* Action Button */}
                <Button 
                  onClick={() => onViewModule?.(module.id)}
                  className="w-full"
                  variant={module.progress?.is_completed ? "outline" : "default"}
                >
                  <Eye className="h-4 w-4 mr-2" />
                  {module.progress?.is_completed ? 'Review' : 'Start Learning'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}