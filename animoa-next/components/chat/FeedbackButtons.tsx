'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'

const FEEDBACK_EMOJIS = [
  { emoji: '👍', label: 'Helpful' },
  { emoji: '❤️', label: 'Love it' },
  { emoji: '🤔', label: 'Made me think' },
  { emoji: '👎', label: 'Not helpful' },
]

interface FeedbackButtonsProps {
  sessionId: string
  messageIndex: number
  existingFeedback?: string | null
  onFeedbackGiven?: (index: number, emoji: string) => void
}

export default function FeedbackButtons({
  sessionId,
  messageIndex,
  existingFeedback,
  onFeedbackGiven,
}: FeedbackButtonsProps) {
  const [selected, setSelected] = useState<string | null>(existingFeedback || null)
  const [saving, setSaving] = useState(false)

  const handleFeedback = async (emoji: string) => {
    if (saving) return

    const newSelection = selected === emoji ? null : emoji
    setSelected(newSelection)

    if (!newSelection) return

    setSaving(true)
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          feedbackEmoji: emoji,
          messageIndex,
        }),
      })
      onFeedbackGiven?.(messageIndex, emoji)
    } catch (error) {
      console.error('Failed to save feedback:', error)
      setSelected(existingFeedback || null)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="flex gap-1 mt-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
      {FEEDBACK_EMOJIS.map(({ emoji, label }) => (
        <button
          key={emoji}
          onClick={() => handleFeedback(emoji)}
          disabled={saving}
          title={label}
          className={cn(
            'p-1 rounded text-sm transition-all hover:scale-110',
            selected === emoji
              ? 'bg-primary/10 scale-110'
              : 'hover:bg-gray-100'
          )}
        >
          {emoji}
        </button>
      ))}
    </div>
  )
}
