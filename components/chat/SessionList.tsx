'use client'

import { useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { formatDate } from '@/lib/utils'
import type { ChatSession } from '@/types'

interface SessionListProps {
  sessions: ChatSession[]
  onSessionCreated: (session: ChatSession) => void
  onSessionDeleted: (sessionId: string) => void
}

export default function SessionList({
  sessions,
  onSessionCreated,
  onSessionDeleted,
}: SessionListProps) {
  const router = useRouter()
  const pathname = usePathname()
  const [isCreating, setIsCreating] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const currentSessionId = pathname.split('/chat/')[1]

  const handleNewChat = async () => {
    setIsCreating(true)
    try {
      const res = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New Chat' }),
      })
      const { session } = await res.json()
      if (session) {
        onSessionCreated(session)
        router.push(`/chat/${session.id}`)
      }
    } catch (error) {
      console.error('Failed to create session:', error)
    } finally {
      setIsCreating(false)
    }
  }

  const handleDelete = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation()
    if (!confirm('Delete this conversation? This cannot be undone.')) return

    setDeletingId(sessionId)
    try {
      await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' })
      onSessionDeleted(sessionId)
      if (currentSessionId === sessionId) {
        router.push('/chat')
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* New Chat Button */}
      <button
        onClick={handleNewChat}
        disabled={isCreating}
        className="mx-3 mb-3 px-4 py-2.5 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 text-sm font-medium flex items-center justify-center gap-2"
      >
        <span>+</span>
        {isCreating ? 'Creating...' : 'New Chat'}
      </button>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto space-y-1 px-2">
        {sessions.length === 0 ? (
          <p className="text-xs text-gray-400 text-center mt-4 px-2">
            No conversations yet. Start a new chat!
          </p>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => router.push(`/chat/${session.id}`)}
              className={cn(
                'group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-colors text-sm',
                currentSessionId === session.id
                  ? 'bg-primary/10 text-primary'
                  : 'text-gray-600 hover:bg-gray-100'
              )}
            >
              <span className="text-base">💬</span>
              <div className="flex-1 min-w-0">
                <p className="truncate font-medium">{session.title}</p>
                <p className="text-xs text-gray-400 truncate">
                  {formatDate(session.created_at)}
                </p>
              </div>
              <button
                onClick={(e) => handleDelete(e, session.id)}
                disabled={deletingId === session.id}
                className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-all"
                title="Delete conversation"
              >
                {deletingId === session.id ? '...' : '✕'}
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
