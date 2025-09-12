import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import './styles.css'
import { Providers } from './providers'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: {
    template: '%s | MisinfoGuard',
    default: 'MisinfoGuard - AI-powered Misinformation Detection Platform',
  },
  description: 'AI-powered platform for detecting and educating about misinformation',
  keywords: ['misinformation', 'fact-checking', 'AI', 'education', 'detection'],
  authors: [{ name: 'MisinfoGuard Team' }],
  robots: 'index, follow',
  openGraph: {
    title: 'MisinfoGuard - AI-powered Misinformation Detection Platform',
    description: 'AI-powered platform for detecting and educating about misinformation',
    type: 'website',
    locale: 'en_US',
    images: [{ url: '/images/og-image.jpg', width: 1200, height: 630 }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'MisinfoGuard - AI-powered Misinformation Detection Platform',
    description: 'AI-powered platform for detecting and educating about misinformation',
    images: ['/images/twitter-image.jpg'],
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/manifest.json',
  appleWebApp: {
    title: 'MisinfoGuard',
    statusBarStyle: 'black-translucent',
    capable: true,
  },
  other: {
    'mobile-web-app-capable': 'yes',
  },
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#111827' },
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{
          __html: `
            // Suppress MetaMask and other extension errors
            if (typeof window !== 'undefined') {
              const originalError = console.error;
              console.error = (...args) => {
                const message = args.join(' ').toLowerCase();
                // Suppress MetaMask and extension-related errors
                if (
                  message.includes('metamask') || 
                  message.includes('chrome-extension://') ||
                  message.includes('failed to connect to metamask') ||
                  message.includes('extension not found')
                ) {
                  return; // Suppress these errors
                }
                originalError.apply(console, args);
              };
              
              // Suppress unhandled promise rejections from extensions
              window.addEventListener('unhandledrejection', function(event) {
                const message = event.reason?.message?.toLowerCase() || '';
                if (
                  message.includes('metamask') || 
                  message.includes('extension') ||
                  message.includes('chrome-extension')
                ) {
                  event.preventDefault();
                  return;
                }
              });
            }
          `
        }} />
      </head>
      <body className={`${inter.className} h-full bg-gray-50 dark:bg-gray-900 antialiased`}>
        <Providers>
          <div className="min-h-full">
            {children}
          </div>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: 'var(--toaster-bg, #363636)',
                color: 'var(--toaster-color, #ffffff)',
                boxShadow: 'var(--toaster-shadow, 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06))',
              },
              className: '',
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#fff',
                },
                className: '!bg-green-50 !text-green-800 dark:!bg-green-900/50 dark:!text-green-200',
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
                className: '!bg-red-50 !text-red-800 dark:!bg-red-900/50 dark:!text-red-200',
              },
            }}
          />
        </Providers>
      </body>
    </html>
  )
}
