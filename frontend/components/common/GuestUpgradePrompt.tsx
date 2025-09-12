import React, { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  CheckCircle, 
  Zap, 
  Shield, 
  Users, 
  BarChart3, 
  Star,
  Clock,
  ArrowRight
} from 'lucide-react';

interface GuestUpgradePromptProps {
  remainingChecks: number;
  onDismiss: () => void;
  className?: string;
}

export default function GuestUpgradePrompt({ 
  remainingChecks, 
  onDismiss, 
  className = '' 
}: GuestUpgradePromptProps) {
  const [isVisible, setIsVisible] = useState(true);

  const handleDismiss = () => {
    setIsVisible(false);
    setTimeout(onDismiss, 300); // Wait for animation to complete
  };

  const benefits = [
    {
      icon: Zap,
      title: 'Unlimited Fact Checks',
      description: 'No daily limits - verify as much content as you need'
    },
    {
      icon: Shield,
      title: 'Detailed Analysis',
      description: 'Get comprehensive reports with sources and evidence'
    },
    {
      icon: BarChart3,
      title: 'Personal Dashboard',
      description: 'Track your fact-checking history and insights'
    },
    {
      icon: Users,
      title: 'Community Access',
      description: 'Join discussions and share findings with others'
    }
  ];

  const getUrgencyMessage = () => {
    if (remainingChecks <= 1) {
      return {
        text: "This is your last free check!",
        color: "text-red-600",
        bgColor: "bg-red-50 border-red-200"
      };
    } else if (remainingChecks <= 3) {
      return {
        text: `Only ${remainingChecks} checks remaining today`,
        color: "text-orange-600",
        bgColor: "bg-orange-50 border-orange-200"
      };
    } else {
      return {
        text: `${remainingChecks} free checks remaining today`,
        color: "text-blue-600",
        bgColor: "bg-blue-50 border-blue-200"
      };
    }
  };

  const urgency = getUrgencyMessage();

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.95 }}
          transition={{ duration: 0.3 }}
          className={`relative bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden ${className}`}
        >
          {/* Close button */}
          <button
            onClick={handleDismiss}
            className="absolute top-4 right-4 z-10 p-1 rounded-full hover:bg-gray-100 transition-colors"
            aria-label="Dismiss"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>

          {/* Header */}
          <div className={`px-6 py-4 border-b ${urgency.bgColor}`}>
            <div className="flex items-center space-x-3">
              <div className="bg-white rounded-full p-2">
                <Clock className={`w-5 h-5 ${urgency.color}`} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">
                  Unlock Unlimited Fact-Checking
                </h3>
                <p className={`text-sm ${urgency.color}`}>
                  {urgency.text}
                </p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {/* Benefits grid */}
            <div className="grid md:grid-cols-2 gap-4 mb-6">
              {benefits.map((benefit, index) => (
                <motion.div
                  key={benefit.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50"
                >
                  <div className="bg-blue-100 rounded-lg p-2">
                    <benefit.icon className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 text-sm">
                      {benefit.title}
                    </h4>
                    <p className="text-xs text-gray-600 mt-1">
                      {benefit.description}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Social proof */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 mb-6">
              <div className="flex items-center space-x-2 mb-2">
                <div className="flex">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-yellow-500 fill-current" />
                  ))}
                </div>
                <span className="text-sm font-medium text-gray-700">
                  Join 50,000+ users
                </span>
              </div>
              <p className="text-sm text-gray-600">
                "This platform has become essential for my daily news consumption. 
                The detailed analysis helps me stay informed with confidence."
              </p>
              <p className="text-xs text-gray-500 mt-1">
                - Sarah M., Verified User
              </p>
            </div>

            {/* Call to action */}
            <div className="flex flex-col sm:flex-row gap-3">
              <Link
                href="/auth/register"
                className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-semibold text-center hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
              >
                <div className="flex items-center justify-center space-x-2">
                  <span>Sign Up Free</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </Link>
              <Link
                href="/auth/login"
                className="flex-1 border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-medium text-center hover:bg-gray-50 transition-colors"
              >
                Already have an account?
              </Link>
            </div>

            {/* Trust indicators */}
            <div className="mt-4 flex items-center justify-center space-x-6 text-xs text-gray-500">
              <div className="flex items-center space-x-1">
                <CheckCircle className="w-3 h-3 text-green-500" />
                <span>Free Forever</span>
              </div>
              <div className="flex items-center space-x-1">
                <CheckCircle className="w-3 h-3 text-green-500" />
                <span>No Credit Card</span>
              </div>
              <div className="flex items-center space-x-1">
                <CheckCircle className="w-3 h-3 text-green-500" />
                <span>Instant Access</span>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
