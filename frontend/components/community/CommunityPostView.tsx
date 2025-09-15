'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  MessageSquare, 
  Heart, 
  Share, 
  Flag, 
  User,
  Clock,
  ThumbsUp,
  ArrowLeft,
  CheckCircle,
  AlertTriangle,
  Shield,
  ImageIcon,
  Video,
  FileText,
  ExternalLink
} from 'lucide-react';

interface CommunityPostViewProps {
  postId: string;
  onBack?: () => void;
}

export default function CommunityPostView({ 
  postId, 
  onBack 
}: CommunityPostViewProps) {
  const [post, setPost] = React.useState<any>(null);
  const [comments, setComments] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [commentText, setCommentText] = React.useState('');
  const [submittingComment, setSubmittingComment] = React.useState(false);

  React.useEffect(() => {
    const fetchPost = async () => {
      try {
        const response = await fetch(`/api/enhanced-community/posts/${postId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setPost(data);
        }
      } catch (error) {
        console.error('Error fetching post:', error);
      }
    };

    const fetchComments = async () => {
      try {
        const response = await fetch(`/api/enhanced-community/posts/${postId}/comments`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setComments(data.comments || []);
        }
      } catch (error) {
        console.error('Error fetching comments:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
    fetchComments();
  }, [postId]);

  const handleLike = async () => {
    if (!post) return;

    try {
      await fetch(`/api/enhanced-community/posts/${postId}/interactions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interaction_type: 'like'
        }),
      });

      // Update local state
      setPost(prev => ({
        ...prev,
        engagement: {
          ...prev.engagement,
          likes: prev.user_interaction?.has_liked 
            ? prev.engagement.likes - 1 
            : prev.engagement.likes + 1
        },
        user_interaction: {
          ...prev.user_interaction,
          has_liked: !prev.user_interaction?.has_liked
        }
      }));
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const handleShare = async () => {
    if (!post) return;

    if (navigator.share) {
      await navigator.share({
        title: post.title,
        text: post.content.slice(0, 100) + '...',
        url: window.location.href,
      });
    } else {
      await navigator.clipboard.writeText(window.location.href);
      // TODO: Show toast notification
    }

    // Track share
    try {
      await fetch(`/api/enhanced-community/posts/${postId}/interactions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interaction_type: 'share'
        }),
      });

      // Update local state
      setPost(prev => ({
        ...prev,
        engagement: {
          ...prev.engagement,
          shares: prev.engagement.shares + 1
        }
      }));
    } catch (error) {
      console.error('Error tracking share:', error);
    }
  };

  const handleReport = async () => {
    // TODO: Implement report modal
    console.log('Report post:', postId);
  };

  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!commentText.trim()) return;
    
    setSubmittingComment(true);

    try {
      const response = await fetch(`/api/enhanced-community/posts/${postId}/comments`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: commentText.trim()
        }),
      });

      if (response.ok) {
        const newComment = await response.json();
        setComments(prev => [newComment, ...prev]);
        setCommentText('');
        
        // Update comment count
        setPost(prev => ({
          ...prev,
          engagement: {
            ...prev.engagement,
            comments: prev.engagement.comments + 1
          }
        }));
      }
    } catch (error) {
      console.error('Error posting comment:', error);
    } finally {
      setSubmittingComment(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  const getFactCheckStatusIcon = () => {
    if (!post) return null;
    
    switch (post.fact_check_status) {
      case 'verified':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'disputed':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'false':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      default:
        return null;
    }
  };

  const getFactCheckStatusText = () => {
    if (!post) return '';
    
    switch (post.fact_check_status) {
      case 'verified':
        return 'Verified';
      case 'disputed':
        return 'Disputed';
      case 'false':
        return 'False Information';
      default:
        return 'Pending Verification';
    }
  };

  const getFactCheckStatusColor = () => {
    if (!post) return '';
    
    switch (post.fact_check_status) {
      case 'verified':
        return 'bg-green-100 text-green-800';
      case 'disputed':
        return 'bg-yellow-100 text-yellow-800';
      case 'false':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getMediaIcon = (url: string) => {
    if (url.includes('video') || url.includes('.mp4') || url.includes('.webm')) {
      return <Video className="h-5 w-5" />;
    }
    if (url.includes('image') || url.includes('.jpg') || url.includes('.png')) {
      return <ImageIcon className="h-5 w-5" />;
    }
    return <FileText className="h-5 w-5" />;
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

  if (!post) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Post not found</h2>
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
          Back to Community
        </Button>
      </div>

      {/* Post Card */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                <User className="h-5 w-5 text-gray-600" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">
                    {post.is_anonymous ? 'Anonymous User' : post.author_name}
                  </span>
                  {post.author_level && (
                    <Badge variant="outline">Level {post.author_level}</Badge>
                  )}
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="h-3 w-3" />
                  <span>{formatTimestamp(post.created_at)}</span>
                </div>
              </div>
            </div>
            
            {post.is_fact_checked && (
              <Badge className={getFactCheckStatusColor()}>
                <div className="flex items-center gap-1">
                  {getFactCheckStatusIcon()}
                  <span>{getFactCheckStatusText()}</span>
                </div>
              </Badge>
            )}
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <div>
            <h1 className="text-2xl font-bold mb-2">{post.title}</h1>
            
            <Badge className="mb-4">
              {post.post_type.charAt(0).toUpperCase() + post.post_type.slice(1)}
            </Badge>
            
            <div className="prose max-w-none whitespace-pre-wrap">
              {post.content}
            </div>
          </div>

          {/* Media Files */}
          {post.media_urls && post.media_urls.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-medium">Attached Media</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {post.media_urls.map((url: string, index: number) => {
                  const isImage = url.includes('image') || url.includes('.jpg') || url.includes('.png');
                  const isVideo = url.includes('video') || url.includes('.mp4') || url.includes('.webm');
                  
                  return (
                    <div key={index} className="border rounded-lg overflow-hidden">
                      {isImage ? (
                        <div className="aspect-video bg-gray-100 relative">
                          <img 
                            src={url} 
                            alt={`Attachment ${index + 1}`} 
                            className="absolute inset-0 w-full h-full object-contain"
                          />
                        </div>
                      ) : isVideo ? (
                        <video 
                          src={url} 
                          controls 
                          className="w-full aspect-video bg-black"
                        />
                      ) : (
                        <div className="p-4 bg-gray-50 flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {getMediaIcon(url)}
                            <span className="text-sm truncate">Attachment {index + 1}</span>
                          </div>
                          <a 
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Tags */}
          {post.tags && post.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-4">
              {post.tags.map((tag: string) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  #{tag}
                </Badge>
              ))}
            </div>
          )}

          {/* Engagement */}
          <div className="flex items-center justify-between pt-4 border-t">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLike}
                className={post.user_interaction?.has_liked ? 'text-red-600' : ''}
              >
                <Heart className={`h-4 w-4 mr-1 ${post.user_interaction?.has_liked ? 'fill-current' : ''}`} />
                {post.engagement.likes}
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => document.getElementById('comments-section')?.scrollIntoView({ behavior: 'smooth' })}
              >
                <MessageSquare className="h-4 w-4 mr-1" />
                {post.engagement.comments}
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={handleShare}
              >
                <Share className="h-4 w-4 mr-1" />
                {post.engagement.shares}
              </Button>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={handleReport}
            >
              <Flag className="h-4 w-4" />
              Report
            </Button>
          </div>

          {/* Fact Check Section */}
          {post.is_fact_checked && (
            <div className={`p-4 rounded-lg mt-6 ${
              post.fact_check_status === 'verified' ? 'bg-green-50' : 
              post.fact_check_status === 'disputed' ? 'bg-yellow-50' : 
              post.fact_check_status === 'false' ? 'bg-red-50' : 
              'bg-gray-50'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <Shield className={`h-5 w-5 ${
                  post.fact_check_status === 'verified' ? 'text-green-600' :
                  post.fact_check_status === 'disputed' ? 'text-yellow-600' :
                  post.fact_check_status === 'false' ? 'text-red-600' :
                  'text-gray-600'
                }`} />
                <h3 className="font-medium">Fact Check Results</h3>
              </div>
              
              <p className="text-gray-700 mb-2">
                {post.fact_check_summary || 'This content has been reviewed by fact-checkers.'}
              </p>
              
              {post.fact_check_sources && post.fact_check_sources.length > 0 && (
                <div className="mt-2">
                  <h4 className="text-sm font-medium mb-1">Sources:</h4>
                  <ul className="text-sm space-y-1">
                    {post.fact_check_sources.map((source: string, index: number) => (
                      <li key={index}>
                        <a 
                          href={source}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline flex items-center gap-1"
                        >
                          Source {index + 1}
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Comments Section */}
      <div id="comments-section">
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Comments ({post.engagement.comments})</CardTitle>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Comment Form */}
            {post.enable_comments && (
              <form onSubmit={handleSubmitComment} className="space-y-4">
                <textarea 
                  className="w-full border border-gray-300 rounded-md p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Add a comment..."
                  rows={3}
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  required
                />
                <div className="flex justify-end">
                  <Button 
                    type="submit" 
                    disabled={submittingComment || !commentText.trim()}
                  >
                    {submittingComment ? 'Posting...' : 'Post Comment'}
                  </Button>
                </div>
              </form>
            )}

            {!post.enable_comments && (
              <div className="text-center py-4 bg-gray-50 rounded-lg">
                <p className="text-gray-600">Comments are disabled for this post.</p>
              </div>
            )}

            {/* Comments List */}
            {post.enable_comments && (
              <div className="space-y-4">
                {comments.length === 0 ? (
                  <div className="text-center py-6">
                    <MessageSquare className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-600">Be the first to comment</p>
                  </div>
                ) : (
                  comments.map((comment: any) => (
                    <div key={comment.id} className="border-b pb-4 last:border-b-0">
                      <div className="flex items-start gap-3 mb-2">
                        <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                          <User className="h-4 w-4 text-gray-600" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">
                              {comment.is_anonymous ? 'Anonymous User' : comment.author_name}
                            </span>
                            <span className="text-xs text-gray-500">
                              {formatTimestamp(comment.created_at)}
                            </span>
                          </div>
                          <p className="text-gray-800 mt-1">{comment.content}</p>
                          
                          <div className="flex items-center gap-3 mt-2">
                            <button className="text-xs text-gray-500 hover:text-blue-600">
                              <ThumbsUp className="h-3 w-3 inline mr-1" />
                              Like {comment.likes > 0 && `(${comment.likes})`}
                            </button>
                            <button className="text-xs text-gray-500 hover:text-blue-600">
                              Reply
                            </button>
                            <button className="text-xs text-gray-500 hover:text-red-600">
                              Report
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}