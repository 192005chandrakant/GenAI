'use client';

import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { 
  Upload, 
  X, 
  Save, 
  Eye,
  Image as ImageIcon,
  Video,
  File,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';

interface MediaFile {
  file: File;
  type: 'image' | 'video' | 'document';
  preview?: string;
  uploading?: boolean;
  uploaded?: boolean;
  url?: string;
}

interface CommunityPostFormProps {
  onSubmit?: (postData: any) => void;
  onCancel?: () => void;
  initialData?: any;
  mode?: 'create' | 'edit';
  userRole?: 'user' | 'moderator' | 'admin';
}

export default function CommunityPostForm({ 
  onSubmit, 
  onCancel, 
  initialData,
  mode = 'create'
}: CommunityPostFormProps) {
  const [formData, setFormData] = useState({
    title: initialData?.title || '',
    content: initialData?.content || '',
    post_type: initialData?.post_type || 'discussion',
    category: initialData?.category || 'misinformation-awareness',
    tags: initialData?.tags?.join(', ') || '',
    is_anonymous: initialData?.is_anonymous || false,
    enable_comments: initialData?.enable_comments ?? true,
    request_fact_check: initialData?.request_fact_check || false
  });

  const [mediaFiles, setMediaFiles] = useState<MediaFile[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [charCount, setCharCount] = useState(initialData?.content?.length || 0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const postTypes = [
    { value: 'discussion', label: 'Discussion', description: 'Start a general discussion' },
    { value: 'question', label: 'Question', description: 'Ask the community for help' },
    { value: 'resource', label: 'Resource', description: 'Share useful resources' },
    { value: 'fact-check', label: 'Fact Check', description: 'Request fact-checking help' },
    { value: 'experience', label: 'Experience', description: 'Share your experiences' }
  ];

  const categories = [
    { value: 'misinformation-awareness', label: 'Misinformation Awareness' },
    { value: 'fact-checking', label: 'Fact Checking' },
    { value: 'media-literacy', label: 'Media Literacy' },
    { value: 'digital-citizenship', label: 'Digital Citizenship' },
    { value: 'news-analysis', label: 'News Analysis' },
    { value: 'educational-resources', label: 'Educational Resources' }
  ];

  const maxContentLength = 5000;

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    if (field === 'content') {
      setCharCount(value.length);
    }
    
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    
    files.forEach(file => {
      // Check file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        alert(`File ${file.name} is too large. Maximum size is 10MB.`);
        return;
      }

      const mediaFile: MediaFile = {
        file,
        type: getFileType(file),
        uploading: false,
        uploaded: false
      };

      // Create preview for images
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          mediaFile.preview = e.target?.result as string;
          setMediaFiles(prev => [...prev, mediaFile]);
        };
        reader.readAsDataURL(file);
      } else {
        setMediaFiles(prev => [...prev, mediaFile]);
      }
    });

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getFileType = (file: File): 'image' | 'video' | 'document' => {
    if (file.type.startsWith('image/')) return 'image';
    if (file.type.startsWith('video/')) return 'video';
    return 'document';
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'image': return <ImageIcon className="h-5 w-5" />;
      case 'video': return <Video className="h-5 w-5" />;
      default: return <File className="h-5 w-5" />;
    }
  };

  const removeMediaFile = (index: number) => {
    setMediaFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadMediaFiles = async () => {
    const uploadPromises = mediaFiles
      .filter(media => !media.uploaded)
      .map(async (media, index) => {
        const mediaIndex = mediaFiles.findIndex(m => m === media);
        
        // Update uploading state
        setMediaFiles(prev => prev.map((m, i) => 
          i === mediaIndex ? { ...m, uploading: true } : m
        ));

        try {
          const formData = new FormData();
          formData.append('file', media.file);
          formData.append('media_type', media.type);
          formData.append('context', 'community');

          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-community/upload-media`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            },
            body: formData
          });

          if (response.ok) {
            const result = await response.json();
            
            // Update uploaded state
            setMediaFiles(prev => prev.map((m, i) => 
              i === mediaIndex ? { 
                ...m, 
                uploading: false, 
                uploaded: true, 
                url: result.secure_url 
              } : m
            ));

            return result.secure_url;
          } else {
            throw new Error('Upload failed');
          }
        } catch (error) {
          console.error('Error uploading file:', error);
          
          // Update error state
          setMediaFiles(prev => prev.map((m, i) => 
            i === mediaIndex ? { ...m, uploading: false, uploaded: false } : m
          ));
          
          return null;
        }
      });

    return Promise.all(uploadPromises);
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    } else if (formData.title.length < 5) {
      newErrors.title = 'Title must be at least 5 characters';
    }

    if (!formData.content.trim()) {
      newErrors.content = 'Content is required';
    } else if (formData.content.length < 10) {
      newErrors.content = 'Content must be at least 10 characters';
    } else if (formData.content.length > maxContentLength) {
      newErrors.content = `Content must be less than ${maxContentLength} characters`;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Upload media files first
      const mediaUrls = await uploadMediaFiles();
      const validMediaUrls = mediaUrls.filter(url => url !== null);

      // Prepare post data
      const postData = {
        title: formData.title.trim(),
        content: formData.content.trim(),
        post_type: formData.post_type,
        category: formData.category,
        tags: formData.tags
          .split(',')
          .filter(tag => tag.trim())
          .map(tag => tag.trim()),
        media_uploads: validMediaUrls,
        allow_comments: formData.enable_comments,
        requires_fact_check: formData.request_fact_check
      };

      await onSubmit?.(postData);
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePreview = () => {
    // TODO: Implement preview functionality
    console.log('Preview post:', formData);
  };

  const selectedPostType = postTypes.find(type => type.value === formData.post_type);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {mode === 'create' ? 'Create Community Post' : 'Edit Post'}
          </h2>
          <p className="text-gray-600">
            Share your thoughts, ask questions, or contribute resources to the community
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handlePreview}>
            <Eye className="h-4 w-4 mr-2" />
            Preview
          </Button>
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Post Type Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Post Type</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {postTypes.map(type => (
                <div
                  key={type.value}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    formData.post_type === type.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleInputChange('post_type', type.value)}
                >
                  <h4 className="font-medium mb-1">{type.label}</h4>
                  <p className="text-sm text-gray-600">{type.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Post Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Title *
              </label>
              <Input
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder={`Enter your ${selectedPostType?.label.toLowerCase()} title...`}
                className={errors.title ? 'border-red-500' : ''}
              />
              {errors.title && (
                <p className="text-red-500 text-xs mt-1">{errors.title}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Content *
              </label>
              <Textarea
                value={formData.content}
                onChange={(e) => handleInputChange('content', e.target.value)}
                placeholder="Share your thoughts, ask your question, or provide detailed information..."
                rows={8}
                className={errors.content ? 'border-red-500' : ''}
              />
              <div className="flex justify-between items-center mt-1">
                {errors.content && (
                  <p className="text-red-500 text-xs">{errors.content}</p>
                )}
                <p className={`text-xs ml-auto ${
                  charCount > maxContentLength ? 'text-red-500' : 'text-gray-500'
                }`}>
                  {charCount}/{maxContentLength}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category *
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => handleInputChange('category', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {categories.map(cat => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags (comma-separated)
                </label>
                <Input
                  value={formData.tags}
                  onChange={(e) => handleInputChange('tags', e.target.value)}
                  placeholder="misinformation, fact-check, news..."
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Media Upload */}
        <Card>
          <CardHeader>
            <CardTitle>Media Attachments</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Button
                type="button"
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
                className="w-full border-dashed border-2 py-8"
              >
                <Upload className="h-6 w-6 mr-2" />
                Click to upload images, videos, or documents
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,video/*,.pdf,.doc,.docx"
                onChange={handleFileSelect}
                className="hidden"
              />
              <p className="text-xs text-gray-600 mt-2">
                Maximum file size: 10MB. Supported formats: Images, Videos, PDF, Word documents
              </p>
            </div>

            {mediaFiles.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {mediaFiles.map((media, index) => (
                  <div key={index} className="border rounded-lg p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getFileIcon(media.type)}
                        <span className="text-sm font-medium truncate">
                          {media.file.name}
                        </span>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeMediaFile(index)}
                        className="h-6 w-6 p-0"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>

                    {media.preview && (
                      <img
                        src={media.preview}
                        alt="Preview"
                        className="w-full h-20 object-cover rounded"
                      />
                    )}

                    <div className="flex items-center gap-2 text-xs">
                      {media.uploading && (
                        <>
                          <Clock className="h-3 w-3 animate-spin" />
                          <span>Uploading...</span>
                        </>
                      )}
                      {media.uploaded && (
                        <>
                          <CheckCircle className="h-3 w-3 text-green-600" />
                          <span className="text-green-600">Uploaded</span>
                        </>
                      )}
                      {!media.uploading && !media.uploaded && (
                        <>
                          <AlertCircle className="h-3 w-3 text-orange-600" />
                          <span className="text-orange-600">Pending</span>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Post Options */}
        <Card>
          <CardHeader>
            <CardTitle>Post Options</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.enable_comments}
                  onChange={(e) => handleInputChange('enable_comments', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium">Enable comments</span>
              </label>

              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.is_anonymous}
                  onChange={(e) => handleInputChange('is_anonymous', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium">Post anonymously</span>
              </label>

              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.request_fact_check}
                  onChange={(e) => handleInputChange('request_fact_check', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium">Request fact-checking</span>
              </label>
            </div>

            <div className="text-xs text-gray-600 space-y-1">
              <p>• Anonymous posts hide your identity from other users</p>
              <p>• Fact-checking requests will be reviewed by moderators</p>
              <p>• All posts are subject to community guidelines</p>
            </div>
          </CardContent>
        </Card>

        {/* Submit Button */}
        <div className="flex justify-end">
          <Button
            type="submit"
            disabled={isSubmitting}
            className="min-w-32"
          >
            {isSubmitting ? (
              <>
                <Clock className="h-4 w-4 mr-2 animate-spin" />
                Publishing...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                {mode === 'create' ? 'Publish Post' : 'Update Post'}
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}