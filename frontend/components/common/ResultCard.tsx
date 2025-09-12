import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle, HelpCircle, Share2, Download } from 'lucide-react';
import { motion } from 'framer-motion';
import { CheckResponse } from '../../lib/api';
import { formatTimestamp } from '../../lib/utils';
import CredibilityBadge from './CredibilityBadge';
import CitationCard from './CitationCard';
import LearnCardComponent from './LearnCardComponent';
import EvidenceMap from '../ui/evidence-map';

interface ResultCardProps {
  result: CheckResponse;
  onShare?: () => void;
  onDownload?: () => void;
}

const ResultCard = ({ result, onShare, onDownload }: ResultCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200 max-w-4xl mx-auto"
    >
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
          <div className="flex items-center">
            <CredibilityBadge score={result.score} size="lg" />
            <div className="ml-4">
              <h2 className="text-2xl font-bold text-gray-900">{result.verdict}</h2>
              <p className="text-gray-500">
                Analyzed {formatTimestamp(result.metadata.timestamp)}
              </p>
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={onShare}
              className="btn btn-outline btn-sm flex items-center space-x-1"
            >
              <Share2 className="w-4 h-4" />
              <span>Share</span>
            </button>
            <button
              onClick={onDownload}
              className="btn btn-outline btn-sm flex items-center space-x-1"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="p-6 bg-gray-50 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Summary</h3>
        <p className="text-gray-700">{result.summary}</p>
      </div>

      {/* Main Content */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Citations */}
          <div className="lg:col-span-2">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Evidence & Sources</h3>
            <div className="space-y-4">
              {result.citations.map((citation) => (
                <CitationCard key={citation.id} citation={citation} />
              ))}
            </div>

            {result.citations.length === 0 && (
              <div className="border border-gray-200 rounded-lg p-6 flex flex-col items-center justify-center text-center">
                <HelpCircle className="w-12 h-12 text-gray-400 mb-2" />
                <h4 className="text-lg font-medium text-gray-700">No Citations Found</h4>
                <p className="text-gray-500 mt-2 max-w-md">
                  Our system couldn't find reliable sources for this content. This could mean the information is very new, or it may require further research.
                </p>
              </div>
            )}

            {/* Reasoning Section */}
            <div className="mt-8">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Analysis Reasoning</h3>
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <p className="text-gray-700 whitespace-pre-line">{result.reasoning}</p>
              </div>
            </div>

            {/* Confidence Section */}
            <div className="mt-6">
              <h4 className="font-medium text-gray-700 mb-2">Confidence Levels</h4>
              <div className="flex space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">High: {Math.round(result.confidenceBands.high * 100)}%</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">Medium: {Math.round(result.confidenceBands.mid * 100)}%</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">Low: {Math.round(result.confidenceBands.low * 100)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Learn Cards */}
          <div className="lg:col-span-1">
            <div className="sticky top-20">
              {result.learnCards.length > 0 && <LearnCardComponent cards={result.learnCards} />}
              
              {/* Claims Extracted */}
              {result.claims.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Claims Detected</h3>
                  <ul className="space-y-2">
                    {result.claims.map((claim) => (
                      <li key={claim.id} className="border rounded-lg p-3 bg-white">
                        <p className="text-gray-800">{claim.what}</p>
                        <div className="mt-1 flex flex-wrap gap-2 text-xs text-gray-500">
                          {claim.who && <span className="inline-flex items-center px-2 py-1 rounded-full bg-blue-50 text-blue-700">Who: {claim.who}</span>}
                          {claim.where && <span className="inline-flex items-center px-2 py-1 rounded-full bg-green-50 text-green-700">Where: {claim.where}</span>}
                          {claim.when && <span className="inline-flex items-center px-2 py-1 rounded-full bg-purple-50 text-purple-700">When: {claim.when}</span>}
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Processing Info */}
              <div className="mt-6 p-4 rounded-lg border border-gray-200 bg-gray-50">
                <h4 className="font-medium text-gray-700 mb-2">Analysis Information</h4>
                <div className="space-y-1 text-sm">
                  <p className="text-gray-600">Language: <span className="text-gray-900">{result.metadata.language.toUpperCase()}</span></p>
                  <p className="text-gray-600">Processing Time: <span className="text-gray-900">{result.metadata.processingTime}ms</span></p>
                  <p className="text-gray-600">Model Version: <span className="text-gray-900">{result.metadata.modelVersion}</span></p>
                  <p className="text-gray-600">Result ID: <span className="font-mono text-xs text-gray-500">{result.id}</span></p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Evidence Map Section */}
      {(result.claims.length > 0 || result.citations.length > 0) && (
        <div className="p-6 border-t border-gray-200">
          <EvidenceMap
            claims={result.claims}
            citations={result.citations}
            verdict={result.verdict}
            score={result.score}
            className="h-96"
          />
        </div>
      )}
      
      {/* Footer */}
      <div className="p-4 border-t border-gray-200 bg-gray-50 text-center text-sm text-gray-500">
        MisinfoGuard analysis results should be used as one of many inputs in your evaluation process. Always verify information with multiple sources.
      </div>
    </motion.div>
  );
};

export default ResultCard;
