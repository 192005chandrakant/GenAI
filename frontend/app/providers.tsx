'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { useRouter } from 'next/navigation'
import { Spinner } from '../components/ui/spinner'
import { AuthProvider } from '../components/auth/AuthProvider'

interface ProvidersProps {
  children: React.ReactNode
}

// Error fallback component
function ErrorFallback({ error, resetErrorBoundary }: { error: Error, resetErrorBoundary: () => void }) {
  const router = useRouter()

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="max-w-md w-full mx-auto px-6 py-12 bg-white dark:bg-gray-800 shadow-xl rounded-lg">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 dark:bg-red-900/30 mb-6">
            <svg className="h-10 w-10 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">Something went wrong</h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            We're sorry, but an unexpected error has occurred. Our team has been notified.
          </p>
          <div className="space-y-3">
            <button
              onClick={() => {
                resetErrorBoundary();
                router.refresh();
              }}
              className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Try again
            </button>
            <button
              onClick={() => {
                resetErrorBoundary();
                router.push('/');
              }}
              className="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md shadow-sm text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Return to home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Theme provider
function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark' | 'loading'>('loading');
  const [mounted, setMounted] = useState(false);

  // 1. Effect for initial theme setup on mount
  useEffect(() => {
    setMounted(true);
    try {
      const storedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
      const systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      const initialTheme = storedTheme || systemPreference;
      setTheme(initialTheme);
    } catch (error) {
      console.warn('Could not access theme from localStorage or system preference.', error);
      setTheme('light'); // Fallback to light theme
    }
  }, []);

  // 2. Effect to apply theme changes to the DOM and update window object
  useEffect(() => {
    if (theme === 'loading') return;

    // Apply class to <html> element
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }

    try {
      // Persist theme to localStorage
      localStorage.setItem('theme', theme);
    } catch (error) {
      console.warn('Could not save theme to localStorage.', error);
    }

    // Update the global theme object for the toggle function
    window.__theme = {
      current: theme,
      toggle: () => {
        // This function will be redefined on each theme change,
        // ensuring it always has the correct current theme.
        setTheme(prevTheme => (prevTheme === 'dark' ? 'light' : 'dark'));
      },
    };
  }, [theme]);

  // Avoid rendering children until theme is determined to prevent flash of unstyled content
  if (!mounted || theme === 'loading') {
    // You can return a loader here, but returning children is fine to avoid layout shifts
    // if you handle the flash of content with CSS.
    return <>{children}</>;
  }

  return <>{children}</>;
}

// Declare the theme type on window object
declare global {
  interface Window {
    __theme?: {
      current: 'light' | 'dark';
      toggle: () => void;
    };
  }
}

export function Providers({ children }: ProvidersProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  )

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <AuthProvider>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider>{children}</ThemeProvider>
        </QueryClientProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
