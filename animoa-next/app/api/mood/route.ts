import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import type { MoodType } from '@/types'

// GET /api/mood - Get mood entries for a date range
export async function GET(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const startDate = searchParams.get('start')
    const endDate = searchParams.get('end')

    let query = supabase
      .from('mood_logs')
      .select('*')
      .eq('user_id', user.id)
      .order('date', { ascending: false })

    if (startDate) {
      query = query.gte('date', startDate)
    }
    if (endDate) {
      query = query.lte('date', endDate)
    }

    const { data: moods, error } = await query

    if (error) {
      console.error('Error fetching moods:', error)
      return NextResponse.json({ error: 'Failed to fetch moods' }, { status: 500 })
    }

    return NextResponse.json({ moods: moods || [] })
  } catch (error) {
    console.error('Mood API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// POST /api/mood - Create or update a mood entry
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { date, mood, note } = await request.json() as {
      date: string
      mood: MoodType
      note?: string
    }

    if (!date || !mood) {
      return NextResponse.json({ error: 'Date and mood are required' }, { status: 400 })
    }

    // Validate mood type
    const validMoods: MoodType[] = ['very_happy', 'happy', 'neutral', 'sad', 'very_sad']
    if (!validMoods.includes(mood)) {
      return NextResponse.json({ error: 'Invalid mood type' }, { status: 400 })
    }

    // Check if entry exists for this date
    const { data: existing } = await supabase
      .from('mood_logs')
      .select('id')
      .eq('user_id', user.id)
      .eq('date', date)
      .single()

    let result
    if (existing) {
      // Update existing entry
      const { data, error } = await supabase
        .from('mood_logs')
        .update({ mood, note })
        .eq('id', existing.id)
        .select()
        .single()

      if (error) {
        console.error('Error updating mood:', error)
        return NextResponse.json({ error: 'Failed to update mood' }, { status: 500 })
      }
      result = data
    } else {
      // Create new entry
      const { data, error } = await supabase
        .from('mood_logs')
        .insert({
          user_id: user.id,
          date,
          mood,
          note,
        })
        .select()
        .single()

      if (error) {
        console.error('Error creating mood:', error)
        return NextResponse.json({ error: 'Failed to create mood' }, { status: 500 })
      }
      result = data
    }

    return NextResponse.json({ mood: result })
  } catch (error) {
    console.error('Mood creation error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
