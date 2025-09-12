/**
 * Custom hooks for the misinformation detection platform
 * Roadmap-compliant authentication and user management hooks
 */

import { useState, useEffect, useCallback } from 'react'
import apiClient from '@/lib/api'
import { useRouter, usePathname } from 'next/navigation'
import { toast } from 'react-hot-toast'
import { useAnalysisStore, useNotificationStore } from '@/lib/store'
import { useAuth } from '@/components/auth/AuthProvider'

// ============== ROADMAP-COMPLIANT AUTHENTICATION HOOKS ==============

/**
 * Hook for optional authentication - allows guest access (roadmap compliant)
 * Supports both guest and authenticated users for fact-checking
 */
export function useOptionalAuth() {
  const { 
    user, 
    userProfile, 
    userData, 
    loading, 
    isGuest, 
    guestId, 
    guestSession,
    upgradeGuestSession 
  } = useAuth()
  
  return { 
    // Firebase user object
    user, 
    // Full roadmap-compliant user profile
    userProfile,
    // Legacy compatibility
    userData, 
    loading, 
    
    // Guest functionality
    isGuest, 
    guestId,
    guestSession,
    
    // Unified authentication state
    isAuthenticated: !!user,
    userId: user?.uid || guestId || 'anonymous',
    
    // Fact-checking capabilities
    canPerformCheck: !loading && (!!user || (!!guestId && (guestSession?.checksRemaining || 0) > 0)),
    checksRemaining: user ? Infinity : (guestSession?.checksRemaining || 0),
    dailyLimit: guestSession?.dailyLimit || 10,
    isAtLimit: !user && (guestSession?.checksRemaining || 0) === 0,
    
    // Upgrade functionality
    upgradeGuestSession,
    shouldPromptUpgrade: isGuest && (guestSession?.checksRemaining || 0) <= 3,
  }
}

/**
 * Hook for components that require authentication (roadmap compliant)
 */
export function useRequiredAuth(redirectTo = '/auth/login') {
  const { user, userProfile, loading } = useAuth()
  const router = useRouter()
  const [isAuthorized, setIsAuthorized] = useState(false)
  
  useEffect(() => {
    if (loading) return
    
    if (!user) {
      router.push(`${redirectTo}?callbackUrl=${encodeURIComponent(window.location.href)}`)
    } else {
      setIsAuthorized(true)
    }
  }, [user, loading, router, redirectTo])
  
  return { 
    user, 
    userProfile, 
    loading, 
    isAuthorized,
    isAuthenticated: !!user 
  }
}

/**
 * Hook for admin-only features (roadmap compliant)
 */
export function useAdminAuth() {
  const { user, userProfile, loading } = useAuth()
  const router = useRouter()
  
  const isAdmin = userProfile?.is_admin || userProfile?.role === 'admin' || userProfile?.role === 'super_admin'
  
  useEffect(() => {
    if (loading) return
    
    if (!user || !isAdmin) {
      router.push('/unauthorized')
    }
  }, [user, isAdmin, loading, router])

  return {
    user,
    userProfile,
    loading,
    isAdmin,
    role: userProfile?.role || 'user',
    canManageUsers: userProfile?.role === 'admin' || userProfile?.role === 'super_admin',
    canModerateContent: isAdmin,
  }
}

/**
 * Hook for user profile management (roadmap compliant)
 */
export function useUserProfile() {
  const { userProfile, refreshProfile } = useAuth()
  const [updating, setUpdating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const updateProfile = useCallback(async (updates: any) => {
    setUpdating(true)
    setError(null)
    
    try {
      const token = localStorage.getItem('authToken')
      if (!token) {
        throw new Error('Not authenticated')
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      })

      if (!response.ok) {
        throw new Error('Failed to update profile')
      }

      await refreshProfile()
      toast.success('Profile updated successfully')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Update failed'
      setError(errorMessage)
      toast.error(errorMessage)
      throw err
    } finally {
      setUpdating(false)
    }
  }, [refreshProfile])

  return {
    user: userProfile,
    userProfile,
    loading: updating,
    error,
    updateProfile,
    refetch: refreshProfile,
    
    // Quick access to roadmap-compliant profile fields
    points: userProfile?.points || 0,
    level: userProfile?.level || 1,
    badges: userProfile?.badges || [],
    streakDays: userProfile?.streak_days || 0,
    totalChecks: userProfile?.total_checks || 0,
    accuracyScore: userProfile?.accuracy_score || 0,
    preferences: userProfile?.preferences,
    isAdmin: userProfile?.is_admin || false,
    role: userProfile?.role || 'user',
  }
}

// ============== FACT CHECKING HOOKS (ROADMAP COMPLIANT) ==============

/**
 * Hook for performing fact checks (works for both guest and authenticated users)
 * Roadmap compliant with daily limits and upgrade prompts
 */
export function useContentChecker() {
  const [isLoading, setIsLoading] = useState(false)
  const { setCurrentAnalysis, addToHistory } = useAnalysisStore()
  const { 
    isGuest, 
    guestId, 
    user, 
    canPerformCheck, 
    checksRemaining, 
    isAtLimit,
    upgradeGuestSession 
  } = useOptionalAuth()
  const router = useRouter()
  
  const checkContent = useCallback(async (
    contentType: 'text' | 'url' | 'image', 
    content: string | File,
    language: 'auto' | 'en' | 'hi' = 'auto'
  ) => {
    // Check if user can perform check
    if (!canPerformCheck) {
      if (isAtLimit) {
        toast.error('Daily limit reached! Sign up for unlimited access.')
        return null
      }
      throw new Error('Cannot perform check at this time')
    }

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
      
      // Determine endpoint based on user type (roadmap compliant)
      let endpoint: string
      let headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      
      if (user) {
        // Authenticated user - use full fact checking endpoint
        endpoint = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/checks`
        const token = localStorage.getItem('authToken')
        if (token) {
          headers['Authorization'] = `Bearer ${token}`
        }
      } else {
        // Guest user - use guest endpoint with limits
        endpoint = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/guest/check`
        if (guestId) {
          headers['X-Guest-ID'] = guestId
        }
      }
      
      // Submit the content for checking
      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          inputType: contentType,
          payload,
          language,
        }),
      })
      
      if (!response.ok) {
        if (response.status === 429) {
          // Rate limit hit - prompt for upgrade
          const errorData = await response.json()
          toast.error(errorData.detail?.message || 'Daily limit reached')
          return null
        }
        throw new Error('Failed to analyze content')
      }
      
      const checkResult = await response.json()
      
      // Update state
      setCurrentAnalysis(checkResult)
      addToHistory(checkResult)
      
      // Show upgrade prompt for guests approaching limit
      if (isGuest && checksRemaining <= 3) {
        toast.success('Check completed! Consider signing up for unlimited access.', {
          duration: 5000,
        })
      }
      
      // Update the URL for sharing
      router.push(`/analyze?id=${checkResult.id}`, { scroll: false })
      
      return checkResult
    } catch (error) {
      toast.error('Failed to analyze content')
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [
    canPerformCheck, 
    isAtLimit, 
    setCurrentAnalysis, 
    addToHistory, 
    router, 
    isGuest, 
    guestId, 
    user,
    checksRemaining
  ])
  
  return { 
    checkContent, 
    isLoading,
    canPerformCheck,
    checksRemaining,
    isAtLimit,
    isGuest,
    upgradeGuestSession,
  }
}

// ============== GAMIFICATION HOOKS (ROADMAP COMPLIANT) ==============

/**
 * Hook for gamification features according to roadmap
 */
export function useGamification() {
  const { userProfile } = useUserProfile()
  
  const getLevelProgress = useCallback(() => {
    if (!userProfile) return { current: 0, next: 100, percentage: 0 }
    
    const currentLevel = userProfile.level
    const currentPoints = userProfile.points
    
    // Roadmap-compliant level calculation
    const pointsForCurrentLevel = (currentLevel - 1) * 100
    const pointsForNextLevel = currentLevel * 100
    const pointsInCurrentLevel = currentPoints - pointsForCurrentLevel
    const pointsNeededForNext = pointsForNextLevel - pointsForCurrentLevel
    
    return {
      current: pointsInCurrentLevel,
      next: pointsNeededForNext,
      percentage: Math.min((pointsInCurrentLevel / pointsNeededForNext) * 100, 100),
    }
  }, [userProfile])

  const getStreakStatus = useCallback(() => {
    if (!userProfile) return { current: 0, isActive: false, nextMilestone: 7 }
    
    const current = userProfile.streak_days
    const milestones = [7, 30, 100, 365] // Roadmap-defined milestones
    const nextMilestone = milestones.find(m => m > current) || (current + 100)
    
    return {
      current,
      isActive: current > 0,
      nextMilestone,
      canEarnBadge: milestones.includes(current + 1),
    }
  }, [userProfile])

  return {
    userProfile,
    points: userProfile?.points || 0,
    level: userProfile?.level || 1,
    badges: userProfile?.badges || [],
    streakDays: userProfile?.streak_days || 0,
    totalChecks: userProfile?.total_checks || 0,
    accuracyScore: userProfile?.accuracy_score || 0,
    
    // Computed values according to roadmap
    levelProgress: getLevelProgress(),
    streakStatus: getStreakStatus(),
    
    // Achievement status
    hasAchievements: (userProfile?.badges || []).length > 0,
    canLevelUp: getLevelProgress().percentage >= 100,
  }
}

// ============== GUEST SESSION HOOKS (ROADMAP COMPLIANT) ==============

/**
 * Hook for managing guest sessions according to roadmap
 */
export function useGuestSession() {
  const { isGuest, guestId, guestSession, upgradeGuestSession } = useAuth()
  const [upgrading, setUpgrading] = useState(false)

  const promptForUpgrade = useCallback(() => {
    if (!isGuest) return
    
    // Use a simple toast message
    toast.error(
      `You have ${guestSession?.checksRemaining || 0} checks remaining today. Sign up for unlimited access!`,
      {
        duration: 6000,
      }
    )
  }, [isGuest, guestSession])

  const handleUpgrade = useCallback(async (authData: any) => {
    if (!isGuest || !guestId) return
    
    setUpgrading(true)
    try {
      await upgradeGuestSession(authData)
      toast.success('Welcome! Your session has been upgraded.')
    } catch (error) {
      console.error('Failed to upgrade guest session:', error)
      toast.error('Failed to upgrade session')
      throw error
    } finally {
      setUpgrading(false)
    }
  }, [isGuest, guestId, upgradeGuestSession])

  return {
    isGuest,
    guestId,
    guestSession,
    upgrading,
    checksRemaining: guestSession?.checksRemaining || 0,
    dailyLimit: guestSession?.dailyLimit || 10,
    isAtLimit: (guestSession?.checksRemaining || 0) === 0,
    shouldPromptUpgrade: isGuest && (guestSession?.checksRemaining || 0) <= 3,
    usagePercentage: guestSession ? (1 - (guestSession.checksRemaining / guestSession.dailyLimit)) * 100 : 0,
    promptForUpgrade,
    handleUpgrade,
  }
}

// ============== LEGACY COMPATIBILITY HOOKS ==============

/**
 * Legacy hook for handling authenticated routes (compatibility)
 */
export function useRequireAuth(redirectTo = '/auth/login') {
  return useRequiredAuth(redirectTo)
}

// ============== UTILITY HOOKS ==============

/**
 * Hook for handling form submission with loading states
 */
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

/**
 * Hook for tracking page views
 */
export function usePageView(pageTitle: string) {
  const pathname = usePathname()
  
  useEffect(() => {
    document.title = `${pageTitle} | MisinfoGuard`
  }, [pageTitle, pathname])
}

/**
 * Hook for handling notifications
 */
export function useNotifications() {
  const { notifications, addNotification, markAsRead, clearNotification, clearAll } = useNotificationStore()
  
  const notifyUser = useCallback((
    message: string, 
    type: 'success' | 'error' | 'info' | 'warning' = 'info'
  ) => {
    addNotification({ message, type })
    
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
