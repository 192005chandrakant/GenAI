'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Award, Check, Shield, Book, MessageSquare, Zap, Upload, Star, Clock, Lock } from 'lucide-react';
import MainLayout from '../../../components/layout/MainLayout';

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  progress: number; // 0 to 100
  total: number;
  current: number;
  unlocked: boolean;
  category: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  points: number;
}

export default function AchievementsPage() {
  const [activeTab, setActiveTab] = useState<'all' | 'unlocked' | 'locked'>('all');
  
  const achievements: Achievement[] = [
    {
      id: 'ach_1',
      title: 'Fact Finder',
      description: 'Complete 10 fact checks to earn this badge',
      icon: <Check className="w-6 h-6" />,
      progress: 50,
      total: 10,
      current: 5,
      unlocked: false,
      category: 'beginner',
      points: 25
    },
    {
      id: 'ach_2',
      title: 'Consistent Checker',
      description: 'Check facts for 5 consecutive days',
      icon: <Clock className="w-6 h-6" />,
      progress: 60,
      total: 5,
      current: 3,
      unlocked: false,
      category: 'beginner',
      points: 50
    },
    {
      id: 'ach_3',
      title: 'Accuracy Advocate',
      description: 'Identify 10 pieces of misleading content',
      icon: <Shield className="w-6 h-6" />,
      progress: 70,
      total: 10,
      current: 7,
      unlocked: false,
      category: 'intermediate',
      points: 75
    },
    {
      id: 'ach_4',
      title: 'Knowledge Seeker',
      description: 'Complete 5 learning modules',
      icon: <Book className="w-6 h-6" />,
      progress: 40,
      total: 5,
      current: 2,
      unlocked: false,
      category: 'beginner',
      points: 50
    },
    {
      id: 'ach_5',
      title: 'Community Guardian',
      description: 'Submit 10 accurate reports to the community',
      icon: <MessageSquare className="w-6 h-6" />,
      progress: 20,
      total: 10,
      current: 2,
      unlocked: false,
      category: 'intermediate',
      points: 100
    },
    {
      id: 'ach_6',
      title: 'Rapid Responder',
      description: 'Verify 5 trending topics within 24 hours of them going viral',
      icon: <Zap className="w-6 h-6" />,
      progress: 0,
      total: 5,
      current: 0,
      unlocked: false,
      category: 'advanced',
      points: 125
    },
    {
      id: 'ach_7',
      title: 'Media Maven',
      description: 'Check 10 different types of media (text, image, audio, video)',
      icon: <Upload className="w-6 h-6" />,
      progress: 30,
      total: 10,
      current: 3,
      unlocked: false,
      category: 'intermediate',
      points: 100
    },
    {
      id: 'ach_8',
      title: 'Truth Champion',
      description: 'Reach a 90% or higher accuracy rate on 20 checks',
      icon: <Award className="w-6 h-6" />,
      progress: 0,
      total: 20,
      current: 0,
      unlocked: false,
      category: 'expert',
      points: 250
    },
    {
      id: 'ach_9',
      title: 'First Check',
      description: 'Complete your first fact check',
      icon: <Star className="w-6 h-6" />,
      progress: 100,
      total: 1,
      current: 1,
      unlocked: true,
      category: 'beginner',
      points: 10
    },
    {
      id: 'ach_10',
      title: 'Learning Pioneer',
      description: 'Complete your first learning module',
      icon: <Book className="w-6 h-6" />,
      progress: 100,
      total: 1,
      current: 1,
      unlocked: true,
      category: 'beginner',
      points: 10
    },
  ];
  
  // Filter achievements based on active tab
  const filteredAchievements = achievements.filter((achievement) => {
    if (activeTab === 'all') return true;
    if (activeTab === 'unlocked') return achievement.unlocked;
    if (activeTab === 'locked') return !achievement.unlocked;
    return true;
  });
  
  // Get total points earned
  const totalPoints = achievements
    .filter(achievement => achievement.unlocked)
    .reduce((total, achievement) => total + achievement.points, 0);
  
  // Get points progress toward next level
  const pointsToNextLevel = 1000;
  const currentLevelPoints = 745; // Mock data
  const nextLevelProgress = (currentLevelPoints / pointsToNextLevel) * 100;

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-1">Achievements</h1>
            <p className="text-gray-600">
              Track your progress and unlock rewards
            </p>
          </div>
          
          <div className="mt-4 md:mt-0 bg-white rounded-lg shadow-sm border border-gray-100 p-4 text-center">
            <div className="flex items-center justify-center space-x-2">
              <Award className="w-5 h-5 text-yellow-500" />
              <span className="text-xl font-bold">{totalPoints} Points</span>
            </div>
            <p className="text-sm text-gray-600 mt-1">Level 6</p>
            <div className="w-full bg-gray-100 rounded-full h-2 mt-2">
              <div 
                className="h-2 rounded-full bg-blue-500"
                style={{ width: `${nextLevelProgress}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">{currentLevelPoints}/{pointsToNextLevel} to Level 7</p>
          </div>
        </div>
        
        {/* Tab Navigation */}
        <div className="bg-gray-100 rounded-lg p-1 flex space-x-1 mb-6 max-w-md">
          <button
            onClick={() => setActiveTab('all')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition ${
              activeTab === 'all' 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setActiveTab('unlocked')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition ${
              activeTab === 'unlocked' 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Unlocked
          </button>
          <button
            onClick={() => setActiveTab('locked')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition ${
              activeTab === 'locked' 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Locked
          </button>
        </div>
        
        {/* Achievements Grid */}
        {filteredAchievements.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAchievements.map((achievement, index) => (
              <motion.div
                key={achievement.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className={`bg-white rounded-xl shadow-sm border p-6 ${
                  achievement.unlocked 
                    ? 'border-green-200' 
                    : 'border-gray-200'
                }`}
              >
                <div className="flex justify-between items-start mb-4">
                  <div className={`p-3 rounded-lg ${
                    achievement.unlocked 
                      ? 'bg-green-100 text-green-600' 
                      : 'bg-gray-100 text-gray-500'
                  }`}>
                    {achievement.icon}
                  </div>
                  
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-700 flex items-center">
                      <Award className="w-4 h-4 mr-1 text-yellow-500" />
                      {achievement.points}
                    </span>
                    {achievement.unlocked && (
                      <div className="ml-2 bg-green-100 p-1 rounded-full">
                        <Check className="w-4 h-4 text-green-600" />
                      </div>
                    )}
                  </div>
                </div>
                
                <h3 className="font-semibold text-lg text-gray-900 mb-1">{achievement.title}</h3>
                <p className="text-gray-600 text-sm mb-3">{achievement.description}</p>
                
                <div className="mt-4">
                  <div className="flex justify-between text-xs text-gray-600 mb-1">
                    <span>Progress</span>
                    <span>{achievement.current}/{achievement.total}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        achievement.unlocked ? 'bg-green-500' : 'bg-blue-500'
                      }`}
                      style={{ width: `${achievement.progress}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="mt-4">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    achievement.category === 'beginner' 
                      ? 'bg-blue-100 text-blue-700' 
                      : achievement.category === 'intermediate'
                      ? 'bg-purple-100 text-purple-700'
                      : achievement.category === 'advanced'
                      ? 'bg-orange-100 text-orange-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {achievement.category.charAt(0).toUpperCase() + achievement.category.slice(1)}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
              <Award className="w-8 h-8 text-gray-400" />
            </div>
            <h2 className="text-xl font-medium text-gray-900 mb-2">No achievements found</h2>
            <p className="text-gray-600">Check back later or change your filter settings</p>
          </div>
        )}
        
        {/* Upcoming Achievements (if on Locked tab) */}
        {activeTab === 'locked' && (
          <div className="mt-12">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Special Achievements</h2>
            
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4">
                <Lock className="w-6 h-6 text-gray-300" />
              </div>
              
              <h3 className="text-lg font-medium text-gray-900 mb-2">Master Fact Checker</h3>
              <p className="text-gray-600 mb-4">Complete 100 fact checks with 85% or higher accuracy</p>
              
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <Award className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">500 Points</p>
                  <p className="text-sm text-gray-500">Expert Level</p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Achievement Levels Guide */}
        <div className="mt-12 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Achievement Levels</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-4 border border-blue-100 rounded-lg bg-blue-50">
              <div className="flex items-center mb-3">
                <div className="p-2 bg-blue-100 rounded-md mr-3">
                  <Star className="w-5 h-5 text-blue-600" />
                </div>
                <h3 className="font-medium text-blue-900">Beginner</h3>
              </div>
              <p className="text-sm text-blue-700">First steps in your fact-checking journey. Easy achievements to get started.</p>
            </div>
            
            <div className="p-4 border border-purple-100 rounded-lg bg-purple-50">
              <div className="flex items-center mb-3">
                <div className="p-2 bg-purple-100 rounded-md mr-3">
                  <Shield className="w-5 h-5 text-purple-600" />
                </div>
                <h3 className="font-medium text-purple-900">Intermediate</h3>
              </div>
              <p className="text-sm text-purple-700">Achievements that require consistent effort and developing fact-checking skills.</p>
            </div>
            
            <div className="p-4 border border-orange-100 rounded-lg bg-orange-50">
              <div className="flex items-center mb-3">
                <div className="p-2 bg-orange-100 rounded-md mr-3">
                  <Zap className="w-5 h-5 text-orange-600" />
                </div>
                <h3 className="font-medium text-orange-900">Advanced</h3>
              </div>
              <p className="text-sm text-orange-700">Challenges for experienced users who actively contribute to fighting misinformation.</p>
            </div>
            
            <div className="p-4 border border-red-100 rounded-lg bg-red-50">
              <div className="flex items-center mb-3">
                <div className="p-2 bg-red-100 rounded-md mr-3">
                  <Award className="w-5 h-5 text-red-600" />
                </div>
                <h3 className="font-medium text-red-900">Expert</h3>
              </div>
              <p className="text-sm text-red-700">The highest tier of achievements, requiring dedication and expertise in fact-checking.</p>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
