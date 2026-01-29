'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { useParams } from 'next/navigation'
import { detectCrisis } from '@/lib/crisis-detection'
import CrisisAlert from '@/components/crisis/CrisisAlert'
import MessageBubble from '@/components/chat/MessageBubble'
import ChatInput from '@/components/chat/ChatInput'
import type { Message, ChatMessage } from '@/types'

export default function ChatSessionPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [messages, setMessages] = useState<Message[]>([])
  const [feedbackMap, setFeedbackMap] = useState<Record<number, string>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)
  const [showCrisisAlert, setShowCrisisAlert] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load message history for this session
  const loadMessages = useCallback(async () => {
    setIsLoadingHistory(true)
    try {
      const res = await fetch(`/api/sessions/${sessionId}/messages`)
      const data = await res.json()
      const chatMessages: ChatMessage[] = data.messages || []

      // Separate actual messages and feedback entries
      const msgList: Message[] = []
      const fbMap: Record<number, string> = {}

      for (const msg of chatMessages) {
        if (msg.sender === 'feedback') {
          if (msg.feedback_for_message_index !== undefined) {
            fbMap[msg.feedback_for_message_index] = msg.message
          }
        } else {
          msgList.push({
            role: msg.sender === 'user' ? 'user' : 'assistant',
            content: msg.message,
          })
        }
      }

      setMessages(msgList)
      setFeedbackMap(fbMap)
    } catch (error) {
      console.error('Failed to load messages:', error)
    } finally {
      setIsLoadingHistory(false)
    }
  }, [sessionId])

  useEffect(() => {
    loadMessages()
  }, [loadMessages])

  const handleSend = async (userMessage: string) => {
    if (isLoading) return

    // Check for crisis keywords
    if (detectCrisis(userMessage)) {
      setShowCrisisAlert(true)
    }

    // Add user message to UI immediately
    const updatedMessages = [...messages, { role: 'user' as const, content: userMessage }]
    setMessages(updatedMessages)
    setIsLoading(true)

    try {
      // Send to streaming API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          sessionId,
          conversationHistory: messages,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      // Read the stream
      const reader = response.body?.getReader()
      if (!reader) throw new Error('No reader available')

      const decoder = new TextDecoder()
      let assistantContent = ''

      // Add empty assistant message that we'll stream into
      setMessages((prev) => [...prev, { role: 'assistant', content: '' }])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value)
        const lines = text.split('\n\n').filter(Boolean)

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const jsonStr = line.replace('data: ', '')

          try {
            const parsed = JSON.parse(jsonStr)

            if (parsed.done) {
              break
            }
            if (parsed.error) {
              console.error('Stream error:', parsed.error)
              break
            }
            if (parsed.content) {
              assistantContent += parsed.content
              // Update the last message (assistant) with streamed content
              setMessages((prev) => {
                const updated = [...prev]
                updated[updated.length - 1] = {
                  role: 'assistant',
                  content: assistantContent,
                }
                return updated
              })
            }
          } catch {
            // Skip malformed JSON chunks
          }
        }
      }

      // If we got no response, show a fallback
      if (!assistantContent) {
        setMessages((prev) => {
          const updated = [...prev]
          updated[updated.length - 1] = {
            role: 'assistant',
            content: "I'm having trouble responding right now. Please try again.",
          }
          return updated
        })
      }
    } catch (error) {
      console.error('Chat error:', error)
      setMessages((prev) => [
        ...prev.slice(0, -1), // Remove empty assistant message if it exists
        {
          role: 'assistant',
          content: "I'm having trouble responding right now. Please try again.",
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleFeedbackGiven = (index: number, emoji: string) => {
    setFeedbackMap((prev) => ({ ...prev, [index]: emoji }))
  }

  if (isLoadingHistory) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-gray-400 text-sm">Loading conversation...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 shrink-0">
        <h1 className="text-lg font-semibold text-secondary">Chat with Animoa</h1>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-20">
            <div className="text-5xl mb-4">🧠</div>
            <h2 className="text-xl font-semibold mb-2">Hi there!</h2>
            <p className="max-w-sm mx-auto">
              I'm Animoa, your wellness companion. How are you feeling today?
            </p>
          </div>
        ) : (
          messages.map((message, i) => (
            <MessageBubble
              key={i}
              content={message.content}
              role={message.role}
              index={i}
              sessionId={sessionId}
              existingFeedback={feedbackMap[i] || null}
              onFeedbackGiven={handleFeedbackGiven}
            />
          ))
        )}

        {/* Typing indicator */}
        {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-md">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <ChatInput onSend={handleSend} disabled={isLoading} />

      {/* Crisis Alert Modal */}
      <CrisisAlert
        isVisible={showCrisisAlert}
        onDismiss={() => setShowCrisisAlert(false)}
      />
    </div>
  )
}
