// User Profile
export interface Profile {
  id: string
  email: string
  full_name?: string
  age?: number
  stress_level?: 'Low' | 'Moderate' | 'High' | 'Very High'
  goals?: string
  interests?: string
  created_at?: string
}

// Chat Types
export interface Message {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatSession {
  id: string
  user_id: string
  title: string
  created_at: string
}

export interface ChatMessage {
  id: string
  user_id: string
  session_id: string
  message: string
  sender: 'user' | 'bot' | 'feedback'
  feedback_for_message_index?: number
  timestamp: string
}

// Mood Types
export type MoodType = 'very_happy' | 'happy' | 'neutral' | 'sad' | 'very_sad'

export interface MoodEntry {
  id: string
  user_id: string
  date: string
  mood: MoodType
  note?: string
  created_at: string
}

export interface MoodConfig {
  emoji: string
  label: string
  value: number
  color: string
  message: string
}

// Assessment Types
export interface AssessmentResponses {
  mood: string
  interest: string
  anxiety: string
  worry: string
  sleep: string
  support: string
  coping: string
}

export interface Assessment {
  id: string
  user_id: string
  responses: AssessmentResponses
  recommendations?: string
  used_chat_history: boolean
  created_at: string
}

// Crisis Detection
export interface CrisisResources {
  title: string
  message: string
}
