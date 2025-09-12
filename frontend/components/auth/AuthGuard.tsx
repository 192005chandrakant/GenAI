import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Spinner } from '../ui/spinner';
import { onAuthStateChange } from '@/lib/auth';

interface AuthGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  requireAuth?: boolean;
}

export function AuthGuard({
  children,
  fallback,
  requireAuth = true,
}: AuthGuardProps) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const unsubscribe = onAuthStateChange((currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (loading) return;

    if (requireAuth && !user) {
      router.push('/auth/login');
    } else if (!requireAuth && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router, requireAuth]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  if (requireAuth && !user) {
    return fallback || null;
  }

  if (!requireAuth && user) {
    return fallback || null;
  }

  return <>{children}</>;
}

export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options = { requireAuth: true }
) {
  return function WithAuthComponent(props: P) {
    return (
      <AuthGuard requireAuth={options.requireAuth}>
        <Component {...props} />
      </AuthGuard>
    );
  };
}
