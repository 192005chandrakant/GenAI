# GenAI Frontend Developer Guide

This comprehensive guide provides detailed information for frontend developers working on the GenAI Misinformation Defense Platform. It covers architecture, components, state management, and development best practices.

## 🏗️ Frontend Architecture

### Core Components

```
frontend/
├── app/                 # Next.js app router
│   ├── globals.css      # Global styles
│   ├── layout.tsx       # Root layout
│   ├── page.tsx         # Home page
│   ├── admin/           # Admin dashboard
│   ├── analyze/         # Analysis pages
│   ├── auth/            # Authentication pages
│   ├── community/       # Community features
│   ├── dashboard/       # User dashboard
│   ├── gamification/    # Gamification features
│   └── learn/           # Learning platform
├── components/          # Reusable UI components
│   ├── auth/            # Authentication components
│   ├── common/          # Common utility components
│   ├── dashboard/       # Dashboard components
│   ├── layout/          # Layout components
│   └── ui/              # UI elements and primitives
├── hooks/               # Custom React hooks
├── lib/                 # Utility functions and services
│   ├── api.ts           # API client
│   ├── auth.ts          # Auth utilities
│   ├── firebase.ts      # Firebase configuration
│   ├── store.ts         # Global state management
│   └── utils.ts         # Helper functions
├── public/              # Static assets
└── styles/              # CSS modules and stylesheets
```

### Project Organization

The frontend follows Next.js App Router architecture:

1. **App Directory** (`app/`) - Page routes and layouts
2. **Components** (`components/`) - Reusable UI components
3. **Libraries** (`lib/`) - Utilities and services
4. **Public** (`public/`) - Static assets
5. **Styles** (`styles/`) - Global styles and theming

## 🚀 Development Environment

### Prerequisites

- Node.js 18+
- npm or yarn
- Access to Firebase project

### Local Setup

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your settings

# Start development server
npm run dev
```

## 🧩 Key Components

### UI Component Library

The project uses [shadcn/ui](https://ui.shadcn.com/) for UI components:

```tsx
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card"

export default function LoginForm() {
  return (
    <Card>
      <CardHeader>Login</CardHeader>
      <CardContent>
        <Input placeholder="Email" />
        <Input type="password" placeholder="Password" />
      </CardContent>
      <CardFooter>
        <Button>Sign in</Button>
      </CardFooter>
    </Card>
  )
}
```

### Layout Components

Common layout components in `components/layout/`:

```tsx
// components/layout/AppShell.tsx
import { Navbar } from "./Navbar"
import { Sidebar } from "./Sidebar"
import { Footer } from "./Footer"

export function AppShell({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-4">{children}</main>
      </div>
      <Footer />
    </div>
  )
}
```

### Authentication Components

User authentication flow in `components/auth/`:

```tsx
// components/auth/SignInForm.tsx
import { useState } from "react"
import { signInWithEmailAndPassword } from "firebase/auth"
import { auth } from "@/lib/firebase"

export function SignInForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await signInWithEmailAndPassword(auth, email, password)
      // Success handling
    } catch (error) {
      // Error handling
    }
  }
  
  // Form implementation
}
```

## 📊 State Management

### Firebase Authentication

The project uses Firebase for authentication:

```tsx
// lib/firebase.ts
import { initializeApp } from "firebase/app"
import { getAuth } from "firebase/auth"

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID
}

const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)
```

### Authentication Hook

Custom hook for auth state:

```tsx
// hooks/useAuth.ts
import { useState, useEffect } from "react"
import { onAuthStateChanged, User } from "firebase/auth"
import { auth } from "@/lib/firebase"

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user)
      setLoading(false)
    })

    return unsubscribe
  }, [])

  return { user, loading }
}
```

### Global State

For global state management, the project uses React Context:

```tsx
// lib/store.ts
import { createContext, useContext, useState, ReactNode } from "react"

type AppState = {
  darkMode: boolean
  toggleDarkMode: () => void
}

const AppContext = createContext<AppState | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
  const [darkMode, setDarkMode] = useState(false)

  const toggleDarkMode = () => setDarkMode(!darkMode)

  return (
    <AppContext.Provider value={{ darkMode, toggleDarkMode }}>
      {children}
    </AppContext.Provider>
  )
}

export function useAppState() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error("useAppState must be used within an AppProvider")
  }
  return context
}
```

## 🔄 API Integration

### API Client

The project uses a custom API client for backend communication:

```tsx
// lib/api.ts
import axios from "axios"
import { auth } from "./firebase"

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    "Content-Type": "application/json"
  }
})

// Add authentication token to requests
api.interceptors.request.use(async (config) => {
  const user = auth.currentUser
  if (user) {
    const token = await user.getIdToken()
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors (authentication, validation, etc.)
    return Promise.reject(error)
  }
)

export default api
```

### API Hooks

Custom hooks for API requests:

```tsx
// hooks/useFactCheck.ts
import { useState } from "react"
import api from "@/lib/api"

export function useFactCheck() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [result, setResult] = useState(null)

  const checkContent = async (data) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await api.post("/api/v1/checks", data)
      setResult(response.data)
      return response.data
    } catch (err) {
      setError(err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { checkContent, loading, error, result }
}
```

## 📱 Responsive Design

### Mobile-First Approach

The project follows mobile-first design principles:

```css
/* Base styles for mobile */
.container {
  padding: 1rem;
}

/* Tablet styles */
@media (min-width: 640px) {
  .container {
    padding: 2rem;
  }
}

/* Desktop styles */
@media (min-width: 1024px) {
  .container {
    padding: 3rem;
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

### Responsive Components

Components are designed to be responsive:

```tsx
// Responsive card grid
<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
  {items.map(item => (
    <Card key={item.id}>
      {/* Card content */}
    </Card>
  ))}
</div>
```

## 🌐 Internationalization

### Multi-language Support

The project uses [next-intl](https://next-intl-docs.vercel.app/) for internationalization:

```tsx
// messages/en.json
{
  "common": {
    "title": "Misinformation Defense",
    "tagline": "AI-powered fact-checking"
  },
  "auth": {
    "signin": "Sign In",
    "signup": "Sign Up",
    "logout": "Log Out"
  }
}

// messages/hi.json
{
  "common": {
    "title": "मिथ्या सूचना सुरक्षा",
    "tagline": "AI-संचालित तथ्य जांच"
  },
  "auth": {
    "signin": "साइन इन करें",
    "signup": "साइन अप करें",
    "logout": "लॉग आउट"
  }
}
```

### Translation Hook

```tsx
// hooks/useTranslation.ts
import { useTranslations } from 'next-intl'

export function useAppTranslation() {
  const t = useTranslations()
  return { t }
}

// Usage
const { t } = useAppTranslation()
<h1>{t('common.title')}</h1>
```

## 🔒 Security Best Practices

### Protected Routes

Implement route protection:

```tsx
// app/dashboard/layout.tsx
import { redirect } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'

export default function DashboardLayout({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div>Loading...</div>
  }
  
  if (!user) {
    redirect('/auth/signin')
  }
  
  return <div>{children}</div>
}
```

### Content Security Policy

Configure CSP in `next.config.js`:

```js
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-inline' https://apis.google.com;"
          }
        ]
      }
    ]
  }
}
```

## 🧪 Testing

### Jest and React Testing Library

```tsx
// components/auth/__tests__/SignInForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { SignInForm } from '../SignInForm'
import { signInWithEmailAndPassword } from 'firebase/auth'

// Mock Firebase
jest.mock('firebase/auth', () => ({
  signInWithEmailAndPassword: jest.fn()
}))

describe('SignInForm', () => {
  it('submits the form with email and password', async () => {
    render(<SignInForm />)
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'user@example.com' }
    })
    
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    })
    
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))
    
    await waitFor(() => {
      expect(signInWithEmailAndPassword).toHaveBeenCalledWith(
        expect.anything(),
        'user@example.com',
        'password123'
      )
    })
  })
})
```

### End-to-End Testing with Playwright

```tsx
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test('user can sign in', async ({ page }) => {
  // Navigate to the sign-in page
  await page.goto('/auth/signin')
  
  // Fill in the form
  await page.fill('input[name="email"]', 'user@example.com')
  await page.fill('input[name="password"]', 'password123')
  
  // Click the sign-in button
  await page.click('button:has-text("Sign In")')
  
  // Expect to be redirected to the dashboard
  await expect(page).toHaveURL('/dashboard')
  
  // Expect the user's name to be displayed
  await expect(page.locator('text=Welcome back')).toBeVisible()
})
```

## 🎨 Styling and Theming

### Tailwind CSS

The project uses Tailwind CSS for styling:

```tsx
// Button component with variants
<button className="px-4 py-2 rounded font-medium transition-colors
  bg-blue-600 hover:bg-blue-700 text-white
  dark:bg-blue-800 dark:hover:bg-blue-900">
  Click me
</button>
```

### Dark Mode Support

Implementation of dark mode:

```tsx
// app/providers.tsx
'use client'

import { ThemeProvider } from 'next-themes'

export function Providers({ children }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </ThemeProvider>
  )
}

// Usage in layout.tsx
import { Providers } from './providers'

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}

// Theme toggle component
import { useTheme } from 'next-themes'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  
  return (
    <button
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="p-2 rounded-full bg-gray-200 dark:bg-gray-800"
    >
      {theme === 'dark' ? '🌞' : '🌙'}
    </button>
  )
}
```

## 📱 PWA Support

### Progressive Web App Configuration

Setup PWA support with Next.js:

```js
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development'
})

module.exports = withPWA({
  // Next.js config
})
```

### Web App Manifest

```json
// public/manifest.json
{
  "name": "Misinformation Defense",
  "short_name": "MisinfoDef",
  "description": "AI-powered misinformation detection and fact checking",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### Service Worker

Service worker for offline support:

```js
// public/sw.js
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('misinfodefense-v1').then((cache) => {
      return cache.addAll([
        '/',
        '/offline',
        '/styles.css',
        '/app.js',
        '/logo.png'
      ])
    })
  )
})

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request).catch(() => {
        return caches.match('/offline')
      })
    })
  )
})
```

## 📊 Analytics and Monitoring

### Google Analytics Integration

```tsx
// lib/analytics.ts
export const GA_TRACKING_ID = process.env.NEXT_PUBLIC_GA_ID

// Track page views
export const pageview = (url) => {
  window.gtag('config', GA_TRACKING_ID, {
    page_path: url,
  })
}

// Track events
export const event = ({ action, category, label, value }) => {
  window.gtag('event', action, {
    event_category: category,
    event_label: label,
    value: value,
  })
}
```

### Error Logging

```tsx
// lib/errorReporting.ts
export function logError(error, context = {}) {
  // Send to your error reporting service
  console.error('Error:', error, context)
  
  if (process.env.NEXT_PUBLIC_ENVIRONMENT !== 'development') {
    // Send to backend error logging endpoint
    fetch('/api/log-error', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: error.message, stack: error.stack, context })
    }).catch(console.error)
  }
}
```

## 🚀 Build and Deployment

### Build Process

```bash
# Create production build
npm run build

# Start production server
npm start
```

### Environment Configuration

The build process uses environment variables from `.env.production`:

```
NEXT_PUBLIC_API_URL=https://api.misinfodefense.com
NEXT_PUBLIC_FIREBASE_API_KEY=production-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=production-project.firebaseapp.com
# Other production variables
```

### Firebase Hosting Deployment

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase project
firebase init hosting

# Deploy to Firebase
firebase deploy --only hosting
```

## 📝 Contributing to Frontend

### Development Workflow

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement Changes**:
   - Follow project coding standards
   - Add tests for new functionality
   - Update documentation

3. **Run Tests Locally**:
   ```bash
   npm run test
   ```

4. **Submit Pull Request**:
   - Describe changes in detail
   - Reference related issues
   - Ensure CI checks pass

### Code Style Guidelines

The project follows these coding standards:
- ESLint for code quality
- Prettier for formatting
- TypeScript for type checking

## 🧩 Frontend Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Firebase Documentation](https://firebase.google.com/docs)

---

This guide provides a comprehensive reference for frontend developers working on the GenAI Misinformation Defense Platform. For setup instructions, see the [Unified Setup Guide](../docs/UNIFIED_SETUP_GUIDE.md).