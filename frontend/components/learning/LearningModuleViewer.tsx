'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  BookmarkPlus, 
  Share, 
  Clock, 
  Users, 
  Star, 
  CheckCircle,
  ArrowLeft,
  ArrowRight,
  FileText,
  Video,
  Image,
  ExternalLink,
  Flag,
  ThumbsUp,
  MessageCircle
} from 'lucide-react';
import ContentSectionBlock, { EducationalContentSection } from './ContentSectionBlock';
import QuizBlock from './QuizBlock';

interface LearningModule {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  content_type: string;
  estimated_duration?: number;
  estimated_duration_minutes?: number;
  content?: string;
  content_sections?: EducationalContentSection[];
  interactive_exercises?: any[];
  learning_objectives: string[];
  metadata?: {
    tags?: string[];
    fact_check_score?: number;
    media_urls?: string[];
  };
  created_at: string;
  created_by: string;
}

interface UserProgress {
  completion_percentage: number;
  is_completed: boolean;
  time_spent: number;
  last_accessed: string;
  current_section?: number;
}

interface LearningModuleViewerProps {
  moduleId: string;
  onBack?: () => void;
  onComplete?: (moduleId: string) => void;
}

export default function LearningModuleViewer({ 
  moduleId, 
  onBack, 
  onComplete 
}: LearningModuleViewerProps) {
  const [module, setModule] = useState<LearningModule | null>(null);
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [timeSpent, setTimeSpent] = useState(0);
  const [currentSection, setCurrentSection] = useState(0);
  const [sections, setSections] = useState<string[]>([]);
  const [bookmarked, setBookmarked] = useState(false);

  useEffect(() => {
    fetchModule();
    fetchProgress();
  }, [moduleId]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying) {
      interval = setInterval(() => {
        setTimeSpent(prev => prev + 1);
        updateProgress();
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  const fetchModule = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-learning/modules/${moduleId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setModule(data);
        
        // Back-compat: split legacy string content else use structured
        const contentSections = (data.content
          ? data.content.split('\n\n').filter((section: string) => section.trim())
          : []);
        setSections(contentSections);
      }
    } catch (error) {
      console.error('Error fetching module:', error);
    }
  };

  const fetchProgress = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-learning/modules/${moduleId}/progress`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProgress(data);
        setTimeSpent(data.time_spent || 0);
        setCurrentSection(data.current_section || 0);
      }
    } catch (error) {
      console.error('Error fetching progress:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProgress = async () => {
    if (!module) return;

    const completionPercentage = Math.min(
      100,
      Math.round(((currentSection + 1) / sections.length) * 100)
    );

    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-learning/modules/${moduleId}/progress`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          completion_percentage: completionPercentage,
          time_spent: timeSpent,
          current_section: currentSection,
          is_completed: completionPercentage === 100
        }),
      });

      setProgress(prev => ({
        ...prev!,
        completion_percentage: completionPercentage,
        time_spent: timeSpent,
        current_section: currentSection,
        is_completed: completionPercentage === 100
      }));

      if (completionPercentage === 100) {
        onComplete?.(moduleId);
      }
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  const toggleBookmark = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-learning/modules/${moduleId}/bookmark`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
      });

      if (response.ok) {
        setBookmarked(!bookmarked);
      }
    } catch (error) {
      console.error('Error toggling bookmark:', error);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      await navigator.share({
        title: module?.title,
        text: module?.description,
        url: window.location.href,
      });
    } else {
      // Fallback to clipboard
      await navigator.clipboard.writeText(window.location.href);
      // TODO: Show toast notification
    }
  };

  const nextSection = () => {
    if (currentSection < sections.length - 1) {
      setCurrentSection(prev => prev + 1);
    }
  };

  const previousSection = () => {
    if (currentSection > 0) {
      setCurrentSection(prev => prev - 1);
    }
  };

  const restartModule = () => {
    setCurrentSection(0);
    setTimeSpent(0);
    setIsPlaying(false);
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getContentTypeIcon = (contentType: string) => {
    switch (contentType) {
      case 'video': return <Video className="h-5 w-5" />;
      case 'text': return <FileText className="h-5 w-5" />;
      default: return <Image className="h-5 w-5" />;
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/3"></div>
        <div className="h-64 bg-gray-200 rounded"></div>
        <div className="h-32 bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (!module) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Module not found</h2>
        <Button onClick={onBack}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Go Back
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={onBack}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Modules
        </Button>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={toggleBookmark}>
            <BookmarkPlus className={`h-4 w-4 ${bookmarked ? 'fill-current' : ''}`} />
          </Button>
          <Button variant="outline" size="sm" onClick={handleShare}>
            <Share className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Module Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-2xl mb-2">{module.title}</CardTitle>
              <p className="text-gray-600 mb-4">{module.description}</p>
              
              <div className="flex flex-wrap items-center gap-2 mb-4">
                {getContentTypeIcon(module.content_type)}
                <Badge className={getDifficultyColor(module.difficulty)}>
                  {module.difficulty}
                </Badge>
                <Badge variant="outline">
                  {module.category.replace('-', ' ')}
                </Badge>
                {(module.metadata?.tags ?? []).slice(0, 3).map(tag => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>{(module.estimated_duration ?? module.estimated_duration_minutes ?? 0)} min</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users className="h-4 w-4" />
                  <span>Time spent: {formatDuration(timeSpent)}</span>
                </div>
                {(module.metadata?.fact_check_score ?? 0) >= 90 && (
                  <div className="flex items-center gap-1 text-green-600">
                    <CheckCircle className="h-4 w-4" />
                    <span>Fact-checked</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>
      {/* Progress */}
      {progress && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Progress</span>
              <span className="text-sm text-gray-600">
                {progress.completion_percentage}% complete
              </span>
            </div>
            <Progress value={progress.completion_percentage} className="mb-4" />
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsPlaying(!isPlaying)}
                >
                  {isPlaying ? (
                    <Pause className="h-4 w-4" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={restartModule}
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
              </div>
              <span className="text-sm text-gray-600">
                Section {currentSection + 1} of {sections.length}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Learning Objectives */}
      {module.learning_objectives.length > 0 && (
        <Card className="border border-gray-200">
          <CardHeader>
            <CardTitle className="text-lg">Learning Objectives</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {module.learning_objectives.map((objective, index) => (
                <li key={index} className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>{objective}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Content */}
      <Card className="border border-gray-200">
        <CardHeader>
          <CardTitle className="text-lg">Module Content</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Structured sections or legacy content */}
          {(module.content_sections && module.content_sections.length > 0) ? (
            <div className="space-y-6">
              {module.content_sections.map((sec, i) => (
                <ContentSectionBlock key={i} section={sec as EducationalContentSection} />
              ))}
            </div>
          ) : (
            <div className="prose max-w-none">
              {sections[currentSection] && (
                <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                  {sections[currentSection]}
                </div>
              )}
            </div>
          )}

          {/* Media Files */}
          {(module.metadata?.media_urls?.length ?? 0) > 0 && (
            <div className="mt-2 space-y-4">
              <h4 className="font-medium">Additional Resources</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(module.metadata?.media_urls ?? []).map((url, index) => (
                  <div key={index} className="border rounded-lg p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Image className="h-5 w-5" />
                        <span className="text-sm">Resource {index + 1}</span>
                      </div>
                      <Button variant="ghost" size="sm" asChild>
                        <a href={url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Navigation only for legacy content */}
          {(!module.content_sections || module.content_sections.length === 0) && sections.length > 0 && (
            <div className="flex items-center justify-between mt-8 pt-6 border-t">
              <Button
                variant="outline"
                onClick={previousSection}
                disabled={currentSection === 0}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Previous
              </Button>

              {currentSection === sections.length - 1 ? (
                <Button
                  onClick={() => {
                    if (progress?.completion_percentage !== 100) {
                      updateProgress();
                    }
                  }}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Complete Module
                </Button>
              ) : (
                <Button onClick={nextSection}>
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Interactive exercises (quizzes etc.) */}
      {(module.interactive_exercises?.length ?? 0) > 0 && (
        <div className="space-y-6">
          {module.interactive_exercises?.map((ex: any, idx: number) => (
            <QuizBlock
              key={ex.id || idx}
              title={ex.title}
              instructions={ex.instructions}
              content={ex.content}
              hints={ex.hints}
              onComplete={(s, t) => {
                // Optional: hook into progress update
                console.log(`Quiz completed: ${s}/${t}`);
              }}
            />
          ))}
        </div>
      )}

      {/* Actions */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="outline" size="sm">
                <ThumbsUp className="h-4 w-4 mr-2" />
                Helpful
              </Button>
              <Button variant="outline" size="sm">
                <MessageCircle className="h-4 w-4 mr-2" />
                Discuss
              </Button>
            </div>
            <Button variant="outline" size="sm">
              <Flag className="h-4 w-4 mr-2" />
              Report Issue
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}