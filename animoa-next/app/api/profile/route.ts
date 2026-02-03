import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// GET /api/profile - Get current user's profile
export async function GET() {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { data: profile, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single()

    if (error) {
      console.error('Error fetching profile:', error)
      return NextResponse.json({ error: 'Failed to fetch profile' }, { status: 500 })
    }

    return NextResponse.json({ profile })
  } catch (error) {
    console.error('Profile API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// PUT /api/profile - Update current user's profile
export async function PUT(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const updates = await request.json() as {
      full_name?: string
      age?: number
      stress_level?: string
      goals?: string
      interests?: string
    }

    // Validate age if provided
    if (updates.age !== undefined && updates.age !== null) {
      if (typeof updates.age !== 'number' || updates.age < 13 || updates.age > 120) {
        return NextResponse.json({ error: 'Age must be between 13 and 120' }, { status: 400 })
      }
    }

    // Validate stress level if provided
    const validStressLevels = ['Low', 'Moderate', 'High', 'Very High']
    if (updates.stress_level && !validStressLevels.includes(updates.stress_level)) {
      return NextResponse.json({ error: 'Invalid stress level' }, { status: 400 })
    }

    // Only allow updating safe fields
    const safeUpdates: Record<string, unknown> = {}
    if (updates.full_name !== undefined) safeUpdates.full_name = updates.full_name
    if (updates.age !== undefined) safeUpdates.age = updates.age
    if (updates.stress_level !== undefined) safeUpdates.stress_level = updates.stress_level
    if (updates.goals !== undefined) safeUpdates.goals = updates.goals
    if (updates.interests !== undefined) safeUpdates.interests = updates.interests

    const { data: profile, error } = await supabase
      .from('profiles')
      .update(safeUpdates)
      .eq('id', user.id)
      .select()
      .single()

    if (error) {
      console.error('Error updating profile:', error)
      return NextResponse.json({ error: 'Failed to update profile' }, { status: 500 })
    }

    return NextResponse.json({ profile })
  } catch (error) {
    console.error('Profile update error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
