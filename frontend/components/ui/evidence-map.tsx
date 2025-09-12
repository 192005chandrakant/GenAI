'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Network, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  ExternalLink, 
  Calendar,
  User,
  Globe,
  Zap,
  Info
} from 'lucide-react';
import { Citation, Claim } from '@/lib/api';

interface EvidenceMapProps {
  claims: Claim[];
  citations: Citation[];
  verdict: string;
  score: number;
  className?: string;
}

interface Node {
  id: string;
  type: 'main' | 'claim' | 'citation';
  data: any;
  x: number;
  y: number;
  connections: string[];
}

interface Connection {
  from: string;
  to: string;
  type: 'support' | 'refute' | 'neutral';
  strength: number;
}

export default function EvidenceMap({ 
  claims, 
  citations, 
  verdict, 
  score, 
  className = '' 
}: EvidenceMapProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    generateMapData();
  }, [claims, citations]);

  useEffect(() => {
    const handleResize = () => {
      if (svgRef.current) {
        const rect = svgRef.current.getBoundingClientRect();
        setDimensions({ width: rect.width, height: rect.height });
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const generateMapData = () => {
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    
    // Create main content node
    const mainNode: Node = {
      id: 'main',
      type: 'main',
      data: { verdict, score },
      x: centerX,
      y: centerY,
      connections: []
    };

    // Create claim nodes in a circle around the main node
    const claimNodes: Node[] = claims.map((claim, index) => {
      const angle = (index * 2 * Math.PI) / Math.max(claims.length, 1);
      const radius = 150;
      return {
        id: `claim-${claim.id}`,
        type: 'claim',
        data: claim,
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius,
        connections: ['main']
      };
    });

    // Create citation nodes around claims
    const citationNodes: Node[] = [];
    const newConnections: Connection[] = [];

    claims.forEach((claim, claimIndex) => {
      // Find citations that relate to this claim
      const relatedCitations = citations.filter(citation => 
        citation.snippet.toLowerCase().includes(claim.what.toLowerCase()) ||
        claim.what.toLowerCase().includes(citation.title.toLowerCase())
      );

      relatedCitations.forEach((citation, citIndex) => {
        const claimNode = claimNodes[claimIndex];
        if (!claimNode) return;

        const angle = (citIndex * 2 * Math.PI) / Math.max(relatedCitations.length, 1);
        const radius = 100;
        
        const citationNode: Node = {
          id: `citation-${citation.id}`,
          type: 'citation',
          data: citation,
          x: claimNode.x + Math.cos(angle) * radius,
          y: claimNode.y + Math.sin(angle) * radius,
          connections: [`claim-${claim.id}`]
        };

        citationNodes.push(citationNode);

        // Add connection
        newConnections.push({
          from: `claim-${claim.id}`,
          to: `citation-${citation.id}`,
          type: citation.stance,
          strength: citation.trustScore
        });
      });

      // Connect claims to main node
      newConnections.push({
        from: 'main',
        to: `claim-${claim.id}`,
        type: 'neutral',
        strength: claim.confidence
      });
    });

    setNodes([mainNode, ...claimNodes, ...citationNodes]);
    setConnections(newConnections);
  };

  const getNodeColor = (node: Node) => {
    switch (node.type) {
      case 'main':
        return score > 70 ? '#10b981' : score > 40 ? '#f59e0b' : '#ef4444';
      case 'claim':
        return node.data.confidence > 0.7 ? '#3b82f6' : '#6b7280';
      case 'citation':
        return node.data.stance === 'support' ? '#10b981' : 
               node.data.stance === 'refute' ? '#ef4444' : '#6b7280';
      default:
        return '#6b7280';
    }
  };

  const getConnectionColor = (connection: Connection) => {
    switch (connection.type) {
      case 'support':
        return '#10b981';
      case 'refute':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const renderNode = (node: Node) => {
    const color = getNodeColor(node);
    const radius = node.type === 'main' ? 20 : node.type === 'claim' ? 15 : 10;

    return (
      <g key={node.id}>
        <motion.circle
          cx={node.x}
          cy={node.y}
          r={radius}
          fill={color}
          stroke="#fff"
          strokeWidth={2}
          className="cursor-pointer hover:opacity-80"
          onClick={() => setSelectedNode(node)}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        />
        {node.type === 'main' && (
          <text
            x={node.x}
            y={node.y + 35}
            textAnchor="middle"
            className="text-sm font-medium fill-current text-gray-700 dark:text-gray-300"
          >
            Content
          </text>
        )}
      </g>
    );
  };

  const renderConnection = (connection: Connection) => {
    const fromNode = nodes.find(n => n.id === connection.from);
    const toNode = nodes.find(n => n.id === connection.to);
    
    if (!fromNode || !toNode) return null;

    const color = getConnectionColor(connection);
    const opacity = connection.strength;

    return (
      <line
        key={`${connection.from}-${connection.to}`}
        x1={fromNode.x}
        y1={fromNode.y}
        x2={toNode.x}
        y2={toNode.y}
        stroke={color}
        strokeWidth={2}
        strokeOpacity={opacity}
        strokeDasharray={connection.type === 'refute' ? '5,5' : 'none'}
      />
    );
  };

  const renderNodeDetails = () => {
    if (!selectedNode) return null;

    const { type, data } = selectedNode;

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="absolute top-4 right-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4 max-w-sm z-10"
      >
        <div className="flex items-start justify-between mb-3">
          <h3 className="font-medium text-gray-900 dark:text-white">
            {type === 'main' ? 'Content Analysis' : 
             type === 'claim' ? 'Claim' : 'Source'}
          </h3>
          <button
            onClick={() => setSelectedNode(null)}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            ×
          </button>
        </div>

        {type === 'main' && (
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <div 
                className={`w-3 h-3 rounded-full ${
                  data.score > 70 ? 'bg-green-500' : 
                  data.score > 40 ? 'bg-yellow-500' : 'bg-red-500'
                }`} 
              />
              <span className="text-sm text-gray-600 dark:text-gray-300">
                Score: {data.score}%
              </span>
            </div>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              {data.verdict}
            </p>
          </div>
        )}

        {type === 'claim' && (
          <div className="space-y-2">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              {data.what}
            </p>
            <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
              <User className="w-3 h-3" />
              <span>{data.who || 'Unknown'}</span>
            </div>
            <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
              <Zap className="w-3 h-3" />
              <span>Confidence: {Math.round(data.confidence * 100)}%</span>
            </div>
          </div>
        )}

        {type === 'citation' && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white">
              {data.title}
            </h4>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {data.snippet}
            </p>
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center space-x-1">
                <Globe className="w-3 h-3" />
                <span className="text-gray-500 dark:text-gray-400">{data.domain}</span>
              </div>
              <div className={`flex items-center space-x-1 ${
                data.stance === 'support' ? 'text-green-600' :
                data.stance === 'refute' ? 'text-red-600' : 'text-gray-600'
              }`}>
                {data.stance === 'support' ? <CheckCircle2 className="w-3 h-3" /> :
                 data.stance === 'refute' ? <XCircle className="w-3 h-3" /> :
                 <AlertTriangle className="w-3 h-3" />}
                <span>{data.stance}</span>
              </div>
            </div>
            {data.url && (
              <a
                href={data.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-1 text-xs text-blue-600 dark:text-blue-400 hover:underline"
              >
                <ExternalLink className="w-3 h-3" />
                <span>View source</span>
              </a>
            )}
          </div>
        )}
      </motion.div>
    );
  };

  return (
    <div className={`relative bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <Network className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Evidence Map
          </h3>
        </div>
        <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-300">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-500 rounded-full" />
            <span>Claims ({claims.length})</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-500 rounded-full" />
            <span>Supporting</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-red-500 rounded-full" />
            <span>Refuting</span>
          </div>
        </div>
      </div>

      {/* Map SVG */}
      <div className="relative h-96 p-4">
        <svg
          ref={svgRef}
          width="100%"
          height="100%"
          className="bg-white dark:bg-gray-800 rounded"
        >
          {/* Render connections first (behind nodes) */}
          {connections.map(renderConnection)}
          
          {/* Render nodes */}
          {nodes.map(renderNode)}
        </svg>

        {/* Node details panel */}
        <AnimatePresence>
          {renderNodeDetails()}
        </AnimatePresence>

        {/* Instructions */}
        {!selectedNode && (
          <div className="absolute bottom-4 left-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
            <div className="flex items-center space-x-2 text-sm text-blue-700 dark:text-blue-300">
              <Info className="w-4 h-4" />
              <span>Click on nodes to explore claims and sources</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
