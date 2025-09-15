'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useRouter } from 'next/navigation';
import apiClient from '@/lib/api';
import { Loader2 } from 'lucide-react';

interface LeaderboardUser {
  rank: number;
  id: string;
  name: string;
  points: number;
  avatar?: string;
  isCurrentUser?: boolean;
}

interface LeaderboardProps {
  currentUserId?: string;
}

// Default leaderboard data if API fails
const defaultLeaderboardData: LeaderboardUser[] = [
  { rank: 1, id: '1', name: 'Alex T.', points: 2540, avatar: '/avatars/01.png' },
  { rank: 2, id: '2', name: 'Maria G.', points: 2310, avatar: '/avatars/02.png' },
  { rank: 3, id: '3', name: 'Sam K.', points: 2100, avatar: '/avatars/03.png' },
  { rank: 12, id: 'current', name: 'You', points: 1280, avatar: '/avatars/user.png', isCurrentUser: true },
];

export default function Leaderboard({ currentUserId }: LeaderboardProps) {
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardUser[]>(defaultLeaderboardData);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  
  useEffect(() => {
    fetchLeaderboard();
  }, [currentUserId]);
  
  const fetchLeaderboard = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getLeaderboard('week');
      
      // Format the data for display
      const formattedData = data.map((user: any) => ({
        rank: user.rank,
        id: user.id,
        name: user.full_name || user.name || user.email.split('@')[0],
        points: user.points,
        avatar: user.photoUrl || `/avatars/0${(user.rank % 9) + 1}.png`,
        isCurrentUser: user.id === currentUserId
      }));
      
      setLeaderboardData(formattedData);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      // Keep default data on error
    } finally {
      setIsLoading(false);
    }
  };
  const handleViewAll = () => {
    router.push('/gamification');
  };

  return (
    <Card className="bg-white dark:bg-gray-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Leaderboard</CardTitle>
          <button 
            className="text-sm text-blue-600 hover:underline"
            onClick={handleViewAll}
          >
            View All
          </button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center py-4">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          </div>
        ) : (
          <ul className="space-y-3">
            {leaderboardData.map((user) => (
              <li
                key={user.id}
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
        )}
      </CardContent>
    </Card>
  );
}
