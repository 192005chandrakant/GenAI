'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, Image as ImageIcon, Video, BookOpen } from 'lucide-react';

export interface EducationalContentSection {
  title: string;
  description: string;
  content_body: string;
  content_type: 'text' | 'image' | 'video' | 'audio' | 'interactive' | 'quiz' | 'simulation' | 'infographic' | 'document' | 'presentation';
  skill_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  estimated_duration_minutes: number;
  tags?: string[];
  keywords?: string[];
  learning_objectives?: string[];
  prerequisites?: string[];
  media_attachments?: string[]; // IDs or URLs
  external_resources?: { title?: string; url?: string }[];
}

function getIcon(type: EducationalContentSection['content_type']) {
  switch (type) {
    case 'video':
      return <Video className="h-5 w-5" />;
    case 'text':
    default:
      return <FileText className="h-5 w-5" />;
  }
}

function getLevelBadge(level: EducationalContentSection['skill_level']) {
  const map: Record<string, string> = {
    beginner: 'bg-green-100 text-green-800',
    intermediate: 'bg-yellow-100 text-yellow-800',
    advanced: 'bg-red-100 text-red-800',
    expert: 'bg-purple-100 text-purple-800',
  };
  return map[level] || 'bg-gray-100 text-gray-800';
}

export default function ContentSectionBlock({ section }: { section: EducationalContentSection }) {
  return (
    <Card className="border border-gray-200">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <CardTitle className="text-xl mb-1 flex items-center gap-2">
              {getIcon(section.content_type)}
              {section.title}
            </CardTitle>
            {section.description && (
              <p className="text-gray-600 text-sm">{section.description}</p>
            )}
          </div>
          <Badge className={getLevelBadge(section.skill_level)}>{section.skill_level}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="prose max-w-none whitespace-pre-wrap text-gray-800">
          {section.content_body}
        </div>

        {(section.tags?.length || 0) > 0 && (
          <div className="flex flex-wrap gap-2">
            {(section.tags || []).map((t) => (
              <Badge key={t} variant="outline" className="text-xs">{t}</Badge>
            ))}
          </div>
        )}

        {(section.external_resources?.length || 0) > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium">Resources</h4>
            <ul className="list-disc ml-5 text-sm text-blue-700">
              {(section.external_resources || []).map((r, i) => (
                <li key={i}>
                  <a href={r.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                    {r.title || r.url}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
