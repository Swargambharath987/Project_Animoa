'use client'

import { useState } from 'react'
import type { MoodType, MoodConfig } from '@/types'

interface MoodPickerProps {
  selectedMood?: MoodType
  note?: string
  onSave: (mood: MoodType, note: string) => void
  isSubmitting?: boolean
}

export const MOOD_CONFIG: Record<MoodType, MoodConfig> = {
  very_happy: {
    emoji: '😄',
    label: 'Great',
    value: 5,
    color: '#22c55e',
    message: "That's wonderful! Keep doing what makes you feel great!",
  },
  happy: {
    emoji: '🙂',
    label: 'Good',
    value: 4,
    color: '#84cc16',
    message: "Good to hear! Small joys add up to a happier life.",
  },
  neutral: {
    emoji: '😐',
    label: 'Okay',
    value: 3,
    color: '#eab308',
    message: "It's okay to have neutral days. They're part of the journey.",
  },
  sad: {
    emoji: '😔',
    label: 'Low',
    value: 2,
    color: '#f97316',
    message: "I'm sorry you're feeling low. Remember, it's okay to not be okay.",
  },
  very_sad: {
    emoji: '😢',
    label: 'Struggling',
    value: 1,
    color: '#ef4444',
    message: "I hear you. Reaching out for support can help. You're not alone.",
  },
}

const moodOrder: MoodType[] = ['very_happy', 'happy', 'neutral', 'sad', 'very_sad']

export default function MoodPicker({ selectedMood, note: initialNote, onSave, isSubmitting }: MoodPickerProps) {
  const [mood, setMood] = useState<MoodType | undefined>(selectedMood)
  const [note, setNote] = useState(initialNote || '')

  const handleSave = () => {
    if (!mood || isSubmitting) return
    onSave(mood, note.trim())
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold text-secondary mb-2">How are you feeling today?</h3>
      <p className="text-sm text-gray-500 mb-6">Select your current mood and optionally add a note.</p>

      {/* Mood buttons */}
      <div className="flex justify-center gap-3 mb-6">
        {moodOrder.map((moodType) => {
          const config = MOOD_CONFIG[moodType]
          const isSelected = mood === moodType

          return (
            <button
              key={moodType}
              onClick={() => setMood(moodType)}
              className={`flex flex-col items-center p-3 rounded-xl transition-all ${
                isSelected
                  ? 'bg-gray-100 ring-2 ring-offset-2 scale-110'
                  : 'hover:bg-gray-50 hover:scale-105'
              }`}
              style={{
                ringColor: isSelected ? config.color : undefined,
              }}
            >
              <span className="text-4xl mb-1">{config.emoji}</span>
              <span className={`text-xs font-medium ${isSelected ? 'text-secondary' : 'text-gray-500'}`}>
                {config.label}
              </span>
            </button>
          )
        })}
      </div>

      {/* Mood message */}
      {mood && (
        <div
          className="text-center p-3 rounded-lg mb-6 text-sm"
          style={{ backgroundColor: `${MOOD_CONFIG[mood].color}15`, color: MOOD_CONFIG[mood].color }}
        >
          {MOOD_CONFIG[mood].message}
        </div>
      )}

      {/* Journal note */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Journal note (optional)
        </label>
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="What's on your mind? Any thoughts, events, or reflections..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
          rows={3}
        />
      </div>

      {/* Save button */}
      <button
        onClick={handleSave}
        disabled={!mood || isSubmitting}
        className="w-full py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isSubmitting ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Saving...
          </span>
        ) : selectedMood ? (
          'Update Mood'
        ) : (
          'Save Mood'
        )}
      </button>
    </div>
  )
}
