import type { Metadata } from 'next'
import Link from 'next/link'
import ImprovedNavbar from '../../components/layout/ImprovedNavbar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Shield, Target, BookOpen, Users, Cpu, Globe, Sparkles, Heart } from 'lucide-react'

export const metadata: Metadata = {
  title: 'About',
  description: 'Learn about MisinfoGuard — our mission, values, and the technology powering AI-driven misinformation detection and education.'
}

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
      {/* Global Nav */}
      <ImprovedNavbar />

      {/* Hero */}
      <section className="pt-20 pb-16">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-100 dark:bg-blue-900/40 mb-4">
              <Shield className="w-7 h-7 text-blue-600 dark:text-blue-400" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">About MisinfoGuard</h1>
            <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 mb-6">
              We build trustworthy AI tools to help people detect misinformation, learn critical thinking skills, and make informed decisions online.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link href="/analyze" className="btn btn-primary">Try the Analyzer</Link>
              <Link href="/learn" className="btn btn-outline">Explore Learning</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Mission & Values */}
      <section className="py-12">
        <div className="container">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Target className="w-5 h-5 text-blue-600" /> Mission</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-700 dark:text-gray-300">
                Empower everyone to spot misleading content and build resilient digital communities.
              </CardContent>
            </Card>
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><BookOpen className="w-5 h-5 text-green-600" /> Education</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-700 dark:text-gray-300">
                Practical modules, quizzes, and resources that teach verification skills and media literacy.
              </CardContent>
            </Card>
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Users className="w-5 h-5 text-purple-600" /> Community</CardTitle>
              </CardHeader>
              <CardContent className="text-gray-700 dark:text-gray-300">
                A supportive space to share insights, discuss trends, and report suspicious content.
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* What we do */}
      <section className="py-12 bg-white dark:bg-gray-900">
        <div className="container">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">What We Do</h2>
            <p className="text-gray-600 dark:text-gray-300 mt-2">AI detection + educational guidance, designed for everyday users and researchers.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="p-6 dark:bg-gray-800 dark:border-gray-700">
              <div className="flex items-center gap-3 mb-3">
                <Cpu className="w-5 h-5 text-indigo-600" />
                <h3 className="font-semibold text-gray-900 dark:text-white">Multi‑modal AI Analysis</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">Analyze text, images, and links with explainable scores and references.</p>
            </Card>
            <Card className="p-6 dark:bg-gray-800 dark:border-gray-700">
              <div className="flex items-center gap-3 mb-3">
                <BookOpen className="w-5 h-5 text-emerald-600" />
                <h3 className="font-semibold text-gray-900 dark:text-white">Interactive Learning</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">Bite‑sized lessons and quizzes to build lasting fact‑checking habits.</p>
            </Card>
            <Card className="p-6 dark:bg-gray-800 dark:border-gray-700">
              <div className="flex items-center gap-3 mb-3">
                <Globe className="w-5 h-5 text-sky-600" />
                <h3 className="font-semibold text-gray-900 dark:text-white">Open & Global</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">Accessible on the web, with internationalization and inclusive design.</p>
            </Card>
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-12">
        <div className="container">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Technology We Use</h2>
            <p className="text-gray-600 dark:text-gray-300 mt-2">Modern, scalable, and developer‑friendly.</p>
          </div>
          <div className="flex flex-wrap justify-center gap-2">
            {['Next.js', 'React', 'TypeScript', 'Tailwind', 'FastAPI', 'Python', 'Firebase', 'Cloudinary'].map(t => (
              <Badge key={t} variant="outline" className="text-sm py-1 px-3">{t}</Badge>
            ))}
          </div>
        </div>
      </section>

      {/* Team placeholder */}
      <section className="py-12 bg-white dark:bg-gray-900">
        <div className="container">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Who We Are</h2>
            <p className="text-gray-600 dark:text-gray-300 mt-2">A small team passionate about truth, safety, and education.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[{name:'Product & Research', color:'text-blue-600'}, {name:'Engineering', color:'text-emerald-600'}, {name:'Community & Ops', color:'text-purple-600'}].map((role, idx) => (
              <Card key={idx} className="dark:bg-gray-800 dark:border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white">Team Member</p>
                      <p className={`text-sm ${role.color}`}>{role.name}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Impact & CTA */}
      <section className="py-16">
        <div className="container">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
            <div className="lg:col-span-2">
              <Card className="dark:bg-gray-800 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-yellow-500" /> Impact so far
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    {[{k:'Analyses', v:'25K+'}, {k:'Modules Learned', v:'5K+'}, {k:'Community Posts', v:'1.2K+'}, {k:'Accuracy', v:'90%+'}].map((s) => (
                      <div key={s.k} className="text-center">
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">{s.v}</div>
                        <div className="text-sm text-gray-600 dark:text-gray-300">{s.k}</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
            <div>
              <Card className="dark:bg-gray-800 dark:border-gray-700">
                <CardContent className="p-6 flex flex-col items-start gap-3">
                  <div className="inline-flex items-center gap-2 text-pink-600">
                    <Heart className="w-5 h-5" />
                    <span className="font-medium">Get involved</span>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300">Join our community, contribute feedback, and help others learn.</p>
                  <div className="flex gap-2">
                    <Link href="/community" className="btn btn-primary">Visit Community</Link>
                    <Link href="/learn" className="btn btn-outline">Start Learning</Link>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
