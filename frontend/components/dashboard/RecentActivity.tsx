'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '../ui/badge';

const activities = [
  {
    id: 1,
    verdict: 'Misleading Content',
    summary: 'The article about "miracle cures" for COVID-19 contains several unsubstantiated claims.',
    score: 35,
    date: '2 days ago',
  },
  {
    id: 2,
    verdict: 'Factually Accurate',
    summary: 'The report on climate change statistics aligns with data from major scientific bodies.',
    score: 92,
    date: '3 days ago',
  },
  {
    id: 3,
    verdict: 'Partially False',
    summary: 'A social media post about a political candidate mixes true and false statements.',
    score: 58,
    date: '5 days ago',
  },
    {
    id: 4,
    verdict: 'Satire/Parody',
    summary: 'An article from a known satirical website was correctly identified.',
    score: 85,
    date: '6 days ago',
  },
];

export default function RecentActivity() {
  return (
    <Card className="bg-white dark:bg-gray-800 h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Recent Activity</CardTitle>
          <Button variant="link" className="text-blue-600 dark:text-blue-400">
            View All
          </Button>
        </div>
        <CardDescription>A log of your recent fact-checking analyses.</CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="space-y-4">
          {activities.map((activity) => (
            <li key={activity.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50">
              <div className="flex-1">
                <p className="font-semibold">{activity.verdict}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400 truncate max-w-md">{activity.summary}</p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">{activity.date}</p>
              </div>
              <Badge
                className={
                  activity.score > 75
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300'
                    : activity.score > 40
                    ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300'
                    : 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300'
                }
              >
                Score: {activity.score}
              </Badge>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
