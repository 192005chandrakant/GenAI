import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, ArrowRight, X } from 'lucide-react';
import { LearnCard } from '../../lib/api';

interface LearnCardComponentProps {
  cards: LearnCard[];
  onClose?: () => void;
}

const LearnCardComponent = ({ cards, onClose }: LearnCardComponentProps) => {
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const currentCard = cards[currentCardIndex];
  
  const goToNextCard = () => {
    if (currentCardIndex < cards.length - 1) {
      setCurrentCardIndex(currentCardIndex + 1);
    }
  };
  
  const goToPreviousCard = () => {
    if (currentCardIndex > 0) {
      setCurrentCardIndex(currentCardIndex - 1);
    }
  };

  // Different background colors based on severity
  const getBgColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 border-red-300';
      case 'medium':
        return 'bg-yellow-100 border-yellow-300';
      case 'low':
        return 'bg-blue-100 border-blue-300';
      default:
        return 'bg-gray-100 border-gray-300';
    }
  };
  
  // Different text colors based on severity
  const getTextColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'text-red-800';
      case 'medium':
        return 'text-yellow-800';
      case 'low':
        return 'text-blue-800';
      default:
        return 'text-gray-800';
    }
  };

  // Different category icons
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'emotional':
        return '😢';
      case 'logical':
        return '🧠';
      case 'credibility':
        return '🔍';
      case 'visual':
        return '👁️';
      default:
        return '❓';
    }
  };
  
  return (
    <div className="relative">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">Learn About Misinformation Techniques</h3>
        {onClose && (
          <button 
            onClick={onClose} 
            className="p-1 rounded-full hover:bg-gray-100"
            aria-label="Close learn cards"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>
      
      <div className="relative w-full h-64">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentCard.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className={`absolute inset-0 p-5 rounded-xl border ${getBgColor(currentCard.severity)}`}
          >
            <div className="flex justify-between items-start">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">{getCategoryIcon(currentCard.category)}</span>
                <h4 className={`text-xl font-medium ${getTextColor(currentCard.severity)}`}>
                  {currentCard.technique}
                </h4>
              </div>
              <div className={`px-2 py-1 text-xs font-medium rounded-full ${getBgColor(currentCard.severity)} ${getTextColor(currentCard.severity)}`}>
                {currentCard.severity === 'high' ? 'High Severity' : 
                 currentCard.severity === 'medium' ? 'Medium Severity' : 'Low Severity'}
              </div>
            </div>
            
            <p className="mt-3 mb-4">{currentCard.explanation}</p>
            
            <div className="bg-white/70 backdrop-blur-sm p-3 rounded-lg">
              <p className="text-sm italic">Example: "{currentCard.example}"</p>
            </div>

            <div className="absolute bottom-4 right-5 flex items-center text-sm text-gray-600">
              <span>Card {currentCardIndex + 1} of {cards.length}</span>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
      
      <div className="flex justify-between mt-4">
        <button
          onClick={goToPreviousCard}
          disabled={currentCardIndex === 0}
          className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg ${
            currentCardIndex === 0 
              ? 'text-gray-400 cursor-not-allowed' 
              : 'text-blue-600 hover:bg-blue-50'
          }`}
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Previous</span>
        </button>
        
        <button
          onClick={goToNextCard}
          disabled={currentCardIndex === cards.length - 1}
          className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg ${
            currentCardIndex === cards.length - 1
              ? 'text-gray-400 cursor-not-allowed' 
              : 'text-blue-600 hover:bg-blue-50'
          }`}
        >
          <span>Next</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default LearnCardComponent;
