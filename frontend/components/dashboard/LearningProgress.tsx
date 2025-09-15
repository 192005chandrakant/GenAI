'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';

interface LearningModule {
  id: string;
  title: string;
  progress: number;
}

interface LearningProgressProps {
  modules?: LearningModule[];
  isLoading?: boolean;
}

// Default courses if none are provided
const defaultModules: LearningModule[] = [
  {
    id: '1',
    title: 'Introduction to Fact-Checking',
    progress: 100,
  },
  {
    id: '2',
    title: 'Identifying Media Bias',
    progress: 75,
  },
  {
    id: '3',
    title: 'Advanced Source Verification',
    progress: 40,
  },
];

export default function LearningProgress({ modules = defaultModules, isLoading = false }: LearningProgressProps) {
  const router = useRouter();
  
  const handleExploreCourses = () => {
    router.push('/learn');
  };
  
  const handleModuleClick = (moduleId: string) => {
    router.push(`/learn/${moduleId}`);
  };

  return (
    <Card className="bg-white dark:bg-gray-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Learning Progress</CardTitle>
            <CardDescription>Your progress in our learning modules.</CardDescription>
          </div>
          <Button 
            variant="outline"
            onClick={handleExploreCourses}
          >
            Explore Courses
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center py-4">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          </div>
        ) : modules.length > 0 ? (
          <ul className="space-y-4">
            {modules.map((module) => (
              <li 
                key={module.id}
                className="cursor-pointer" 
                onClick={() => handleModuleClick(module.id)}
              >
                <div className="flex justify-between items-center mb-1">
                  <p className="font-medium">{module.title}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{module.progress}%</p>
                </div>
                <Progress value={module.progress} />
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">No learning modules found</p>
            <Button onClick={handleExploreCourses}>Start Learning</Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
