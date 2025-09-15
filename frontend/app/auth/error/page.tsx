'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { AlertCircle, Home, RefreshCw, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';

const errorMessages: Record<string, string> = {
  Configuration: 'There is a problem with the server configuration.',
  AccessDenied: 'Access denied. You do not have permission to sign in.',
  Verification: 'The verification token has expired or has already been used.',
  Default: 'An unexpected error occurred during authentication.',
  OAuthSignin: 'Error in constructing an authorization URL.',
  OAuthCallback: 'Error in handling the response from an OAuth provider.',
  OAuthCreateAccount: 'Could not create OAuth account in the database.',
  EmailCreateAccount: 'Could not create email account in the database.',
  Callback: 'Error in the OAuth callback handler route.',
  OAuthAccountNotLinked: 'The account is already associated with another user.',
  EmailSignin: 'Check your email address.',
  CredentialsSignin: 'Sign in failed. Check the details you provided are correct.',
  SessionRequired: 'Please sign in to access this page.',
};

function AuthErrorContent() {
  const searchParams = useSearchParams();
  const [error, setError] = useState<string>('');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const errorParam = searchParams?.get('error') || 'Default';
    setError(errorParam);
  }, [searchParams]);

  if (!mounted) {
    return null; // Avoid hydration mismatch
  }

  const errorMessage = errorMessages[error] || errorMessages.Default;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 via-white to-orange-50 dark:from-gray-900 dark:via-gray-800 dark:to-red-900 p-4">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-6 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Authentication Error
            </h1>
            
            <p className="text-gray-600 dark:text-gray-300 mb-8">
              {errorMessage}
            </p>

            <div className="space-y-4">
              <Button
                asChild
                className="w-full bg-red-600 hover:bg-red-700 text-white"
              >
                <Link href="/auth/login">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Try Again
                </Link>
              </Button>

              <Button
                asChild
                variant="outline"
                className="w-full"
              >
                <Link href="/">
                  <Home className="w-4 h-4 mr-2" />
                  Back to Home
                </Link>
              </Button>
            </div>

            <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-center text-gray-500 dark:text-gray-400 mb-4">
                <Shield className="w-5 h-5 mr-2" />
                <span className="text-sm">Need help?</span>
              </div>
              
              <p className="text-xs text-gray-500 dark:text-gray-400">
                If this error persists, please{' '}
                <Link 
                  href="/contact" 
                  className="text-blue-600 dark:text-blue-400 hover:underline"
                >
                  contact our support team
                </Link>
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default function AuthErrorPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
      </div>
    }>
      <AuthErrorContent />
    </Suspense>
  );
}