'use client'

import { ReactNode, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { useSession } from 'next-auth/react'
import NavigationWrapper from '../../components/layout/NavigationWrapper'
import ProtectedRoute from '../../components/auth/ProtectedRoute'
import { motion } from 'framer-motion'

interface PageLayoutProps {
  children: ReactNode
  fullWidth?: boolean
  hideFooter?: boolean
  requireAuth?: boolean
  adminOnly?: boolean
}

const PageLayout = ({
  children,
  fullWidth = false,
  hideFooter = false,
  requireAuth = false,
  adminOnly = false,
}: PageLayoutProps) => {
  const pathname = usePathname()
  const { status } = useSession()
  
  // Add page view analytics
  useEffect(() => {
    if (pathname) {
      // Track page view
      console.log(`Page view: ${pathname}`)
      // Here you could add analytics tracking code
    }
  }, [pathname])
  
  // Render content
  const pageContent = (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      className="w-full"
    >
      {children}
    </motion.div>
  )

  // If authentication is required, wrap in ProtectedRoute
  const wrappedContent = requireAuth ? (
    <ProtectedRoute adminOnly={adminOnly}>
      {pageContent}
    </ProtectedRoute>
  ) : pageContent

  return (
    <NavigationWrapper 
      fullWidth={fullWidth}
      hideFooter={hideFooter}
    >
      {wrappedContent}
    </NavigationWrapper>
  )
}

export default PageLayout
