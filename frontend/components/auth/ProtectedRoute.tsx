import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Spinner } from '../ui/spinner';
import { auth, onAuthStateChange } from '@/lib/auth';

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
  const [user, setUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const unsubscribe = onAuthStateChange((currentUser) => {
      setLoading(true);
      
      if (!currentUser) {
        setUser(null);
        setIsAdmin(false);
        router.push(`${redirectTo}?callbackUrl=${window.location.href}`);
        setLoading(false);
      } else {
        setUser(currentUser);
        
        // Check if user is admin - you'll need to implement this based on your user data
        // This is an example implementation - adjust based on your actual data structure
        currentUser.getIdTokenResult().then((idTokenResult) => {
          setIsAdmin(idTokenResult.claims.admin === true);
          
          if (adminOnly && !idTokenResult.claims.admin) {
            router.push('/dashboard');
          }
          
          setLoading(false);
        });
      }
    });
    
    return () => unsubscribe();
  }, [adminOnly, redirectTo, router]);

  if (loading) {
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
  if (!user || (adminOnly && !isAdmin)) {
    return null;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
