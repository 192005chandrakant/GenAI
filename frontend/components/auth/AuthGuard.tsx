import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Spinner } from '../ui/spinner';

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
  const { data: session, status } = useSession();
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    if (status === 'loading') return;

    if (requireAuth && !session) {
      router.push('/auth/login');
    } else if (!requireAuth && session) {
      router.push('/dashboard');
    } else {
      setIsChecking(false);
    }
  }, [session, status, router, requireAuth]);

  if (status === 'loading' || isChecking) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  if (requireAuth && !session) {
    return fallback || null;
  }

  if (!requireAuth && session) {
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
