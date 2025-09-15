'use client'

import { ReactNode, useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'
import NavigationWrapper from '../../components/layout/NavigationWrapper'
import ProtectedRoute from '../../components/auth/ProtectedRoute'
import { motion } from 'framer-motion'
import { onAuthStateChange } from '@/lib/auth';

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
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    const unsubscribe = onAuthStateChange((user) => {
      setStatus(user ? 'authenticated' : 'unauthenticated')
    })
    return () => unsubscribe()
  }, [])

  // Add page view analytics
  useEffect(() => {
    if (pathname) {
      // Track page view - only in production or when needed
      if (process.env.NODE_ENV === 'development') {
        console.log(`Page view: ${pathname}`)
      }
      // Here you could add analytics tracking code for production
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
