'use client';

import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Award, Star, Shield, Check, TrendingUp, Medal, Target, Badge as BadgeIcon } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';
import { Progress } from '../ui/progress';
import { useRouter } from 'next/navigation';

interface Achievement {
  id: string;
  name: string;
  icon?: string;
  color?: string;
  description: string;
  achieved: boolean;
  progress?: number;
}

interface AchievementsProps {
  achievements?: Achievement[];
}

// Map icon strings from API to actual Lucide icons
const iconMap: Record<string, React.ReactNode> = {
  'award': <Award />,
  'star': <Star />,
  'shield': <Shield />,
  'check': <Check />,
  'trending-up': <TrendingUp />,
  'medal': <Medal />,
  'target': <Target />,
  'badge': <BadgeIcon />
};

// Default achievements if none are provided
const defaultAchievements: Achievement[] = [
  { id: '1', name: 'Fact Finder', icon: 'award', color: 'text-yellow-500', description: 'Complete 10 checks', achieved: true },
  { id: '2', name: 'Truth Seeker', icon: 'star', color: 'text-blue-500', description: 'Achieve a 90+ score', achieved: true },
  { id: '3', name: 'Debunker', icon: 'shield', color: 'text-green-500', description: 'Identify 5 misleading articles', achieved: true },
  { id: '4', name: 'Master Analyst', icon: 'target', color: 'text-gray-400', description: 'Complete 50 checks', achieved: false, progress: 60 },
];

export default function Achievements({ achievements = defaultAchievements }: AchievementsProps) {
  const router = useRouter();
  
  const handleViewAllAchievements = () => {
    router.push('/gamification');
  };

  return (
    <Card className="bg-white dark:bg-gray-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Achievements</CardTitle>
          <button 
            className="text-sm text-blue-600 hover:underline"
            onClick={handleViewAllAchievements}
          >
            View All
          </button>
        </div>
      </CardHeader>
      <CardContent>
        <TooltipProvider>
          <div className="flex flex-wrap justify-around gap-2">
            {achievements.map((ach) => {
              // Get icon from map or use Award as default
              const IconComponent = ach.icon && iconMap[ach.icon] ? 
                iconMap[ach.icon] : 
                <Award />;
              
              return (
                <Tooltip key={ach.id}>
                  <TooltipTrigger asChild>
                    <div className="flex flex-col items-center">
                      <button
                        type="button"
                        aria-label={ach.name}
                        className={`p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                          !ach.achieved && 'opacity-50'
                        }`}
                      >
                        <div className={`h-10 w-10 ${ach.color || 'text-gray-500'}`}>
                          {IconComponent}
                        </div>
                      </button>
                      {ach.progress !== undefined && !ach.achieved && (
                        <div className="w-12 mt-1">
                          <Progress value={ach.progress} className="h-1" />
                        </div>
                      )}
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>
                    <div className="space-y-1">
                      <p className="font-semibold">
                        {ach.name} 
                        {ach.achieved && <span className="ml-1 text-green-500">✓</span>}
                      </p>
                      <p className="text-sm text-gray-500">{ach.description}</p>
                      {ach.progress !== undefined && !ach.achieved && (
                        <div className="flex items-center gap-2">
                          <Progress value={ach.progress} className="h-1 flex-grow" />
                          <span className="text-xs">{ach.progress}%</span>
                        </div>
                      )}
                    </div>
                  </TooltipContent>
                </Tooltip>
              );
            })}
          </div>
        </TooltipProvider>
      </CardContent>
    </Card>
  );
}
