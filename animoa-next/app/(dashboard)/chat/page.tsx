'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function ChatPage() {
  const router = useRouter()
  const [creating, setCreating] = useState(false)

  const handleNewChat = async () => {
    setCreating(true)
    try {
      const res = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New Chat' }),
      })
      const { session } = await res.json()
      if (session) {
        router.push(`/chat/${session.id}`)
      }
    } catch (error) {
      console.error('Failed to create session:', error)
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="flex-1 flex items-center justify-center bg-gray-50">
      <div className="text-center max-w-md px-6">
        <div className="text-6xl mb-6">💬</div>
        <h1 className="text-2xl font-semibold text-secondary mb-3">
          Welcome to Animoa
        </h1>
        <p className="text-gray-500 mb-8">
          Start a new conversation to begin your wellness journey.
          Your chats are private and saved securely.
        </p>
        <button
          onClick={handleNewChat}
          disabled={creating}
          className="px-8 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 text-lg font-medium"
        >
          {creating ? 'Starting...' : 'Start New Chat'}
        </button>
        <p className="text-xs text-gray-400 mt-6">
          Or select an existing conversation from the sidebar.
        </p>
      </div>
    </div>
  )
}
