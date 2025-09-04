import React from 'react';
import { motion } from 'framer-motion';
import { Citation } from '../../lib/api';
import { formatTimestamp, truncateText } from '../../lib/utils';
import { ExternalLink, CheckCircle2, XCircle, HelpCircle } from 'lucide-react';

interface CitationCardProps {
  citation: Citation;
  onClick?: () => void;
}

const CitationCard = ({ citation, onClick }: CitationCardProps) => {
  const getStanceColor = (stance: string) => {
    switch (stance) {
      case 'support':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'refute':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'neutral':
        return 'text-gray-600 bg-gray-50 border-gray-200';
      default:
        return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getStanceIcon = (stance: string) => {
    switch (stance) {
      case 'support':
        return <CheckCircle2 className="w-4 h-4" />;
      case 'refute':
        return <XCircle className="w-4 h-4" />;
      case 'neutral':
        return <HelpCircle className="w-4 h-4" />;
      default:
        return null;
    }
  };

  const getDomainFavicon = (domain: string) => {
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=32`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="border rounded-lg overflow-hidden bg-white hover:shadow-md transition-shadow"
      onClick={onClick}
    >
      <div className="border-b border-gray-100 p-3 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <img 
            src={getDomainFavicon(citation.domain)}
            alt={citation.domain}
            className="w-4 h-4"
            onError={(e) => {
              // Fallback if favicon fails to load
              (e.target as HTMLImageElement).src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v.01"/><path d="M12 8v4"/></svg>';
            }}
          />
          <span className="font-medium text-gray-800 truncate max-w-[180px]">
            {citation.domain}
          </span>
          {citation.publishDate && (
            <span className="text-xs text-gray-500">
              {formatTimestamp(citation.publishDate)}
            </span>
          )}
        </div>
        <div className={`px-2 py-1 text-xs font-medium rounded-full flex items-center space-x-1 ${getStanceColor(citation.stance)}`}>
          {getStanceIcon(citation.stance)}
          <span>
            {citation.stance === 'support' ? 'Supports' : 
             citation.stance === 'refute' ? 'Refutes' : 'Neutral'}
          </span>
        </div>
      </div>
      
      <div className="p-4">
        <h4 className="font-medium text-gray-900 mb-2">{truncateText(citation.title, 100)}</h4>
        <p className="text-sm text-gray-600 mb-4">
          "{truncateText(citation.snippet, 150)}"
        </p>
        
        <div className="flex items-center justify-between mt-2">
          {citation.author && (
            <span className="text-xs text-gray-500">By {citation.author}</span>
          )}
          <a
            href={citation.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-600 hover:text-blue-800 flex items-center space-x-1"
            onClick={(e) => e.stopPropagation()}
          >
            <span>View Source</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
      
      <div className="p-2 bg-gray-50 border-t border-gray-100 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className={`h-full ${
                citation.trustScore >= 80 ? 'bg-green-500' : 
                citation.trustScore >= 50 ? 'bg-yellow-500' : 
                'bg-red-500'
              }`}
              style={{ width: `${citation.trustScore}%` }}
            ></div>
          </div>
          <span className="text-xs text-gray-600">Trust score: {citation.trustScore}%</span>
        </div>
      </div>
    </motion.div>
  );
};

export default CitationCard;
