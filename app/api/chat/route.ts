import { NextRequest, NextResponse } from 'next/server'
import { createGroqClient, GROQ_MODEL, getSystemPromptWithRAG } from '@/lib/groq'
import { createClient } from '@/lib/supabase/server'
import { retrieveKnowledge, formatKnowledgeContext } from '@/lib/rag'
import type { Message } from '@/types'

export async function POST(request: NextRequest) {
  try {
    const { message, sessionId, conversationHistory } = await request.json()

    if (!message) {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 })
    }

    // Get user and profile for personalization
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    let profile = null
    const { data } = await supabase
      .from('profiles')
      .select('full_name, stress_level, goals, interests')
      .eq('id', user.id)
      .single()
    profile = data

    // Save user message to Supabase
    if (sessionId) {
      await supabase.from('chat_history').insert({
        user_id: user.id,
        session_id: sessionId,
        message,
        sender: 'user',
      })
    }

    // RAG: Retrieve relevant knowledge based on user's message
    const knowledgeResults = await retrieveKnowledge(message, {
      matchCount: 3,
      similarityThreshold: 0.45,
    })
    const knowledgeContext = formatKnowledgeContext(knowledgeResults)

    // Build messages array for Groq with RAG-enhanced system prompt
    const groqMessages = [
      { role: 'system' as const, content: getSystemPromptWithRAG(profile ?? undefined, knowledgeContext || undefined) },
      ...((conversationHistory || []) as Message[]).map((msg: Message) => ({
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
      })),
      { role: 'user' as const, content: message },
    ]

    // Create Groq client with streaming
    const groq = createGroqClient()

    const stream = await groq.chat.completions.create({
      model: GROQ_MODEL,
      messages: groqMessages,
      temperature: 0.7,
      max_tokens: 500,
      stream: true,
    })

    // Create a ReadableStream that sends chunks to the client
    const encoder = new TextEncoder()
    let fullResponse = ''

    const readable = new ReadableStream({
      async start(controller) {
        try {
          for await (const chunk of stream) {
            const content = chunk.choices[0]?.delta?.content || ''
            if (content) {
              fullResponse += content
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({ content })}\n\n`))
            }
          }

          // Save the complete bot response to Supabase
          if (sessionId && fullResponse) {
            await supabase.from('chat_history').insert({
              user_id: user.id,
              session_id: sessionId,
              message: fullResponse,
              sender: 'bot',
            })

            // Auto-update session title from first user message
            const { data: messages } = await supabase
              .from('chat_history')
              .select('id')
              .eq('session_id', sessionId)
              .eq('sender', 'user')

            if (messages && messages.length === 1) {
              // This is the first message - update session title
              const title = message.length > 40
                ? message.substring(0, 40) + '...'
                : message
              await supabase
                .from('chat_sessions')
                .update({ title })
                .eq('id', sessionId)
            }
          }

          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ done: true })}\n\n`))
          controller.close()
        } catch (error) {
          console.error('Streaming error:', error)
          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify({ error: 'Streaming failed' })}\n\n`)
          )
          controller.close()
        }
      },
    })

    return new Response(readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    })
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Failed to generate response' },
      { status: 500 }
    )
  }
}
