import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-blue-50">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🧠</span>
          <span className="text-xl font-semibold text-secondary">Animoa</span>
        </div>
        <nav className="flex gap-4">
          <Link
            href="/login"
            className="px-4 py-2 text-primary hover:text-primary-dark transition-colors"
          >
            Log In
          </Link>
          <Link
            href="/signup"
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
          >
            Sign Up
          </Link>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-4xl md:text-5xl font-bold text-secondary mb-6">
          Your Mental Health Companion
        </h1>
        <p className="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          A safe space for self-reflection and emotional support through
          thoughtful conversations, mood tracking, and personalized wellness insights.
        </p>
        <Link
          href="/signup"
          className="inline-block px-8 py-4 bg-primary text-white text-lg rounded-lg hover:bg-primary-dark transition-colors shadow-lg"
        >
          Get Started Free
        </Link>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            emoji="💬"
            title="AI Chat Companion"
            description="Have meaningful conversations with an empathetic AI that listens and supports you."
          />
          <FeatureCard
            emoji="📊"
            title="Mood Tracking"
            description="Track your emotional journey with visual insights and pattern recognition."
          />
          <FeatureCard
            emoji="📋"
            title="Wellness Assessment"
            description="Get personalized recommendations based on evidence-based mental health screenings."
          />
        </div>
      </section>

      {/* Disclaimer */}
      <section className="container mx-auto px-4 py-12">
        <div className="bg-amber-50 border-l-4 border-amber-400 p-6 rounded-r-lg max-w-3xl mx-auto">
          <h3 className="font-semibold text-amber-800 mb-2">Important Note</h3>
          <p className="text-amber-700 text-sm">
            Animoa is designed to provide support and general wellness information,
            not to replace professional mental health care. If you&apos;re experiencing
            a crisis or need immediate help, please contact a qualified healthcare
            provider or emergency services.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 text-center text-gray-500 text-sm">
        <p>&copy; {new Date().getFullYear()} Animoa. All rights reserved.</p>
      </footer>
    </main>
  )
}

function FeatureCard({
  emoji,
  title,
  description,
}: {
  emoji: string
  title: string
  description: string
}) {
  return (
    <div className="p-6 bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow">
      <div className="text-4xl mb-4">{emoji}</div>
      <h3 className="text-xl font-semibold text-secondary mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}
