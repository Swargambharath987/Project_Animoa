'use client'

import { useState, useEffect, useCallback } from 'react'
import { usePathname } from 'next/navigation'
import SessionList from '@/components/chat/SessionList'
import type { ChatSession } from '@/types'

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [loading, setLoading] = useState(true)
  const pathname = usePathname()

  const fetchSessions = useCallback(async () => {
    try {
      const res = await fetch('/api/sessions')
      const data = await res.json()
      setSessions(data.sessions || [])
    } catch (error) {
      console.error('Failed to fetch sessions:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  // Fetch sessions on mount and when pathname changes
  useEffect(() => {
    fetchSessions()
  }, [fetchSessions, pathname])

  const handleSessionCreated = (session: ChatSession) => {
    setSessions((prev) => [session, ...prev])
  }

  const handleSessionDeleted = (sessionId: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== sessionId))
  }

  return (
    <div className="flex h-full">
      {/* Sessions Sidebar */}
      <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col pt-4 shrink-0">
        <h2 className="px-4 pb-3 text-sm font-semibold text-gray-500 uppercase tracking-wider">
          Conversations
        </h2>
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <SessionList
            sessions={sessions}
            onSessionCreated={handleSessionCreated}
            onSessionDeleted={handleSessionDeleted}
          />
        )}
      </div>

      {/* Chat Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {children}
      </div>
    </div>
  )
}
