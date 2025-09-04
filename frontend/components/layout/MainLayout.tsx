import React, { ReactNode } from 'react';
import Navbar from './Navbar';
import Footer from './Footer';
import { cn } from '../../lib/utils';
import { useSession } from 'next-auth/react';
import { Spinner } from '../ui/spinner';

interface MainLayoutProps {
  children: ReactNode;
  className?: string;
  hideFooter?: boolean;
  fullWidth?: boolean;
}

const MainLayout = ({
  children,
  className,
  hideFooter = false,
  fullWidth = false,
}: MainLayoutProps) => {
  const { status } = useSession();
  
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      
      <main className={cn(
        'flex-grow',
        fullWidth ? '' : 'container mx-auto px-4 py-6 md:py-12',
        className
      )}>
        {status === 'loading' ? (
          <div className="flex items-center justify-center h-[50vh]">
            <Spinner size="lg" />
          </div>
        ) : (
          children
        )}
      </main>
      
      {!hideFooter && <Footer />}
    </div>
  );
};

export default MainLayout;
