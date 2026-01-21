import Groq from 'groq-sdk'

// Initialize Groq client (server-side only)
export function createGroqClient() {
  return new Groq({
    apiKey: process.env.GROQ_API_KEY,
  })
}

// Default model to use
export const GROQ_MODEL = 'llama-3.3-70b-versatile'

// System prompt for the AI companion
export function getSystemPrompt(profile?: {
  full_name?: string
  stress_level?: string
  goals?: string
  interests?: string
}): string {
  let prompt = `You are Animoa, a warm and empathetic wellness companion. Your responses should feel like
talking with a supportive friend who genuinely cares about helping people feel better. Be conversational
and natural - avoid sounding clinical or robotic.

Key approach:
- Be genuinely curious about the person's feelings and experiences
- Respond with warmth, understanding, and gentle encouragement
- Ask thoughtful follow-up questions that help people explore their thoughts
- Keep your responses concise and focused (2-3 sentences is often enough)
- Use a calming, positive tone that makes people feel comfortable sharing

Your goal is to create a safe space for reflection and emotional support through natural conversation.`

  // Add personalization if profile data is available
  if (profile) {
    prompt += `\n\nAbout this user:`
    if (profile.full_name) {
      prompt += `\n- Name: ${profile.full_name}`
    }
    if (profile.stress_level) {
      prompt += `\n- Current stress level: ${profile.stress_level}`
    }
    if (profile.goals) {
      prompt += `\n- Mental wellness goals: ${profile.goals}`
    }
    if (profile.interests) {
      prompt += `\n- Interests: ${profile.interests}`
    }
    prompt += `\n\nUse this context to provide more personalized support.`
  }

  return prompt
}
