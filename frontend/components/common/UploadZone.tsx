import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { X, Upload, FileText, Image, File, AlertCircle, Loader2, Link } from 'lucide-react';
import { formatFileSize } from '../../lib/utils';
import { Button } from '../ui/button';
import { Spinner } from '../ui/spinner';

interface UploadZoneProps {
  onFileAccepted: (file: File) => void;
  onTextInput: (text: string) => void;
  onUrlInput: (url: string) => void;
  isLoading?: boolean;
  maxSize?: number; // in bytes
  acceptedFileTypes?: string[];
  className?: string;
}

const UploadZone = ({
  onFileAccepted,
  onTextInput,
  onUrlInput,
  isLoading = false,
  maxSize = 10 * 1024 * 1024, // 10MB default
  acceptedFileTypes = ['image/*', 'application/pdf', 'text/*'],
  className = '',
}: UploadZoneProps) => {
  const [activeTab, setActiveTab] = useState<'file' | 'text' | 'url'>('file');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [error, setError] = useState<string | null>(null);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles, fileRejections } = useDropzone({
    accept: acceptedFileTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    maxSize,
    maxFiles: 1,
    onDropAccepted: (files) => {
      setError(null);
      onFileAccepted(files[0]);
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
    disabled: isLoading,
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
      {isLoading && (
        <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex items-center justify-center rounded-lg animate-fade-in">
          <div className="flex flex-col items-center">
            <Spinner size="lg" className="mb-2" />
            <p className="text-gray-700 font-medium">Analyzing content...</p>
          </div>
        </div>
      )}

      {/* File Upload */}
      {activeTab === 'file' && (
        <div 
          {...getRootProps()} 
          className={`border-2 border-dashed rounded-lg p-8 cursor-pointer transition-colors text-center relative ${
            isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
          } ${isLoading ? 'pointer-events-none opacity-50' : ''}`}
        >
          <input {...getInputProps()} />
          
          {acceptedFiles.length > 0 ? (
            <div className="flex items-center justify-center space-x-2 py-2">
              <File className="w-6 h-6 text-blue-600" />
              <span className="font-medium text-gray-900">{acceptedFiles[0].name}</span>
              <span className="text-gray-500 text-sm">({formatFileSize(acceptedFiles[0].size)})</span>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  // Clear accepted files by forcing a re-render
                  setActiveTab('text');
                  setActiveTab('file');
                }}
                className="p-1 hover:bg-gray-100 rounded-full"
                disabled={isLoading}
              >
                <X className="w-4 h-4 text-gray-500" />
              </button>
            </div>
          ) : (
            <div>
              <Upload className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <p className="text-lg font-medium text-gray-900 mb-1">Drag and drop a file here, or click to select</p>
              <p className="text-sm text-gray-600">
                Support for images, PDFs, and text files (max {formatFileSize(maxSize)})
              </p>
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
              disabled={isLoading || text.trim().length === 0}
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
              disabled={isLoading || url.trim().length === 0}
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





