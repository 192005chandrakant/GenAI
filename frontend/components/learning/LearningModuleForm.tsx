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
  Plus, 
  FileText, 
  Video, 
  Image as ImageIcon, 
  File,
  Save,
  Eye,
  AlertCircle,
  CheckCircle,
  Clock,
  Trash
} from 'lucide-react';

interface MediaFile {
  file: File;
  type: 'image' | 'video' | 'document';
  preview?: string;
  uploading?: boolean;
  uploaded?: boolean;
  url?: string;
}

interface LearningModuleFormProps {
  onSubmit?: (moduleData: any) => void;
  onCancel?: () => void;
  initialData?: any;
  mode?: 'create' | 'edit';
}

export default function LearningModuleForm({ 
  onSubmit, 
  onCancel, 
  initialData,
  mode = 'create'
}: LearningModuleFormProps) {
  const [formData, setFormData] = useState({
    title: initialData?.title || '',
    description: initialData?.description || '',
    category: initialData?.category || 'misinformation-awareness',
    difficulty: initialData?.difficulty || 'beginner',
    content_type: initialData?.content_type || 'text',
    estimated_duration: initialData?.estimated_duration || 30,
    tags: initialData?.metadata?.tags?.join(', ') || '',
    content: initialData?.content || '',
    learning_objectives: initialData?.learning_objectives?.join('\n') || '',
    is_published: initialData?.is_published || false
  });

  const [mediaFiles, setMediaFiles] = useState<MediaFile[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [objectives, setObjectives] = useState<string[]>(
    initialData?.learning_objectives || []
  );
  const [newObjective, setNewObjective] = useState('');
  const [charCount, setCharCount] = useState(initialData?.content?.length || 0);
  const maxContentLength = 10000;

  const categories = [
    { value: 'misinformation-awareness', label: 'Misinformation Awareness' },
    { value: 'fact-checking', label: 'Fact Checking' },
    { value: 'media-literacy', label: 'Media Literacy' },
    { value: 'digital-citizenship', label: 'Digital Citizenship' },
    { value: 'critical-thinking', label: 'Critical Thinking' },
    { value: 'source-verification', label: 'Source Verification' }
  ];

  const difficulties = [
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' }
  ];

  const contentTypes = [
    { value: 'text', label: 'Text-based' },
    { value: 'video', label: 'Video' },
    { value: 'interactive', label: 'Interactive' },
    { value: 'mixed', label: 'Mixed Media' }
  ];

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
      // Check file size (15MB limit)
      if (file.size > 15 * 1024 * 1024) {
        alert(`File ${file.name} is too large. Maximum size is 15MB.`);
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
  
  const addLearningObjective = () => {
    if (newObjective.trim()) {
      setObjectives(prev => [...prev, newObjective.trim()]);
      setNewObjective('');
    }
  };

  const removeLearningObjective = (index: number) => {
    setObjectives(prev => prev.filter((_, i) => i !== index));
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
          formData.append('context', 'educational');

          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/enhanced-learning/upload-media`, {
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

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    } else if (formData.description.length < 20) {
      newErrors.description = 'Description must be at least 20 characters';
    }

    if (!formData.content.trim()) {
      newErrors.content = 'Content is required';
    } else if (formData.content.length < 100) {
      newErrors.content = 'Content must be at least 100 characters';
    } else if (formData.content.length > maxContentLength) {
      newErrors.content = `Content must be less than ${maxContentLength} characters`;
    }

    if (objectives.length === 0) {
      newErrors.objectives = 'At least one learning objective is required';
    }

    if (isNaN(parseInt(formData.estimated_duration.toString())) || parseInt(formData.estimated_duration.toString()) < 1) {
      newErrors.estimated_duration = 'Duration must be a positive number';
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

      // Prepare module data
      const moduleData = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        category: formData.category,
        difficulty: formData.difficulty,
        content_type: formData.content_type,
        estimated_duration: parseInt(formData.estimated_duration.toString()),
        content: formData.content.trim(),
        learning_objectives: objectives,
        is_published: formData.is_published,
        metadata: {
          tags: formData.tags
            .split(',')
            .filter(tag => tag.trim())
            .map(tag => tag.trim()),
          media_urls: [
            ...(initialData?.metadata?.media_urls || []),
            ...validMediaUrls
          ]
        }
      };

      await onSubmit?.(moduleData);
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePreview = () => {
    // TODO: Implement preview functionality
    console.log('Preview module:', formData);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {mode === 'create' ? 'Create Learning Module' : 'Edit Learning Module'}
          </h2>
          <p className="text-gray-600">
            Design educational content to help users identify and combat misinformation
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
        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Title *
              </label>
              <Input
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="Enter module title..."
                className={errors.title ? 'border-red-500' : ''}
              />
              {errors.title && (
                <p className="text-red-500 text-xs mt-1">{errors.title}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description *
              </label>
              <Textarea
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Describe what users will learn..."
                rows={3}
                className={errors.description ? 'border-red-500' : ''}
              />
              {errors.description && (
                <p className="text-red-500 text-xs mt-1">{errors.description}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                  Difficulty *
                </label>
                <select
                  value={formData.difficulty}
                  onChange={(e) => handleInputChange('difficulty', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {difficulties.map(diff => (
                    <option key={diff.value} value={diff.value}>
                      {diff.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Content Type *
                </label>
                <select
                  value={formData.content_type}
                  onChange={(e) => handleInputChange('content_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {contentTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Estimated Duration (minutes) *
                </label>
                <Input
                  type="number"
                  min="1"
                  value={formData.estimated_duration}
                  onChange={(e) => handleInputChange('estimated_duration', parseInt(e.target.value) || 0)}
                  className={errors.estimated_duration ? 'border-red-500' : ''}
                />
                {errors.estimated_duration && (
                  <p className="text-red-500 text-xs mt-1">{errors.estimated_duration}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags (comma-separated)
                </label>
                <Input
                  value={formData.tags}
                  onChange={(e) => handleInputChange('tags', e.target.value)}
                  placeholder="fact-checking, misinformation, media literacy..."
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Learning Objectives */}
        <Card>
          <CardHeader>
            <CardTitle>Learning Objectives *</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-end gap-2">
              <div className="flex-grow">
                <Input
                  value={newObjective}
                  onChange={(e) => setNewObjective(e.target.value)}
                  placeholder="Add a specific learning objective..."
                  className={errors.objectives ? 'border-red-500' : ''}
                />
              </div>
              <Button 
                type="button"
                onClick={addLearningObjective}
                disabled={!newObjective.trim()}
              >
                <Plus className="h-4 w-4 mr-1" />
                Add
              </Button>
            </div>

            {errors.objectives && (
              <p className="text-red-500 text-xs">{errors.objectives}</p>
            )}

            {objectives.length > 0 ? (
              <ul className="space-y-2">
                {objectives.map((objective, index) => (
                  <li key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <span>{objective}</span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeLearningObjective(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 text-sm italic">
                Add specific, measurable objectives that learners will achieve after completing this module
              </p>
            )}
          </CardContent>
        </Card>
        
        {/* Module Content */}
        <Card>
          <CardHeader>
            <CardTitle>Module Content *</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Textarea
                value={formData.content}
                onChange={(e) => handleInputChange('content', e.target.value)}
                placeholder="Write the main content of your learning module here. You can use Markdown formatting."
                rows={15}
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

            <div className="text-sm text-gray-600 space-y-1">
              <p>Tips:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Use clear, concise language appropriate for your target audience</li>
                <li>Break content into logical sections with appropriate headers</li>
                <li>Include examples and practical applications where possible</li>
                <li>Support claims with credible sources</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Media Upload */}
        <Card>
          <CardHeader>
            <CardTitle>Media Resources</CardTitle>
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
                accept="image/*,video/*,.pdf,.doc,.docx,.ppt,.pptx"
                onChange={handleFileSelect}
                className="hidden"
              />
              <p className="text-xs text-gray-600 mt-2">
                Maximum file size: 15MB. Supported formats: Images, Videos, PDF, Word documents
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
                        className="w-full h-24 object-cover rounded"
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

            {/* Existing Media */}
            {initialData?.metadata?.media_urls && initialData.metadata.media_urls.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-2">Existing Media</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {initialData.metadata.media_urls.map((url: string, index: number) => (
                    <div key={`existing-${index}`} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {url.includes('image') ? (
                            <ImageIcon className="h-5 w-5" />
                          ) : url.includes('video') ? (
                            <Video className="h-5 w-5" />
                          ) : (
                            <FileText className="h-5 w-5" />
                          )}
                          <span className="text-sm truncate">
                            Resource {index + 1}
                          </span>
                        </div>
                        {/* TODO: Add functionality to remove existing media */}
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0"
                        >
                          <Trash className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Publishing Options */}
        <Card>
          <CardHeader>
            <CardTitle>Publishing Options</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_published"
                checked={formData.is_published}
                onChange={(e) => handleInputChange('is_published', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="is_published" className="text-sm font-medium text-gray-700">
                Publish module immediately
              </label>
            </div>
            <p className="text-xs text-gray-600 mt-1">
              Unpublished modules are only visible to educators and admins
            </p>
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
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                {mode === 'create' ? 'Create Module' : 'Update Module'}
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}