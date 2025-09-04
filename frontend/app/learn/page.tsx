'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Search, Filter, Bookmark, CheckCircle, Loader2, AlertTriangle } from 'lucide-react';
import MainLayout from '../../components/layout/MainLayout';
import { toast } from 'react-hot-toast';
import { useRequireAuth, usePageView } from '@/hooks';
import apiClient from '@/lib/api';

interface LearningModule {
  id: string;
  title: string;
  description: string;
  duration: number; // in minutes
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  category: string;
  image: string;
  tags: string[];
  lessons: number;
  completed?: boolean;
}

interface Category {
  id: string;
  name: string;
  icon: JSX.Element;
}

// Mock data for learning modules
const mockLearningModules: LearningModule[] = [
  {
    id: 'mod_1',
    title: 'Spotting Clickbait Headlines',
    description: 'Learn how to identify manipulative headlines designed to get clicks rather than inform.',
    duration: 15,
    difficulty: 'beginner',
    category: 'content',
    image: '/images/clickbait.jpg',
    tags: ['headlines', 'clickbait', 'manipulation'],
    lessons: 5,
  },
  {
    id: 'mod_2',
    title: 'Understanding Statistical Manipulation',
    description: 'Discover how data and statistics can be misrepresented to support false narratives.',
    duration: 25,
    difficulty: 'intermediate',
    category: 'statistics',
    image: '/images/statistics.jpg',
    tags: ['statistics', 'data', 'charts', 'graphs'],
    lessons: 7,
  },
  {
    id: 'mod_3',
    title: 'Deepfake Detection Basics',
    description: 'Learn the fundamentals of identifying AI-generated fake videos and images.',
    duration: 30,
    difficulty: 'intermediate',
    category: 'media',
    image: '/images/deepfakes.jpg',
    tags: ['deepfakes', 'AI', 'image manipulation', 'video'],
    lessons: 8,
  },
  {
    id: 'mod_4',
    title: 'Fact-Checking Techniques',
    description: 'Master the tools and methods used by professional fact-checkers.',
    duration: 20,
    difficulty: 'beginner',
    category: 'factchecking',
    image: '/images/factchecking.jpg',
    tags: ['fact-checking', 'research', 'verification'],
    lessons: 6,
  },
  {
    id: 'mod_5',
    title: 'Evaluating Source Credibility',
    description: 'Learn how to assess the reliability and bias of information sources.',
    duration: 15,
    difficulty: 'beginner',
    category: 'credibility',
    image: '/images/sources.jpg',
    tags: ['sources', 'credibility', 'bias', 'evaluation'],
    lessons: 5,
  },
  {
    id: 'mod_6',
    title: 'Advanced Propaganda Analysis',
    description: 'Understand sophisticated propaganda techniques and how they influence opinions.',
    duration: 40,
    difficulty: 'advanced',
    category: 'techniques',
    image: '/images/propaganda.jpg',
    tags: ['propaganda', 'persuasion', 'manipulation'],
    lessons: 10,
  },
];

// Categories
const categories: Category[] = [
  { id: 'all', name: 'All Topics', icon: <BookOpen className="w-5 h-5" /> },
  { id: 'content', name: 'Content Analysis', icon: <BookOpen className="w-5 h-5" /> },
  { id: 'statistics', name: 'Statistics & Data', icon: <BookOpen className="w-5 h-5" /> },
  { id: 'media', name: 'Media Literacy', icon: <BookOpen className="w-5 h-5" /> },
  { id: 'factchecking', name: 'Fact-Checking', icon: <BookOpen className="w-5 h-5" /> },
  { id: 'credibility', name: 'Source Credibility', icon: <BookOpen className="w-5 h-5" /> },
  { id: 'techniques', name: 'Manipulation Techniques', icon: <BookOpen className="w-5 h-5" /> },
];

export default function LearnPage() {
  // Use authentication hook
  const { session, status } = useRequireAuth();
  
  // Set up page tracking
  usePageView('Learning Center');
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string[]>([]);
  const [modules, setModules] = useState<LearningModule[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [bookmarkedModules, setBookmarkedModules] = useState<string[]>([]);

  // Fetch learning modules
  useEffect(() => {
    const fetchModules = async () => {
      if (status !== 'authenticated') return;
      
      setIsLoading(true);
      setError(null);
      try {
        // Try to fetch from API
        try {
          const data = await apiClient.getLearningModules();
          setModules(data);
        } catch (apiError) {
          console.warn('Failed to fetch from API, using mock data:', apiError);
          // Fallback to mock data
          const randomlyCompleted = mockLearningModules.map(module => ({
            ...module,
            completed: Math.random() > 0.7, // Randomly mark some as completed
          }));
          setModules(randomlyCompleted);
        }
      } catch (error: any) {
        console.error('Failed to fetch learning modules:', error);
        setError(error.message || 'Failed to load learning content');
        toast.error('Failed to load learning content');
      } finally {
        setIsLoading(false);
      }
    };
    
    if (status === 'authenticated') {
      fetchModules();
      
      // Load bookmarks from localStorage
      const storedBookmarks = localStorage.getItem('bookmarkedModules');
      if (storedBookmarks) {
        try {
          const parsedBookmarks = JSON.parse(storedBookmarks);
          setBookmarkedModules(parsedBookmarks);
        } catch (e) {
          console.error('Failed to parse bookmarks:', e);
          localStorage.removeItem('bookmarkedModules');
        }
      }
    }
  }, [status]);

  // Filter modules based on search, category, and difficulty
  const filteredModules = modules.filter(module => {
    const matchesSearch = 
      searchQuery === '' || 
      module.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      module.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      module.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = 
      selectedCategory === 'all' || 
      module.category === selectedCategory;
    
    const matchesDifficulty = 
      selectedDifficulty.length === 0 || 
      selectedDifficulty.includes(module.difficulty);
    
    return matchesSearch && matchesCategory && matchesDifficulty;
  });

  // Toggle difficulty filter
  const toggleDifficulty = (difficulty: string) => {
    setSelectedDifficulty(prev => 
      prev.includes(difficulty)
        ? prev.filter(d => d !== difficulty)
        : [...prev, difficulty]
    );
  };

  // Toggle bookmark
  const toggleBookmark = (moduleId: string) => {
    setBookmarkedModules(prev => {
      const newBookmarks = prev.includes(moduleId)
        ? prev.filter(id => id !== moduleId)
        : [...prev, moduleId];
      
      // Save to localStorage
      localStorage.setItem('bookmarkedModules', JSON.stringify(newBookmarks));
      
      return newBookmarks;
    });
  };

  if (status === 'loading') {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center py-16">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
          <p className="text-lg font-medium text-gray-900">Loading authentication...</p>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <section className="text-center mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Learn to Fight Misinformation
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Explore our interactive learning modules to build your digital literacy skills 
              and become an expert in spotting and countering misinformation.
            </p>
          </motion.div>
        </section>
        
        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-red-400 mr-2" />
              <p className="text-red-800">{error}</p>
              <button 
                className="ml-auto text-red-500 hover:text-red-700"
                onClick={() => setError(null)}
              >
                <span className="sr-only">Dismiss</span>
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Search and Filter Section */}
        <section className="mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-4">
              {/* Search Input */}
              <div className="relative flex-grow">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  placeholder="Search for topics, skills, or keywords..."
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              {/* Difficulty Filter */}
              <div className="flex items-center space-x-2">
                <Filter className="h-5 w-5 text-gray-500" />
                <span className="text-sm text-gray-700 whitespace-nowrap">Difficulty:</span>
                <div className="flex space-x-2">
                  <button
                    onClick={() => toggleDifficulty('beginner')}
                    className={`px-3 py-1 text-sm rounded-full ${
                      selectedDifficulty.includes('beginner')
                        ? 'bg-green-100 text-green-800 border border-green-200'
                        : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
                    }`}
                  >
                    Beginner
                  </button>
                  <button
                    onClick={() => toggleDifficulty('intermediate')}
                    className={`px-3 py-1 text-sm rounded-full ${
                      selectedDifficulty.includes('intermediate')
                        ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                        : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
                    }`}
                  >
                    Intermediate
                  </button>
                  <button
                    onClick={() => toggleDifficulty('advanced')}
                    className={`px-3 py-1 text-sm rounded-full ${
                      selectedDifficulty.includes('advanced')
                        ? 'bg-red-100 text-red-800 border border-red-200'
                        : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
                    }`}
                  >
                    Advanced
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Categories Navigation */}
        <section className="mb-8">
          <div className="flex overflow-x-auto pb-2 hide-scrollbar space-x-2">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 whitespace-nowrap rounded-full flex items-center space-x-2 transition-colors ${
                  selectedCategory === category.id
                    ? 'bg-blue-100 text-blue-800 border border-blue-200'
                    : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-100'
                }`}
              >
                {category.icon}
                <span>{category.name}</span>
              </button>
            ))}
          </div>
        </section>

        {/* Modules Grid */}
        <section>
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-16">
              <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
              <p className="text-lg font-medium text-gray-900">Loading learning modules...</p>
            </div>
          ) : filteredModules.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredModules.map((module) => (
                <motion.div
                  key={module.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                  className="bg-white rounded-xl overflow-hidden border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
                >
                  <div className="relative h-48 bg-gray-200">
                    <div className="absolute inset-0 bg-gradient-to-t from-gray-900/70 to-transparent flex items-end">
                      <div className="p-4 text-white">
                        <div className="flex justify-between items-start">
                          <h3 className="text-xl font-semibold line-clamp-2">{module.title}</h3>
                          <button
                            onClick={() => toggleBookmark(module.id)}
                            className="p-1 rounded-full bg-white/20 backdrop-blur-sm hover:bg-white/30"
                            aria-label={bookmarkedModules.includes(module.id) ? "Remove bookmark" : "Add bookmark"}
                          >
                            <Bookmark 
                              className={`w-5 h-5 ${
                                bookmarkedModules.includes(module.id) ? 'text-yellow-300 fill-yellow-300' : 'text-white'
                              }`} 
                            />
                          </button>
                        </div>
                        <div className="flex space-x-2 mt-1">
                          <span className={`text-xs px-2 py-1 rounded-full
                            ${module.difficulty === 'beginner' ? 'bg-green-100 text-green-800' : 
                              module.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' : 
                              'bg-red-100 text-red-800'}`}
                          >
                            {module.difficulty.charAt(0).toUpperCase() + module.difficulty.slice(1)}
                          </span>
                          <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                            {module.duration} mins
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-4">
                    <p className="text-gray-600 mb-4 line-clamp-2">{module.description}</p>
                    <div className="flex justify-between items-center">
                      <div className="flex items-center text-sm text-gray-600">
                        <BookOpen className="w-4 h-4 mr-1" />
                        <span>{module.lessons} lessons</span>
                      </div>
                      {module.completed ? (
                        <div className="flex items-center text-green-600 text-sm font-medium">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          <span>Completed</span>
                        </div>
                      ) : (
                        <button 
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          onClick={async () => {
                            try {
                              toast.promise(
                                apiClient.completeLesson(module.id), 
                                {
                                  loading: 'Starting module...',
                                  success: (data) => {
                                    // Update the module as completed
                                    setModules(prev => prev.map(m => 
                                      m.id === module.id ? { ...m, completed: true } : m
                                    ));
                                    return `Module started! You earned ${data.points} points.`;
                                  },
                                  error: 'Failed to start module'
                                }
                              );
                            } catch (error) {
                              console.error('Error starting module:', error);
                            }
                          }}
                        >
                          Start Learning →
                        </button>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="bg-gray-100 rounded-full p-4 mb-4">
                <Search className="w-10 h-10 text-gray-500" />
              </div>
              <h3 className="text-xl font-medium text-gray-900 mb-2">No matching learning modules found</h3>
              <p className="text-gray-600 max-w-md">
                Try adjusting your search terms or filters to find what you're looking for.
              </p>
            </div>
          )}
        </section>
      </div>
    </MainLayout>
  );
}
