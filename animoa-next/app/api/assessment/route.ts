import { NextRequest, NextResponse } from 'next/server'
import { createGroqClient, GROQ_MODEL } from '@/lib/groq'
import { createClient } from '@/lib/supabase/server'
import type { AssessmentResponses } from '@/types'

// GET /api/assessment - List all assessments for the current user
export async function GET() {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { data: assessments, error } = await supabase
      .from('questionnaire_responses')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching assessments:', error)
      return NextResponse.json({ error: 'Failed to fetch assessments' }, { status: 500 })
    }

    return NextResponse.json({ assessments: assessments || [] })
  } catch (error) {
    console.error('Assessment API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// POST /api/assessment - Create a new assessment and generate recommendations
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { responses, includeChatHistory } = await request.json() as {
      responses: AssessmentResponses
      includeChatHistory?: boolean
    }

    if (!responses) {
      return NextResponse.json({ error: 'Responses are required' }, { status: 400 })
    }

    // Get user profile for personalization
    const { data: profile } = await supabase
      .from('profiles')
      .select('full_name, age, stress_level, goals, interests')
      .eq('id', user.id)
      .single()

    // Optionally get recent chat history for context
    let chatContext = ''
    if (includeChatHistory) {
      const { data: recentChats } = await supabase
        .from('chat_history')
        .select('message, sender')
        .eq('user_id', user.id)
        .in('sender', ['user', 'bot'])
        .order('timestamp', { ascending: false })
        .limit(20)

      if (recentChats && recentChats.length > 0) {
        const conversations = recentChats.reverse().map(msg =>
          `${msg.sender === 'user' ? 'User' : 'Animoa'}: ${msg.message}`
        ).join('\n')
        chatContext = `\n\nRecent conversation context:\n${conversations}`
      }
    }

    // Generate recommendations using Groq
    const recommendations = await generateRecommendations(responses, profile, chatContext)

    // Save assessment to database
    const { data: assessment, error } = await supabase
      .from('questionnaire_responses')
      .insert({
        user_id: user.id,
        responses,
        recommendations,
        used_chat_history: includeChatHistory || false,
      })
      .select()
      .single()

    if (error) {
      console.error('Error saving assessment:', error)
      return NextResponse.json({ error: 'Failed to save assessment' }, { status: 500 })
    }

    return NextResponse.json({ assessment })
  } catch (error) {
    console.error('Assessment creation error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// Helper function to generate personalized recommendations
async function generateRecommendations(
  responses: AssessmentResponses,
  profile: { full_name?: string; age?: number; stress_level?: string; goals?: string; interests?: string } | null,
  chatContext: string
): Promise<string> {
  const groq = createGroqClient()

  const systemPrompt = `You are a compassionate mental wellness advisor. Based on the user's assessment responses,
provide personalized, actionable recommendations. Be warm, supportive, and practical.

Structure your response as follows:
1. **Overall Assessment**: Brief summary of their current state (2-3 sentences)
2. **Key Insights**: What patterns or areas need attention (2-3 bullet points)
3. **Personalized Recommendations**: Specific, actionable suggestions (3-5 items)
4. **Daily Practices**: Simple activities they can start today (2-3 items)
5. **Encouragement**: A supportive closing message

Keep the tone conversational and hopeful. Avoid clinical language.
Remember: This is supportive guidance, not a medical diagnosis.`

  const responseLabels: Record<string, Record<string, string>> = {
    mood: {
      'not_at_all': 'Not at all',
      'several_days': 'Several days',
      'more_than_half': 'More than half the days',
      'nearly_every_day': 'Nearly every day'
    },
    interest: {
      'not_at_all': 'Not at all',
      'several_days': 'Several days',
      'more_than_half': 'More than half the days',
      'nearly_every_day': 'Nearly every day'
    },
    anxiety: {
      'not_at_all': 'Not at all',
      'several_days': 'Several days',
      'more_than_half': 'More than half the days',
      'nearly_every_day': 'Nearly every day'
    },
    worry: {
      'not_at_all': 'Not at all',
      'several_days': 'Several days',
      'more_than_half': 'More than half the days',
      'nearly_every_day': 'Nearly every day'
    },
    sleep: {
      'very_good': 'Very good',
      'good': 'Good',
      'fair': 'Fair',
      'poor': 'Poor',
      'very_poor': 'Very poor'
    },
    support: {
      'strong': 'Strong support network',
      'moderate': 'Moderate support',
      'limited': 'Limited support',
      'none': 'Little to no support'
    }
  }

  const userPrompt = `Please analyze these assessment responses and provide personalized wellness recommendations:

**PHQ-2 (Depression Screening)**
- Feeling down, depressed, or hopeless: ${responseLabels.mood[responses.mood] || responses.mood}
- Little interest or pleasure in doing things: ${responseLabels.interest[responses.interest] || responses.interest}

**GAD-2 (Anxiety Screening)**
- Feeling nervous, anxious, or on edge: ${responseLabels.anxiety[responses.anxiety] || responses.anxiety}
- Not being able to stop or control worrying: ${responseLabels.worry[responses.worry] || responses.worry}

**Additional Factors**
- Sleep quality: ${responseLabels.sleep[responses.sleep] || responses.sleep}
- Social support: ${responseLabels.support[responses.support] || responses.support}
- Current coping strategies: ${responses.coping || 'Not specified'}

${profile ? `
**User Profile**
${profile.full_name ? `- Name: ${profile.full_name}` : ''}
${profile.age ? `- Age: ${profile.age}` : ''}
${profile.stress_level ? `- Self-reported stress level: ${profile.stress_level}` : ''}
${profile.goals ? `- Wellness goals: ${profile.goals}` : ''}
${profile.interests ? `- Interests: ${profile.interests}` : ''}
` : ''}
${chatContext}`

  try {
    const completion = await groq.chat.completions.create({
      model: GROQ_MODEL,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.7,
      max_tokens: 1000,
    })

    return completion.choices[0]?.message?.content || 'Unable to generate recommendations at this time.'
  } catch (error) {
    console.error('Groq API error:', error)
    return 'Unable to generate recommendations at this time. Please try again later.'
  }
}
