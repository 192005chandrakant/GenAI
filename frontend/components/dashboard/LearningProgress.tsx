'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';

const courses = [
  {
    title: 'Introduction to Fact-Checking',
    progress: 100,
  },
  {
    title: 'Identifying Media Bias',
    progress: 75,
  },
  {
    title: 'Advanced Source Verification',
    progress: 40,
  },
];

export default function LearningProgress() {
  return (
    <Card className="bg-white dark:bg-gray-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Learning Progress</CardTitle>
            <CardDescription>Your progress in our learning modules.</CardDescription>
          </div>
          <Button variant="outline">Explore Courses</Button>
        </div>
      </CardHeader>
      <CardContent>
        <ul className="space-y-4">
          {courses.map((course, index) => (
            <li key={index}>
              <div className="flex justify-between items-center mb-1">
                <p className="font-medium">{course.title}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{course.progress}%</p>
              </div>
              <Progress value={course.progress} />
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
