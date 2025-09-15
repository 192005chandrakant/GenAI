import { NextResponse } from 'next/server';

// Mock dashboard data
const mockDashboardData = {
  stats: {
    total_checks: 42,
    points: 1280,
    leaderboard_rank: 12,
    courses_completed: 5,
    stats_change: {
      checks_change: '+12%',
      points_change: '+80',
      rank_change: '-2',
      courses_change: '+1'
    }
  },
  recent_activity: [
    {
      id: '1',
      verdict: 'Misleading Content',
      summary: 'The article about "miracle cures" for COVID-19 contains several unsubstantiated claims.',
      score: 35,
      date: '2 days ago',
    },
    {
      id: '2',
      verdict: 'Factually Accurate',
      summary: 'The report on climate change statistics aligns with data from major scientific bodies.',
      score: 92,
      date: '3 days ago',
    },
    {
      id: '3',
      verdict: 'Partially False',
      summary: 'A social media post about a political candidate mixes true and false statements.',
      score: 58,
      date: '5 days ago',
    },
    {
      id: '4',
      verdict: 'Satire/Parody',
      summary: 'An article from a known satirical website was correctly identified.',
      score: 85,
      date: '6 days ago',
    },
  ],
  achievements: [
    { 
      id: '1', 
      name: 'Fact Finder', 
      icon: 'award', 
      color: 'text-yellow-500', 
      description: 'Complete 10 checks', 
      achieved: true 
    },
    { 
      id: '2', 
      name: 'Truth Seeker', 
      icon: 'star', 
      color: 'text-blue-500', 
      description: 'Achieve a 90+ score', 
      achieved: true 
    },
    { 
      id: '3', 
      name: 'Debunker', 
      icon: 'shield', 
      color: 'text-green-500', 
      description: 'Identify 5 misleading articles', 
      achieved: true 
    },
    { 
      id: '4', 
      name: 'Master Analyst', 
      icon: 'target', 
      color: 'text-gray-400', 
      description: 'Complete 50 checks', 
      achieved: false, 
      progress: 60 
    },
  ],
  learning_progress: [
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
  ]
};

export async function GET() {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Return mock data
  return NextResponse.json(mockDashboardData);
}