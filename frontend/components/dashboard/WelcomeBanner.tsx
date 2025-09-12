'use client';

import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

type WelcomeBannerProps = {
  name: string;
};

export default function WelcomeBanner({ name }: WelcomeBannerProps) {
  const router = useRouter();

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Welcome back, {name}!
        </h1>
        <p className="text-gray-600 dark:text-gray-300 mt-1">
          Here's your summary of your activity and progress.
        </p>
      </div>
      <Button onClick={() => router.push('/analyze')}>
        Analyze New Content
      </Button>
    </div>
  );
}
