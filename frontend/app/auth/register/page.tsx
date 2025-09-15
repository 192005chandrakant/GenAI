'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { UserPlus, Mail, Lock, User, Eye, EyeOff, Shield, ArrowLeft, Github } from 'lucide-react'
import { toast } from 'react-hot-toast'
import { signInWithGoogle, signUpWithEmail, signInWithGitHub } from '@/lib/firebase'
import { useAuth } from '@/components/auth/AuthProvider'

export default function RegisterPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    }>
      <RegisterPageContent />
    </Suspense>
  );
}

function RegisterPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const callbackUrl = searchParams.get('callbackUrl') || '/dashboard'
  const { user } = useAuth()
  
  const [isLoading, setIsLoading] = useState(false)
  const [isGoogleLoading, setIsGoogleLoading] = useState(false)
  const [isGithubLoading, setIsGithubLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  })

  // Redirect if already authenticated
  useEffect(() => {
    if (user) {
      router.push(callbackUrl)
    }
  }, [user, router, callbackUrl])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleEmailSignUp = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      toast.error('Password must be at least 6 characters long')
      return
    }

    setIsLoading(true)
    
    try {
      await signUpWithEmail(formData.email, formData.password, formData.fullName)
      toast.success('Account created successfully!')
      router.push(callbackUrl)
    } catch (error: any) {
      console.error('Sign up error:', error)
      
      // Handle specific Firebase errors
      if (error.code === 'auth/email-already-in-use') {
        toast.error('An account with this email already exists')
      } else if (error.code === 'auth/weak-password') {
        toast.error('Password is too weak')
      } else if (error.code === 'auth/invalid-email') {
        toast.error('Invalid email address')
      } else {
        toast.error(error.message || 'Failed to create account')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleSignUp = async () => {
    setIsLoading(true)
    
    try {
      await signInWithGoogle()
      toast.success('Successfully signed up with Google!')
      router.push(callbackUrl)
    } catch (error: any) {
      console.error('Google sign up error:', error)
      
      if (error.code === 'auth/popup-closed-by-user') {
        toast.error('Sign up was cancelled')
      } else if (error.code === 'auth/popup-blocked') {
        toast.error('Popup was blocked. Please allow popups and try again.')
      } else {
        toast.error(error.message || 'Failed to sign up with Google')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleGithubSignUp = async () => {
    setIsGithubLoading(true)
    
    try {
      await signInWithGitHub()
      toast.success('Successfully signed up with GitHub!')
      router.push(callbackUrl)
    } catch (error: any) {
      console.error('GitHub sign up error:', error)
      
      if (error.code === 'auth/popup-closed-by-user') {
        toast.error('Sign up was cancelled')
      } else if (error.code === 'auth/popup-blocked') {
        toast.error('Popup was blocked. Please allow popups and try again.')
      } else {
        toast.error(error.message || 'Failed to sign up with GitHub')
      }
    } finally {
      setIsGithubLoading(false)
    }
  }

  if (user) {
    return null // Don't render anything while redirecting
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900 p-4">
      {/* Back to Home Button */}
      <Link 
        href="/"
        className="fixed top-4 left-4 z-10 inline-flex items-center px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-white dark:hover:bg-gray-800 transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Home
      </Link>

      <div className="w-full max-w-md">
        <Card className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-8 shadow-lg">
          <div className="text-center mb-8">
            <Link href="/" className="inline-flex items-center space-x-2 mb-4">
              <Shield className="w-10 h-10 text-blue-600 dark:text-blue-400" />
              <span className="text-2xl font-bold text-gray-800 dark:text-white">MisinfoGuard</span>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create Account</h1>
            <p className="text-gray-600 dark:text-gray-300 mt-2">
              Join us to start detecting misinformation
            </p>
          </div>

          {/* OAuth Sign Up Buttons */}
          <div className="space-y-3 mb-6">
            {/* Google Sign Up Button */}
            <Button
              type="button"
              onClick={handleGoogleSignUp}
              className="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 hover:text-gray-900 dark:hover:text-white"
              disabled={isLoading || isGoogleLoading || isGithubLoading}
            >
              {isGoogleLoading ? (
                <Spinner size="sm" className="mr-2" />
              ) : (
                <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
              )}
              Continue with Google
            </Button>

            {/* GitHub Sign Up Button */}
            <Button
              type="button"
              onClick={handleGithubSignUp}
              className="w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 hover:text-gray-900 dark:hover:text-white"
              disabled={isLoading || isGoogleLoading || isGithubLoading}
            >
              {isGithubLoading ? (
                <Spinner size="sm" className="mr-2" />
              ) : (
                <Github className="mr-2 h-4 w-4" />
              )}
              Continue with GitHub
            </Button>
          </div>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300 dark:border-gray-600" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-white dark:bg-gray-800 px-2 text-gray-500">Or continue with email</span>
            </div>
          </div>

          <form onSubmit={handleEmailSignUp} className="space-y-6">
            <div>
              <Label htmlFor="fullName" className="text-gray-700 dark:text-gray-200">
                Full Name
              </Label>
              <div className="relative mt-1">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  id="fullName"
                  name="fullName"
                  type="text"
                  required
                  value={formData.fullName}
                  onChange={handleInputChange}
                  className="pl-10 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400"
                  placeholder="Enter your full name"
                  disabled={isLoading}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="email" className="text-gray-700 dark:text-gray-200">
                Email address
              </Label>
              <div className="relative mt-1">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  className="pl-10 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400"
                  placeholder="Enter your email"
                  disabled={isLoading}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="password" className="text-gray-700 dark:text-gray-200">
                Password
              </Label>
              <div className="relative mt-1">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="pl-10 pr-10 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400"
                  placeholder="Create a password"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <div>
              <Label htmlFor="confirmPassword" className="text-gray-700 dark:text-gray-200">
                Confirm Password
              </Label>
              <div className="relative mt-1">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="pl-10 pr-10 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400"
                  placeholder="Confirm your password"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Creating Account...
                </>
              ) : (
                <>
                  <UserPlus className="mr-2 h-4 w-4" />
                  Create Account
                </>
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Already have an account?{' '}
              <Link
                href={`/auth/login${callbackUrl ? `?callbackUrl=${encodeURIComponent(callbackUrl)}` : ''}`}
                className="font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300"
              >
                Sign in here
              </Link>
            </p>
          </div>

          <div className="mt-4 text-center">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              By creating an account, you agree to our{' '}
              <Link href="/terms" className="underline hover:text-gray-700 dark:hover:text-gray-300">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="underline hover:text-gray-700 dark:hover:text-gray-300">
                Privacy Policy
              </Link>
            </p>
          </div>
        </Card>
      </div>
    </div>
  )
}
