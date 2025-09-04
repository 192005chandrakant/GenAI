// NavigationWrapper.tsx
'use client'

import { ReactNode, useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'
import ImprovedNavbar from './ImprovedNavbar'
import EnhancedLayout from './EnhancedLayout'

interface NavigationWrapperProps {
  children: ReactNode
  fullWidth?: boolean
  hideFooter?: boolean
  showBackToTop?: boolean
}

// Map route paths to page titles
const routeTitles: Record<string, string> = {
  '/': 'Home',
  '/analyze': 'Analyze Content',
  '/learn': 'Learning Center',
  '/community': 'Community',
  '/dashboard': 'Dashboard',
  '/dashboard/settings': 'Account Settings',
  '/dashboard/achievements': 'Achievements',
  '/dashboard/history': 'History',
  '/admin': 'Admin Panel',
}

// Routes that require authentication
const protectedRoutes = [
  '/dashboard',
  '/dashboard/settings',
  '/dashboard/achievements',
  '/dashboard/history',
]

// Routes that require admin privileges
const adminRoutes = [
  '/admin',
]

export default function NavigationWrapper({
  children,
  fullWidth = false,
  hideFooter = false,
  showBackToTop = true,
}: NavigationWrapperProps) {
  const pathname = usePathname()
  const [pageTitle, setPageTitle] = useState<string | undefined>(undefined)
  const [requireAuth, setRequireAuth] = useState(false)
  const [requireAdmin, setRequireAdmin] = useState(false)
  
  useEffect(() => {
    // Set page title based on route
    if (pathname) {
      // Check for exact route match
      if (routeTitles[pathname]) {
        setPageTitle(routeTitles[pathname])
      } else {
        // Check for parent route match
        const segments = pathname.split('/').filter(Boolean)
        const parentPath = segments.length > 1 ? `/${segments[0]}` : pathname
        setPageTitle(routeTitles[parentPath] || 'Page')
      }
      
      // Check if the route requires authentication
      const needsAuth = protectedRoutes.some(route => pathname.startsWith(route))
      setRequireAuth(needsAuth)
      
      // Check if the route requires admin privileges
      const needsAdmin = adminRoutes.some(route => pathname.startsWith(route))
      setRequireAdmin(needsAdmin)
    }
  }, [pathname])
  
  return (
    <EnhancedLayout
      pageTitle={pageTitle}
      fullWidth={fullWidth}
      hideFooter={hideFooter}
      showBackToTop={showBackToTop}
      requireAuth={requireAuth || requireAdmin}
      className="pb-10"
    >
      {children}
    </EnhancedLayout>
  )
}
