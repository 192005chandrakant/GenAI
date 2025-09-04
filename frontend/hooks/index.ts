import { useState, useEffect, useCallback } from 'react'
import { useSession } from 'next-auth/react'
import apiClient from '@/lib/api'
import { useRouter, usePathname } from 'next/navigation'
import { toast } from 'react-hot-toast'
import { useAnalysisStore, useNotificationStore } from '@/lib/store'

// Hook for handling authenticated routes
export function useRequireAuth(redirectTo = '/auth/login') {
  const { data: session, status } = useSession()
  const router = useRouter()
  
  useEffect(() => {
    if (status === 'loading') return
    
    if (!session) {
      router.push(`${redirectTo}?callbackUrl=${encodeURIComponent(window.location.href)}`)
    }
  }, [session, status, router, redirectTo])
  
  return { session, status }
}

// Hook for fetching user data
export function useUserProfile() {
  const { data: session } = useSession()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  
  const fetchUserProfile = useCallback(async () => {
    if (!session?.user) return
    
    try {
      setLoading(true)
      setError(null)
      const userData = await apiClient.getProfile()
      setUser(userData)
    } catch (err) {
      setError(err as Error)
      toast.error('Failed to load your profile')
    } finally {
      setLoading(false)
    }
  }, [session?.user])
  
  useEffect(() => {
    if (session?.user) {
      fetchUserProfile()
    }
  }, [session?.user, fetchUserProfile])
  
  return { user, loading, error, refetch: fetchUserProfile }
}

// Hook for checking content
export function useContentChecker() {
  const [isLoading, setIsLoading] = useState(false)
  const { setCurrentAnalysis, addToHistory } = useAnalysisStore()
  const router = useRouter()
  
  const checkContent = useCallback(async (
    contentType: 'text' | 'url' | 'image', 
    content: string | File,
    language: 'auto' | 'en' | 'hi' = 'auto'
  ) => {
    setIsLoading(true)
    try {
      let payload: string
      
      if (contentType === 'image' && content instanceof File) {
        // Upload the image first
        const uploadResponse = await apiClient.uploadFile(content)
        payload = uploadResponse.url
      } else {
        payload = content as string
      }
      
      // Submit the content for checking
      const checkResult = await apiClient.submitCheck({
        inputType: contentType,
        payload,
        language
      })
      
      // Update state
      setCurrentAnalysis(checkResult)
      addToHistory(checkResult)
      
      // Update the URL for sharing
      router.push(`/analyze?id=${checkResult.id}`, { scroll: false })
      
      return checkResult
    } catch (error) {
      toast.error('Failed to analyze content')
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [setCurrentAnalysis, addToHistory, router])
  
  return { checkContent, isLoading }
}

// Hook for handling form submission
export function useFormSubmit<T>(
  onSubmit: (data: T) => Promise<void>,
  successMessage = 'Success!'
) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const handleSubmit = useCallback(async (data: T) => {
    setIsSubmitting(true)
    setError(null)
    
    try {
      await onSubmit(data)
      toast.success(successMessage)
    } catch (err: any) {
      const message = err.message || 'Something went wrong'
      setError(message)
      toast.error(message)
    } finally {
      setIsSubmitting(false)
    }
  }, [onSubmit, successMessage])
  
  return { isSubmitting, error, handleSubmit }
}

// Hook for tracking page views
export function usePageView(pageTitle: string) {
  const pathname = usePathname()
  
  useEffect(() => {
    // Update page title
    document.title = `${pageTitle} | MisinfoGuard`
    
    // You could add analytics tracking here
    // Example: analytics.trackPageView(pathname)
    
  }, [pageTitle, pathname])
}

// Hook for handling notifications
export function useNotifications() {
  const { notifications, addNotification, markAsRead, clearNotification, clearAll } = useNotificationStore()
  
  const notifyUser = useCallback((
    message: string, 
    type: 'success' | 'error' | 'info' | 'warning' = 'info'
  ) => {
    addNotification({ message, type })
    
    // Also show a toast for immediate feedback
    switch (type) {
      case 'success':
        toast.success(message)
        break
      case 'error':
        toast.error(message)
        break
      case 'warning':
        toast.error(message)
        break
      default:
        toast(message)
    }
  }, [addNotification])
  
  return {
    notifications,
    notifyUser,
    markAsRead,
    clearNotification,
    clearAll,
    unreadCount: notifications.filter(n => !n.read).length
  }
}
