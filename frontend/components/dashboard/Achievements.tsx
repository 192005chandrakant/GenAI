'use client';

import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Award, Star, Shield } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';

type AchievementItem = {
  name: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  color: string; // Tailwind color classes
  description: string;
};

const achievements: AchievementItem[] = [
  { name: 'Fact Finder', icon: Award, color: 'text-yellow-500', description: 'Complete 10 checks' },
  { name: 'Truth Seeker', icon: Star, color: 'text-blue-500', description: 'Achieve a 90+ score' },
  { name: 'Debunker', icon: Shield, color: 'text-green-500', description: 'Identify 5 misleading articles' },
  { name: 'Fact Finder', icon: Award, color: 'text-gray-400', description: 'Complete 10 checks' },
];

export default function Achievements() {
  return (
    <Card className="bg-white dark:bg-gray-800">
      <CardHeader>
        <CardTitle>Achievements</CardTitle>
      </CardHeader>
      <CardContent>
        <TooltipProvider>
          <div className="flex justify-around">
            {achievements.map((ach, index) => {
              const Icon = ach.icon;
              return (
                <Tooltip key={index}>
                  <TooltipTrigger asChild>
                    <button
                      type="button"
                      aria-label={ach.name}
                      className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      <Icon className={`h-10 w-10 ${ach.color}`} />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="font-semibold">{ach.name}</p>
                    <p className="text-sm text-gray-500">{ach.description}</p>
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
