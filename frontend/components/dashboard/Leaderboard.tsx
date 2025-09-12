'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

const leaderboardData = [
  { rank: 1, name: 'Alex T.', points: 2540, avatar: '/avatars/01.png' },
  { rank: 2, name: 'Maria G.', points: 2310, avatar: '/avatars/02.png' },
  { rank: 3, name: 'Sam K.', points: 2100, avatar: '/avatars/03.png' },
  { rank: 12, name: 'You', points: 1280, avatar: '/avatars/user.png', isCurrentUser: true },
];

export default function Leaderboard() {
  return (
    <Card className="bg-white dark:bg-gray-800">
      <CardHeader>
        <CardTitle>Leaderboard</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-3">
          {leaderboardData.map((user) => (
            <li
              key={user.rank}
              className={`flex items-center p-2 rounded-lg ${
                user.isCurrentUser ? 'bg-blue-50 dark:bg-blue-900/50' : ''
              }`}
            >
              <span className="text-lg font-bold w-8">{user.rank}</span>
              <Avatar className="h-9 w-9">
                <AvatarImage src={user.avatar} alt={user.name} />
                <AvatarFallback>{user.name.charAt(0)}</AvatarFallback>
              </Avatar>
              <span className="ml-3 font-medium flex-1">{user.name}</span>
              <span className="font-semibold text-gray-700 dark:text-gray-300">{user.points} pts</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
