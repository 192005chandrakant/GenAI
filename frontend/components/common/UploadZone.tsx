import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { X, Upload, FileText, Image, File, AlertCircle, Link } from 'lucide-react';
import { formatFileSize } from '../../lib/utils';
import { Button } from '../ui/button';
import { Spinner } from '../ui/spinner';
import { apiClient } from '../../lib/api';
import { toast } from 'react-hot-toast';

interface UploadZoneProps {
  onFileAccepted: (file: File) => void;
  onTextInput: (text: string) => void;
  onUrlInput: (url: string) => void;
  isLoading?: boolean;
  maxSize?: number; // in bytes
  acceptedFileTypes?: string[];
  className?: string;
  enableImageTextExtraction?: boolean; // OCR functionality
}

const UploadZone = ({
  onFileAccepted,
  onTextInput,
  onUrlInput,
  isLoading = false,
  maxSize = 10 * 1024 * 1024, // 10MB default
  acceptedFileTypes = ['image/*', 'application/pdf', 'text/*'],
  className = '',
  enableImageTextExtraction = true,
}: UploadZoneProps) => {
  const [activeTab, setActiveTab] = useState<'file' | 'text' | 'url'>('file');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [isExtracting, setIsExtracting] = useState(false);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: acceptedFileTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    maxSize,
    maxFiles: 1,
    onDropAccepted: async (files) => {
      setError(null);
      const file = files[0];
      setUploadedFile(file);
      
      try {
        // Upload file to Cloudinary
        let uploadResult;
        if (file.type.startsWith('image/')) {
          uploadResult = await apiClient.uploadImage(file, { optimize: true });
        } else {
          uploadResult = await apiClient.uploadDocument(file);
        }
        
        setUploadResult(uploadResult);
        
        // If it's an image and OCR is enabled, try to extract text
        if (file.type.startsWith('image/') && enableImageTextExtraction) {
          setIsExtracting(true);
          try {
            const ocrResult = await apiClient.extractTextFromImage(file);
            if (ocrResult.success && ocrResult.extracted_text?.trim()) {
              toast.success('Text extracted from image successfully!');
              // Auto-fill the text tab with extracted text
              setText(ocrResult.extracted_text);
              setActiveTab('text');
            }
          } catch (ocrError) {
            console.warn('OCR extraction failed:', ocrError);
            // Don't show error for OCR failure, just continue with file upload
          } finally {
            setIsExtracting(false);
          }
        }
        
        // Call the original handler
        onFileAccepted(file);
        
      } catch (uploadError) {
        console.error('Upload error:', uploadError);
        setError('Failed to upload file. Please try again.');
        toast.error('Upload failed. Please try again.');
      }
    },
    onDropRejected: (rejections) => {
      const rejection = rejections[0];
      if (rejection?.errors[0]?.code === 'file-too-large') {
        setError(`File is too large. Maximum size is ${formatFileSize(maxSize)}.`);
      } else if (rejection?.errors[0]?.code === 'file-invalid-type') {
        setError('Invalid file type. Please upload an image, PDF, or text file.');
      } else {
        setError('Error uploading file. Please try again.');
      }
    },
    disabled: isLoading || isExtracting,
  });

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim().length > 0) {
      setError(null);
      onTextInput(text);
    } else {
      setError('Please enter some text to analyze.');
    }
  };

  const handleUrlSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Simple URL validation
    const urlPattern = /^(https?:\/\/)(www\.)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$/i;
    if (urlPattern.test(url)) {
      setError(null);
      onUrlInput(url);
    } else {
      setError('Please enter a valid URL.');
    }
  };

  const clearUploadedFile = () => {
    setUploadedFile(null);
    setUploadResult(null);
    setError(null);
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <Image className="w-6 h-6 text-blue-600" />;
    } else if (file.type.includes('pdf')) {
      return <FileText className="w-6 h-6 text-red-600" />;
    } else {
      return <File className="w-6 h-6 text-gray-600" />;
    }
  };

  return (
    <div className={`w-full relative ${className}`}>
      {/* Tab Navigation */}
      <div className="flex mb-4 border-b">
        <button
          className={`px-4 py-2 flex items-center ${
            activeTab === 'file' 
              ? 'text-blue-600 border-b-2 border-blue-600 font-medium' 
              : 'text-gray-600 hover:text-blue-600'
          }`}
          onClick={() => {
            setActiveTab('file');
            setError(null);
          }}
          disabled={isLoading}
        >
          <Upload className="w-4 h-4 mr-2" />
          <span>Upload File</span>
        </button>
        <button
          className={`px-4 py-2 flex items-center ${
            activeTab === 'text' 
              ? 'text-blue-600 border-b-2 border-blue-600 font-medium' 
              : 'text-gray-600 hover:text-blue-600'
          }`}
          onClick={() => {
            setActiveTab('text');
            setError(null);
          }}
          disabled={isLoading}
        >
          <FileText className="w-4 h-4 mr-2" />
          <span>Enter Text</span>
        </button>
        <button
          className={`px-4 py-2 flex items-center ${
            activeTab === 'url' 
              ? 'text-blue-600 border-b-2 border-blue-600 font-medium' 
              : 'text-gray-600 hover:text-blue-600'
          }`}
          onClick={() => {
            setActiveTab('url');
            setError(null);
          }}
          disabled={isLoading}
        >
          <Link className="w-4 h-4 mr-2" />
          <span>Enter URL</span>
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg flex items-start animate-fade-in">
          <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
          <button 
            onClick={() => setError(null)}
            className="ml-auto"
          >
            <X className="w-5 h-5 text-red-500 hover:text-red-700" />
          </button>
        </div>
      )}

      {/* Loading Indicator */}
      {(isLoading || isExtracting) && (
        <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex items-center justify-center rounded-lg animate-fade-in">
          <div className="flex flex-col items-center">
            <Spinner size="lg" className="mb-2" />
            <p className="text-gray-700 font-medium">
              {isExtracting ? 'Extracting text from image...' : 'Analyzing content...'}
            </p>
          </div>
        </div>
      )}

      {/* File Upload */}
      {activeTab === 'file' && (
        <div 
          {...getRootProps()} 
          className={`border-2 border-dashed rounded-lg p-8 cursor-pointer transition-colors text-center relative ${
            isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
          } ${isLoading || isExtracting ? 'pointer-events-none opacity-50' : ''}`}
        >
          <input {...getInputProps()} />
          
          {uploadedFile ? (
            <div className="space-y-4">
              <div className="flex items-center justify-center space-x-2 py-2">
                {getFileIcon(uploadedFile)}
                <span className="font-medium text-gray-900">{uploadedFile.name}</span>
                <span className="text-gray-500 text-sm">({formatFileSize(uploadedFile.size)})</span>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    clearUploadedFile();
                  }}
                  className="p-1 hover:bg-gray-100 rounded-full"
                  disabled={isLoading || isExtracting}
                >
                  <X className="w-4 h-4 text-gray-500" />
                </button>
              </div>
              
              {uploadResult && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-green-700 text-sm font-medium">File uploaded successfully</span>
                  </div>
                  {uploadResult.url && (
                    <a 
                      href={uploadResult.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-xs mt-1 block truncate"
                    >
                      View uploaded file
                    </a>
                  )}
                </div>
              )}
              
              {uploadedFile.type.startsWith('image/') && enableImageTextExtraction && (
                <div className="text-sm text-gray-600 bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <div className="flex items-start space-x-2">
                    <Image className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-blue-900">Image Text Extraction</p>
                      <p>We'll automatically extract any text from this image for analysis.</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div>
              <Upload className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <p className="text-lg font-medium text-gray-900 mb-1">Drag and drop a file here, or click to select</p>
              <p className="text-sm text-gray-600">
                Support for images, PDFs, and text files (max {formatFileSize(maxSize)})
              </p>
              {enableImageTextExtraction && (
                <p className="text-xs text-blue-600 mt-2">
                  ✨ Text will be automatically extracted from uploaded images
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Text Input */}
      {activeTab === 'text' && (
        <form onSubmit={handleTextSubmit}>
          <div className="space-y-4">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full h-40 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              placeholder="Paste or type the text you want to analyze..."
              disabled={isLoading}
            />
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading || isExtracting || text.trim().length === 0}
              loading={isLoading}
            >
              {isLoading ? 'Analyzing...' : 'Analyze Text'}
            </Button>
          </div>
        </form>
      )}

      {/* URL Input */}
      {activeTab === 'url' && (
        <form onSubmit={handleUrlSubmit}>
          <div className="space-y-4">
            <div>
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter a URL to analyze (e.g., https://example.com/article)"
                disabled={isLoading}
              />
              <p className="mt-2 text-sm text-gray-600">
                We'll fetch the content from this URL and analyze it for potential misinformation.
              </p>
            </div>
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading || isExtracting || url.trim().length === 0}
              loading={isLoading}
            >
              {isLoading ? 'Fetching and Analyzing...' : 'Analyze URL'}
            </Button>
          </div>
        </form>
      )}
    </div>
  );
};

export default UploadZone;