'use client'

import Link from 'next/link'
import { Shield, Brain, Globe, Award, Users, Zap } from 'lucide-react'
import ImprovedNavbar from '../components/layout/ImprovedNavbar'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
      <ImprovedNavbar />

      {/* Hero Section */}
      <section className="pt-20 pb-32 bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
        <div className="container">
          <div className="text-center max-w-4xl mx-auto animate-fade-in">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6 leading-tight">
              Fight <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">Misinformation</span> with AI
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
              Advanced AI-powered platform to detect, analyze, and educate about misinformation across all media types.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                href="/analyze"
                className="btn btn-primary btn-lg animate-slide-up"
                style={{ animationDelay: '100ms' }}
              >
                Start Analyzing
              </Link>
              <Link
                href="/learn"
                className="btn btn-outline btn-lg animate-slide-up"
                style={{ animationDelay: '200ms' }}
              >
                Learn More
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white dark:bg-gray-800">
        <div className="container">
          <div className="text-center mb-16 animate-fade-in">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Why Choose Our Platform?
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Advanced AI technology combined with educational resources to help you navigate the digital world safely.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="card dark:bg-gray-700 dark:border-gray-600 p-8 text-center hover:shadow-elevation-2 transition-all duration-300 animate-slide-up">
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                <Shield className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">AI-Powered Detection</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Advanced machine learning algorithms analyze content for potential misinformation with high accuracy.
              </p>
            </div>

            <div className="card dark:bg-gray-700 dark:border-gray-600 p-8 text-center hover:shadow-elevation-2 transition-all duration-300 animate-slide-up" style={{ animationDelay: '100ms' }}>
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                <Brain className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Educational Content</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Learn about misinformation patterns, fact-checking techniques, and digital literacy skills.
              </p>
            </div>

            <div className="card dark:bg-gray-700 dark:border-gray-600 p-8 text-center hover:shadow-elevation-2 transition-all duration-300 animate-slide-up" style={{ animationDelay: '200ms' }}>
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                <Globe className="w-8 h-8 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Multi-Language Support</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Analyze content in multiple languages with automatic translation and detection capabilities.
              </p>
            </div>

            <div className="card dark:bg-gray-700 dark:border-gray-600 p-8 text-center hover:shadow-elevation-2 transition-all duration-300 animate-slide-up" style={{ animationDelay: '300ms' }}>
              <div className="w-16 h-16 bg-yellow-100 dark:bg-yellow-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                <Award className="w-8 h-8 text-yellow-600 dark:text-yellow-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Gamified Learning</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Earn points, complete challenges, and track your progress in becoming a misinformation expert.
              </p>
            </div>

            <div className="card dark:bg-gray-700 dark:border-gray-600 p-8 text-center hover:shadow-elevation-2 transition-all duration-300 animate-slide-up" style={{ animationDelay: '400ms' }}>
              <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                <Users className="w-8 h-8 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Community Reports</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Contribute to the community by reporting suspicious content and helping others stay informed.
              </p>
            </div>

            <div className="card dark:bg-gray-700 dark:border-gray-600 p-8 text-center hover:shadow-elevation-2 transition-all duration-300 animate-slide-up" style={{ animationDelay: '500ms' }}>
              <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                <Zap className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Real-time Analysis</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Get instant results with our powerful AI system that processes content in real-time.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900">
        <div className="container">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Simple, fast, and accurate misinformation detection in three easy steps.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-20 h-20 bg-blue-600 dark:bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-6 text-white text-2xl font-bold">
                1
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Submit Content</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Upload text, images, videos, or paste URLs for analysis.
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-purple-600 dark:bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-6 text-white text-2xl font-bold">
                2
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">AI Analysis</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Our advanced AI algorithms analyze the content for misinformation patterns.
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-green-600 dark:bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6 text-white text-2xl font-bold">
                3
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Get Results</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Receive detailed analysis with confidence scores and explanations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-700 dark:to-purple-700">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Ready to Fight Misinformation?
            </h2>
            <p className="text-xl mb-8 max-w-2xl mx-auto text-white/90">
              Join thousands of users who are already protecting themselves and their communities from false information.
            </p>
            <Link
              href="/analyze"
              className="inline-flex items-center justify-center px-8 py-4 bg-white text-blue-600 dark:text-blue-700 rounded-full font-medium hover:bg-gray-50 dark:hover:bg-gray-100 transition-colors shadow-elevation-2 hover:shadow-elevation-3"
            >
              Get Started Now
            </Link>
          </div>
        </div>
      </section>

    </div>
  )
}
