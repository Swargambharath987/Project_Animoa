'use client'

import FeedbackButtons from './FeedbackButtons'

interface MessageBubbleProps {
  content: string
  role: 'user' | 'assistant'
  index: number
  sessionId: string
  existingFeedback?: string | null
  onFeedbackGiven?: (index: number, emoji: string) => void
}

export default function MessageBubble({
  content,
  role,
  index,
  sessionId,
  existingFeedback,
  onFeedbackGiven,
}: MessageBubbleProps) {
  const isUser = role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[75%] ${isUser ? '' : 'group'}`}>
        {/* Avatar + Name */}
        <div className={`flex items-center gap-2 mb-1 ${isUser ? 'justify-end' : ''}`}>
          <span className="text-xs text-gray-400">
            {isUser ? 'You' : 'Animoa'}
          </span>
        </div>

        {/* Message Content */}
        <div
          className={`px-4 py-3 rounded-2xl whitespace-pre-wrap ${
            isUser
              ? 'bg-primary text-white rounded-br-md'
              : 'bg-gray-100 text-gray-800 rounded-bl-md'
          }`}
        >
          {content}
        </div>

        {/* Feedback Buttons (only for assistant messages) */}
        {!isUser && (
          <FeedbackButtons
            sessionId={sessionId}
            messageIndex={index}
            existingFeedback={existingFeedback}
            onFeedbackGiven={onFeedbackGiven}
          />
        )}
      </div>
    </div>
  )
}
