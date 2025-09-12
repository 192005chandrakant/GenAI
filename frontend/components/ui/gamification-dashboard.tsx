'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Trophy, 
  Star, 
  Award, 
  TrendingUp, 
  Zap, 
  Target, 
  Calendar,
  Gift,
  Users,
  Crown,
  Medal,
  Flame
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import apiClient from '@/lib/api';
import { toast } from 'react-hot-toast';

interface UserStats {
  user_id: string;
  total_points: number;
  level: number;
  level_progress: number;
  next_level_points: number;
  checks_completed: number;
  accuracy_rate: number;
  current_streak: number;
  longest_streak: number;
  badges_earned: number;
  achievements_unlocked: number;
  content_shared: number;
  reports_submitted: number;
  learning_modules_completed: number;
  rank_global: number;
  rank_weekly: number;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  category: string;
  icon_url: string;
  points_reward: number;
  badge_id: string;
  requirements: Record<string, any>;
  progress: Record<string, any>;
  earned: boolean;
  earned_at?: string;
}

interface Challenge {
  id: string;
  title: string;
  description: string;
  type: string;
  icon_url: string;
  points_reward: number;
  badge_reward?: string;
  requirements: Record<string, any>;
  progress: Record<string, any>;
  starts_at: string;
  ends_at: string;
  completed: boolean;
  participants_count: number;
}

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  display_name: string;
  score: number;
  avatar_url?: string;
  badges: string[];
}

export default function GamificationDashboard() {
  const [stats, setStats] = useState<UserStats | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'achievements' | 'challenges' | 'leaderboard'>('overview');

  useEffect(() => {
    loadGamificationData();
  }, []);

  const loadGamificationData = async () => {
    try {
      setLoading(true);
      const [statsRes, achievementsRes, challengesRes, leaderboardRes] = await Promise.all([
        apiClient.get('/api/v1/gamification/stats'),
        apiClient.get('/api/v1/gamification/achievements'),
        apiClient.get('/api/v1/gamification/challenges'),
        apiClient.get('/api/v1/gamification/leaderboard?limit=10')
      ]);

      setStats(statsRes.data);
      setAchievements(achievementsRes.data);
      setChallenges(challengesRes.data);
      setLeaderboard(leaderboardRes.data.entries || []);
    } catch (error) {
      console.error('Failed to load gamification data:', error);
      toast.error('Failed to load gamification data');
    } finally {
      setLoading(false);
    }
  };

  const claimDailyReward = async () => {
    try {
      const response = await apiClient.post('/api/v1/gamification/daily-reward/claim');
      toast.success(response.data.message);
      loadGamificationData(); // Refresh data
    } catch (error) {
      console.error('Failed to claim daily reward:', error);
      toast.error('Failed to claim daily reward');
    }
  };

  const joinChallenge = async (challengeId: string) => {
    try {
      await apiClient.post(`/api/v1/gamification/challenges/${challengeId}/join`);
      toast.success('Successfully joined challenge!');
      loadGamificationData(); // Refresh data
    } catch (error) {
      console.error('Failed to join challenge:', error);
      toast.error('Failed to join challenge');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-lg shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100">Total Points</p>
              <p className="text-2xl font-bold">{stats?.total_points || 0}</p>
            </div>
            <Star className="w-8 h-8 text-blue-200" />
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-gradient-to-r from-green-500 to-emerald-600 text-white p-6 rounded-lg shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100">Level {stats?.level || 1}</p>
              <p className="text-sm text-green-200">
                {Math.round((stats?.level_progress || 0) * 100)}% to next
              </p>
            </div>
            <Crown className="w-8 h-8 text-green-200" />
          </div>
          <Progress 
            value={(stats?.level_progress || 0) * 100} 
            className="mt-2 bg-green-400" 
          />
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-gradient-to-r from-orange-500 to-red-600 text-white p-6 rounded-lg shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100">Current Streak</p>
              <p className="text-2xl font-bold">{stats?.current_streak || 0} days</p>
            </div>
            <Flame className="w-8 h-8 text-orange-200" />
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-gradient-to-r from-purple-500 to-pink-600 text-white p-6 rounded-lg shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100">Global Rank</p>
              <p className="text-2xl font-bold">#{stats?.rank_global || 'N/A'}</p>
            </div>
            <Trophy className="w-8 h-8 text-purple-200" />
          </div>
        </motion.div>
      </div>

      {/* Daily Reward */}
      <div className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white p-6 rounded-lg shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Gift className="w-8 h-8" />
            <div>
              <h3 className="text-lg font-bold">Daily Reward</h3>
              <p className="text-yellow-100">Claim your daily points and maintain your streak!</p>
            </div>
          </div>
          <Button 
            onClick={claimDailyReward}
            className="bg-white text-orange-600 hover:bg-yellow-50"
          >
            Claim 25 Points
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.checks_completed || 0}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Checks Completed</p>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{Math.round(stats?.accuracy_rate || 0)}%</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Accuracy Rate</p>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.badges_earned || 0}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Badges Earned</p>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.achievements_unlocked || 0}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Achievements</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAchievements = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {achievements.map((achievement) => (
        <motion.div
          key={achievement.id}
          whileHover={{ scale: 1.02 }}
          className={`p-6 rounded-lg border-2 transition-all duration-200 ${
            achievement.earned
              ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200 dark:from-green-900/20 dark:to-emerald-900/20 dark:border-green-700'
              : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'
          }`}
        >
          <div className="flex items-start space-x-4">
            <div className={`p-3 rounded-full ${
              achievement.earned ? 'bg-green-100 dark:bg-green-900/30' : 'bg-gray-100 dark:bg-gray-700'
            }`}>
              <Award className={`w-6 h-6 ${
                achievement.earned ? 'text-green-600 dark:text-green-400' : 'text-gray-400'
              }`} />
            </div>
            <div className="flex-1">
              <h3 className={`font-bold ${
                achievement.earned ? 'text-green-800 dark:text-green-200' : 'text-gray-900 dark:text-white'
              }`}>
                {achievement.title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                {achievement.description}
              </p>
              <div className="flex items-center justify-between">
                <span className={`text-xs px-2 py-1 rounded-full ${
                  achievement.earned 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                }`}>
                  {achievement.earned ? 'Completed' : 'In Progress'}
                </span>
                <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                  +{achievement.points_reward} pts
                </span>
              </div>
              {!achievement.earned && achievement.progress && (
                <div className="mt-2">
                  <Progress 
                    value={Math.min(100, (Object.values(achievement.progress)[0] as number / Object.values(achievement.requirements)[0] as number) * 100)}
                    className="h-2"
                  />
                </div>
              )}
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );

  const renderChallenges = () => (
    <div className="space-y-4">
      {challenges.map((challenge) => (
        <motion.div
          key={challenge.id}
          whileHover={{ scale: 1.01 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm"
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-4 flex-1">
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                <Target className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-gray-900 dark:text-white">{challenge.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">{challenge.description}</p>
                <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                  <div className="flex items-center space-x-1">
                    <Users className="w-4 h-4" />
                    <span>{challenge.participants_count} participants</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Star className="w-4 h-4" />
                    <span>{challenge.points_reward} points</span>
                  </div>
                </div>
                <div className="mt-2">
                  <Progress value={75} className="h-2" />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Progress: {Object.values(challenge.progress)[0]} / {Object.values(challenge.requirements)[0]}
                  </p>
                </div>
              </div>
            </div>
            <Button
              onClick={() => joinChallenge(challenge.id)}
              disabled={challenge.completed}
              className="ml-4"
            >
              {challenge.completed ? 'Completed' : 'Join'}
            </Button>
          </div>
        </motion.div>
      ))}
    </div>
  );

  const renderLeaderboard = () => (
    <div className="space-y-4">
      {leaderboard.map((entry, index) => (
        <motion.div
          key={entry.user_id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm"
        >
          <div className="flex items-center space-x-4">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
              entry.rank === 1 ? 'bg-yellow-500' :
              entry.rank === 2 ? 'bg-gray-400' :
              entry.rank === 3 ? 'bg-amber-600' : 'bg-blue-500'
            }`}>
              {entry.rank <= 3 ? (
                entry.rank === 1 ? <Crown className="w-5 h-5" /> :
                <Medal className="w-5 h-5" />
              ) : (
                entry.rank
              )}
            </div>
            <div className="flex-1">
              <h3 className="font-medium text-gray-900 dark:text-white">{entry.display_name}</h3>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500 dark:text-gray-400">{entry.score} points</span>
                {entry.badges.length > 0 && (
                  <div className="flex items-center space-x-1">
                    {entry.badges.slice(0, 3).map((badge, i) => (
                      <div key={i} className="w-4 h-4 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                        <Award className="w-2 h-2 text-blue-600 dark:text-blue-400" />
                      </div>
                    ))}
                    {entry.badges.length > 3 && (
                      <span className="text-xs text-gray-400 dark:text-gray-500">+{entry.badges.length - 3}</span>
                    )}
                  </div>
                )}
              </div>
            </div>
            <TrendingUp className="w-5 h-5 text-green-500" />
          </div>
        </motion.div>
      ))}
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Gamification Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Track your progress, earn rewards, and compete with other users
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
        {[
          { id: 'overview', label: 'Overview', icon: TrendingUp },
          { id: 'achievements', label: 'Achievements', icon: Award },
          { id: 'challenges', label: 'Challenges', icon: Target },
          { id: 'leaderboard', label: 'Leaderboard', icon: Trophy }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
              activeTab === tab.id
                ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'achievements' && renderAchievements()}
          {activeTab === 'challenges' && renderChallenges()}
          {activeTab === 'leaderboard' && renderLeaderboard()}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
