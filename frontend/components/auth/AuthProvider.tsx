import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from 'firebase/auth';
import { auth, onAuthStateChange } from '../../lib/firebase';

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  photo_url?: string;
  is_admin: boolean;
  role: 'user' | 'moderator' | 'admin' | 'super_admin';
  provider: 'firebase' | 'google' | 'github' | 'email';
  email_verified: boolean;
  points: number;
  level: number;
  badges: string[];
  streak_days: number;
  total_checks: number;
  accuracy_score: number;
  preferences: {
    language: string;
    notifications: boolean;
    privacy_level: 'public' | 'private' | 'restricted';
    analysis_mode: 'quick' | 'detailed' | 'expert';
    dark_mode: boolean;
  };
  created_at: string;
  last_login?: string;
  updated_at?: string;
}

interface AuthContextType {
  // Firebase user object
  user: User | null;
  // Full user profile from backend (roadmap compliant)
  userProfile: UserProfile | null;
  // Authentication loading state
  loading: boolean;
  // Legacy userData for backward compatibility
  userData: any;
  setUserData: (data: any) => void;
  // Guest access functionality
  isGuest: boolean;
  guestId: string | null;
  guestSession: {
    checksRemaining: number;
    dailyLimit: number;
    createdAt?: string;
  } | null;
  // Authentication functions
  refreshProfile: () => Promise<void>;
  upgradeGuestSession: (authData: any) => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  userProfile: null,
  loading: true,
  userData: null,
  setUserData: () => {},
  isGuest: false,
  guestId: null,
  guestSession: null,
  refreshProfile: async () => {},
  upgradeGuestSession: async () => {},
});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [userData, setUserData] = useState<any>(null); // Legacy compatibility
  const [loading, setLoading] = useState(true);
  const [guestId, setGuestId] = useState<string | null>(null);
  const [guestSession, setGuestSession] = useState<any>(null);

  // Generate or retrieve guest ID for unauthenticated users
  useEffect(() => {
    if (typeof window !== 'undefined') {
      let existingGuestId = localStorage.getItem('guestId');
      if (!existingGuestId) {
        existingGuestId = `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('guestId', existingGuestId);
      }
      setGuestId(existingGuestId);
      
      // Initialize guest session if not authenticated
      if (!user) {
        initializeGuestSession(existingGuestId);
      }
    }
  }, [user]);

  // Initialize guest session according to roadmap
  const initializeGuestSession = async (guestId: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/guest/session`, {
        headers: {
          'X-Guest-ID': guestId,
        },
      });
      
      if (response.ok) {
        const sessionData = await response.json();
        setGuestSession({
          checksRemaining: sessionData.checks_remaining,
          dailyLimit: sessionData.daily_limit,
          createdAt: sessionData.created_at,
        });
      } else {
        // Set default guest session
        setGuestSession({
          checksRemaining: 10,
          dailyLimit: 10,
        });
      }
    } catch (error) {
      console.warn('Could not fetch guest session, using defaults:', error);
      setGuestSession({
        checksRemaining: 10,
        dailyLimit: 10,
      });
    }
  };

  // Refresh user profile from backend
  const refreshProfile = async () => {
    if (!user) return;
    
    try {
      const idToken = await user.getIdToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const profile = await response.json();
        setUserProfile(profile);
        setUserData(profile); // Legacy compatibility
        localStorage.setItem('userProfile', JSON.stringify(profile));
        localStorage.setItem('authToken', idToken);
      } else {
        console.warn('Failed to fetch user profile from backend');
        // Create fallback profile from Firebase data
        createFallbackProfile();
      }
    } catch (error) {
      console.error('Error refreshing user profile:', error);
      createFallbackProfile();
    }
  };

  // Create fallback profile from Firebase user data
  const createFallbackProfile = () => {
    if (!user) return;
    
    const fallbackProfile: UserProfile = {
      id: user.uid,
      email: user.email || '',
      full_name: user.displayName || 'User',
      photo_url: user.photoURL || undefined,
      is_admin: false,
      role: 'user',
      provider: 'firebase',
      email_verified: user.emailVerified,
      points: 0,
      level: 1,
      badges: [],
      streak_days: 0,
      total_checks: 0,
      accuracy_score: 0.0,
      preferences: {
        language: 'en',
        notifications: true,
        privacy_level: 'public',
        analysis_mode: 'quick',
        dark_mode: false,
      },
      created_at: new Date().toISOString(),
    };
    
    setUserProfile(fallbackProfile);
    setUserData(fallbackProfile); // Legacy compatibility
    localStorage.setItem('userProfile', JSON.stringify(fallbackProfile));
  };

  // Upgrade guest session to authenticated user (ChatGPT-style)
  const upgradeGuestSession = async (authData: any) => {
    if (!guestId) return;
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/upgrade-guest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          guest_id: guestId,
          auth_request: authData,
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Guest session upgraded successfully:', result);
        
        // Clear guest data
        localStorage.removeItem('guestId');
        setGuestId(null);
        setGuestSession(null);
        
        // The Firebase auth state change will handle the rest
        return result;
      } else {
        console.warn('Failed to upgrade guest session');
      }
    } catch (error) {
      console.error('Error upgrading guest session:', error);
    }
  };

  // Listen for Firebase authentication state changes
  useEffect(() => {
    try {
      let unsubscribe = () => {};
      
      // Delay Firebase initialization slightly to improve page load
      const timeoutId = setTimeout(() => {
        try {
          unsubscribe = onAuthStateChange(async (firebaseUser) => {
            setUser(firebaseUser);
            
            if (firebaseUser) {
              // User is authenticated - fetch full profile
              setLoading(true);
              
              try {
                await refreshProfile();
              } catch (profileError) {
                console.error("Error refreshing profile:", profileError);
                // Fallback to basic user data
                createFallbackProfile();
              }
              
              // Clear guest session since user is now authenticated
              if (guestId) {
                localStorage.removeItem('guestId');
                setGuestId(null);
                setGuestSession(null);
              }
            } else {
              // User signed out - clear authenticated data but keep guest functionality
              setUserProfile(null);
              setUserData(null);
              localStorage.removeItem('userProfile');
              localStorage.removeItem('authToken');
              localStorage.removeItem('user'); // Legacy cleanup
              
              // Reinitialize guest session
              if (guestId) {
                initializeGuestSession(guestId);
              }
            }
            
            setLoading(false);
          });
        } catch (authError) {
          console.error("Auth state change subscription error:", authError);
          setLoading(false);
        }
      }, 500); // Short delay to prioritize layout loading

      // Cleanup function
      return () => {
        clearTimeout(timeoutId);
        if (typeof unsubscribe === 'function') {
          unsubscribe();
        }
      };
    } catch (error) {
      console.error("Critical auth error:", error);
      setLoading(false);
      return () => {};
    }
  }, [guestId]);

  // Load cached profile on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const cachedProfile = localStorage.getItem('userProfile');
      if (cachedProfile) {
        try {
          const profile = JSON.parse(cachedProfile);
          setUserProfile(profile);
          setUserData(profile); // Legacy compatibility
        } catch (error) {
          console.warn('Failed to parse cached profile:', error);
        }
      }
    }
  }, []);

  const value = {
    user,
    userProfile,
    loading,
    userData,
    setUserData,
    isGuest: !user,
    guestId,
    guestSession,
    refreshProfile,
    upgradeGuestSession,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
