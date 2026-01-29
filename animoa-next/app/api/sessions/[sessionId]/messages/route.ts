import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// GET /api/sessions/[sessionId]/messages - Load messages for a session
export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { sessionId } = params

    const { data: messages, error } = await supabase
      .from('chat_history')
      .select('*')
      .eq('session_id', sessionId)
      .eq('user_id', user.id)
      .order('timestamp', { ascending: true })

    if (error) {
      console.error('Error fetching messages:', error)
      return NextResponse.json({ error: 'Failed to fetch messages' }, { status: 500 })
    }

    return NextResponse.json({ messages: messages || [] })
  } catch (error) {
    console.error('Messages API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// POST /api/sessions/[sessionId]/messages - Save a message to a session
export async function POST(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { sessionId } = params
    const { message, sender } = await request.json()

    const { data, error } = await supabase
      .from('chat_history')
      .insert({
        user_id: user.id,
        session_id: sessionId,
        message,
        sender,
      })
      .select()
      .single()

    if (error) {
      console.error('Error saving message:', error)
      return NextResponse.json({ error: 'Failed to save message' }, { status: 500 })
    }

    return NextResponse.json({ message: data })
  } catch (error) {
    console.error('Save message error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
