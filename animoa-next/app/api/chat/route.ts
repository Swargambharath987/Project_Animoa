import { NextRequest, NextResponse } from 'next/server'
import { createGroqClient, GROQ_MODEL, getSystemPrompt } from '@/lib/groq'
import { createClient } from '@/lib/supabase/server'
import type { Message } from '@/types'

export async function POST(request: NextRequest) {
  try {
    const { message, conversationHistory } = await request.json()

    if (!message) {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 })
    }

    // Get user profile for personalization
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    let profile = null
    if (user) {
      const { data } = await supabase
        .table('profiles')
        .select('full_name, stress_level, goals, interests')
        .eq('id', user.id)
        .single()
      profile = data
    }

    // Create Groq client and generate response
    const groq = createGroqClient()

    const messages = [
      { role: 'system' as const, content: getSystemPrompt(profile) },
      ...((conversationHistory || []) as Message[]).map((msg: Message) => ({
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
      })),
      { role: 'user' as const, content: message },
    ]

    const completion = await groq.chat.completions.create({
      model: GROQ_MODEL,
      messages,
      temperature: 0.7,
    })

    const response = completion.choices[0]?.message?.content || 'I apologize, I could not generate a response.'

    return NextResponse.json({ response })
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Failed to generate response' },
      { status: 500 }
    )
  }
}
