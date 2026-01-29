import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// POST /api/feedback - Save feedback for a bot message
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { sessionId, feedbackEmoji, messageIndex } = await request.json()

    if (!sessionId || !feedbackEmoji || messageIndex === undefined) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 })
    }

    // Check if feedback already exists for this message
    const { data: existing } = await supabase
      .from('chat_history')
      .select('id')
      .eq('session_id', sessionId)
      .eq('user_id', user.id)
      .eq('sender', 'feedback')
      .eq('feedback_for_message_index', messageIndex)
      .single()

    if (existing) {
      // Update existing feedback
      const { error } = await supabase
        .from('chat_history')
        .update({ message: feedbackEmoji })
        .eq('id', existing.id)

      if (error) {
        console.error('Error updating feedback:', error)
        return NextResponse.json({ error: 'Failed to update feedback' }, { status: 500 })
      }
    } else {
      // Insert new feedback
      const { error } = await supabase
        .from('chat_history')
        .insert({
          user_id: user.id,
          session_id: sessionId,
          message: feedbackEmoji,
          sender: 'feedback',
          feedback_for_message_index: messageIndex,
        })

      if (error) {
        console.error('Error saving feedback:', error)
        return NextResponse.json({ error: 'Failed to save feedback' }, { status: 500 })
      }
    }

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Feedback API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
