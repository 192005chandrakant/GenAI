import { NextResponse } from 'next/server';

// Mock leaderboard data
const mockLeaderboardData = [
  { rank: 1, id: 'user1', name: 'Alex T.', points: 2540, photoUrl: '/avatars/01.png' },
  { rank: 2, id: 'user2', name: 'Maria G.', points: 2310, photoUrl: '/avatars/02.png' },
  { rank: 3, id: 'user3', name: 'Sam K.', points: 2100, photoUrl: '/avatars/03.png' },
  { rank: 4, id: 'user4', name: 'Jamie L.', points: 1890, photoUrl: '/avatars/04.png' },
  { rank: 5, id: 'user5', name: 'Pat D.', points: 1720, photoUrl: '/avatars/05.png' },
  { rank: 12, id: 'current', name: 'You', points: 1280, photoUrl: '/avatars/user.png' }
];

export async function GET(request: Request) {
  // Get search params
  const { searchParams } = new URL(request.url);
  const timeframe = searchParams.get('timeframe') || 'week';
  
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // Add a random variation to points based on timeframe
  let result = mockLeaderboardData;
  
  if (timeframe === 'month') {
    result = mockLeaderboardData.map(user => ({
      ...user,
      points: Math.round(user.points * 2.5)
    }));
  } else if (timeframe === 'all') {
    result = mockLeaderboardData.map(user => ({
      ...user,
      points: Math.round(user.points * 5.2)
    }));
  }
  
  return NextResponse.json(result);
}