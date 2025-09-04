import React, { ReactNode, useEffect, useState } from 'react';
import ImprovedNavbar from './ImprovedNavbar';
import Footer from './Footer';
import { cn } from '../../lib/utils';
import { useSession } from 'next-auth/react';
import { Spinner } from '../ui/spinner';
import { motion, AnimatePresence } from 'framer-motion';

interface EnhancedLayoutProps {
  children: ReactNode;
  className?: string;
  hideFooter?: boolean;
  fullWidth?: boolean;
  showBackToTop?: boolean;
  pageTitle?: string;
  loading?: boolean;
  requireAuth?: boolean;
}

const EnhancedLayout = ({
  children,
  className,
  hideFooter = false,
  fullWidth = false,
  showBackToTop = false,
  pageTitle,
  loading = false,
  requireAuth = false,
}: EnhancedLayoutProps) => {
  const { status } = useSession();
  const [showBackButton, setShowBackButton] = useState(false);
  const [pageTransition, setPageTransition] = useState(false);
  
  // Handle scroll for back to top button
  useEffect(() => {
    if (!showBackToTop) return;
    
    const handleScroll = () => {
      if (window.scrollY > 400) {
        setShowBackButton(true);
      } else {
        setShowBackButton(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [showBackToTop]);
  
  // Page transition effect
  useEffect(() => {
    setPageTransition(true);
    const timer = setTimeout(() => setPageTransition(false), 800);
    return () => clearTimeout(timer);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };
  
  // Check if we should show loading state
  const isLoading = loading || (requireAuth && status === 'loading');

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 dark:bg-gray-900">
      <ImprovedNavbar />
      
      {pageTitle && (
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
          <div className={cn(
            "py-4",
            fullWidth ? "" : "container mx-auto px-4"
          )}>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {pageTitle}
            </h1>
          </div>
        </div>
      )}
      
      <AnimatePresence mode="wait">
        <motion.main 
          key={pageTitle || 'page'}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
          className={cn(
            'flex-grow',
            fullWidth ? '' : 'container mx-auto px-4 py-6 md:py-8',
            className
          )}
        >
          {isLoading ? (
            <div className="flex flex-col items-center justify-center h-[50vh]">
              <Spinner size="lg" />
              <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
            </div>
          ) : (
            children
          )}
        </motion.main>
      </AnimatePresence>
      
      {!hideFooter && <Footer />}
      
      {/* Back to top button */}
      <AnimatePresence>
        {showBackButton && showBackToTop && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.2 }}
            onClick={scrollToTop}
            className="fixed bottom-8 right-8 p-3 bg-blue-600 dark:bg-blue-500 text-white rounded-full shadow-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 z-40"
            aria-label="Back to top"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Page transition overlay */}
      <AnimatePresence>
        {pageTransition && (
          <motion.div
            initial={{ opacity: 1 }}
            animate={{ opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="fixed inset-0 bg-white dark:bg-gray-900 z-50 pointer-events-none"
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default EnhancedLayout;
