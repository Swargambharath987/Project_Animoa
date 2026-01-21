'use client'

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
  const pathname = usePathname()
  const router = useRouter()

  const handleLogout = async () => {
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/login')
    router.refresh()
  }

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-gray-200">
        <Link href="/chat" className="flex items-center gap-2">
          <span className="text-2xl">🧠</span>
          <span className="text-xl font-semibold text-secondary">Animoa</span>
        </Link>
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
  )
}
