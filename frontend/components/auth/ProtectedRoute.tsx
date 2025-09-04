import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { Spinner } from '../ui/spinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  adminOnly?: boolean;
  redirectTo?: string;
}

export const ProtectedRoute = ({
  children,
  adminOnly = false,
  redirectTo = '/auth/login',
}: ProtectedRouteProps) => {
  const { data: session, status } = useSession();
  const router = useRouter();
  const isLoading = status === 'loading';

  useEffect(() => {
    if (!isLoading) {
      // If not authenticated, redirect to login
      if (!session) {
        router.push(`${redirectTo}?callbackUrl=${window.location.href}`);
      }
      // If admin-only route and user is not an admin, redirect to dashboard
      else if (adminOnly && !session.user.isAdmin) {
        router.push('/dashboard');
      }
    }
  }, [isLoading, session, adminOnly, redirectTo, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[50vh]">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">Verifying your access...</p>
        </div>
      </div>
    );
  }

  // If not authorized or admin check fails, don't render children
  if (!session || (adminOnly && !session.user.isAdmin)) {
    return null;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
