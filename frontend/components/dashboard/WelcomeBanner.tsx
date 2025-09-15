'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';

type WelcomeBannerProps = {
  name: string;
};

export default function WelcomeBanner({ name }: WelcomeBannerProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyzeClick = () => {
    setIsLoading(true);
    router.push('/analyze');
  };

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 flex flex-col sm:flex-row items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Welcome back, {name}!
        </h1>
        <p className="text-gray-600 dark:text-gray-300 mt-1">
          Here's your summary of your activity and progress.
        </p>
      </div>
      <Button 
        onClick={handleAnalyzeClick}
        disabled={isLoading}
        className="mt-4 sm:mt-0"
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Loading...
          </>
        ) : (
          'Analyze New Content'
        )}
      </Button>
    </div>
  );
}
