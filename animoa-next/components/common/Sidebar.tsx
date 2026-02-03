'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { cn } from '@/lib/utils'

interface SidebarProps {
  userEmail: string
}

const navItems = [
  { href: '/chat', label: 'Chat', emoji: '💬' },
  { href: '/mood', label: 'Mood Tracker', emoji: '📊' },
  { href: '/assessment', label: 'Assessment', emoji: '📋' },
  { href: '/profile', label: 'Profile', emoji: '👤' },
]

export default function Sidebar({ userEmail }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()
  const router = useRouter()

  // Close sidebar on route change (mobile)
  useEffect(() => {
    setIsOpen(false)
  }, [pathname])

  const handleLogout = async () => {
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/login')
    router.refresh()
  }

  return (
    <>
      {/* Mobile header bar */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-40 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <button
          onClick={() => setIsOpen(true)}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Open menu"
        >
          <svg className="w-6 h-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <Link href="/chat" className="flex items-center gap-2">
          <span className="text-xl">🧠</span>
          <span className="text-lg font-semibold text-secondary">Animoa</span>
        </Link>
        <div className="w-10" /> {/* Spacer for centering */}
      </div>

      {/* Backdrop overlay (mobile) */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-black/50"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed lg:relative z-50 h-full w-64 bg-white border-r border-gray-200 flex flex-col shrink-0 transition-transform duration-200',
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Logo */}
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <Link href="/chat" className="flex items-center gap-2">
            <span className="text-2xl">🧠</span>
            <span className="text-xl font-semibold text-secondary">Animoa</span>
          </Link>
          {/* Close button (mobile) */}
          <button
            onClick={() => setIsOpen(false)}
            className="lg:hidden p-1 hover:bg-gray-100 rounded transition-colors"
            aria-label="Close menu"
          >
            <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                    pathname.startsWith(item.href)
                      ? 'bg-primary text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  )}
                >
                  <span className="text-xl">{item.emoji}</span>
                  <span>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-sm text-gray-500 mb-2 truncate" title={userEmail}>
            {userEmail}
          </div>
          <button
            onClick={handleLogout}
            className="w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors text-left"
          >
            Log out
          </button>
        </div>
      </aside>
    </>
  )
}
