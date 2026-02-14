'use client'

import { useState } from 'react'
import type { AssessmentResponses } from '@/types'

interface QuestionnaireFormProps {
  onSubmit: (responses: AssessmentResponses, includeChatHistory: boolean) => void
  isSubmitting?: boolean
}

type FrequencyOption = 'not_at_all' | 'several_days' | 'more_than_half' | 'nearly_every_day'
type SleepOption = 'very_good' | 'good' | 'fair' | 'poor' | 'very_poor'
type SupportOption = 'strong' | 'moderate' | 'limited' | 'none'

const frequencyOptions: { value: FrequencyOption; label: string }[] = [
  { value: 'not_at_all', label: 'Not at all' },
  { value: 'several_days', label: 'Several days' },
  { value: 'more_than_half', label: 'More than half the days' },
  { value: 'nearly_every_day', label: 'Nearly every day' },
]

const sleepOptions: { value: SleepOption; label: string }[] = [
  { value: 'very_good', label: 'Very good' },
  { value: 'good', label: 'Good' },
  { value: 'fair', label: 'Fair' },
  { value: 'poor', label: 'Poor' },
  { value: 'very_poor', label: 'Very poor' },
]

const supportOptions: { value: SupportOption; label: string }[] = [
  { value: 'strong', label: 'Strong support network' },
  { value: 'moderate', label: 'Moderate support' },
  { value: 'limited', label: 'Limited support' },
  { value: 'none', label: 'Little to no support' },
]

export default function QuestionnaireForm({ onSubmit, isSubmitting }: QuestionnaireFormProps) {
  const [mood, setMood] = useState<FrequencyOption | ''>('')
  const [interest, setInterest] = useState<FrequencyOption | ''>('')
  const [anxiety, setAnxiety] = useState<FrequencyOption | ''>('')
  const [worry, setWorry] = useState<FrequencyOption | ''>('')
  const [sleep, setSleep] = useState<SleepOption | ''>('')
  const [support, setSupport] = useState<SupportOption | ''>('')
  const [coping, setCoping] = useState('')
  const [includeChatHistory, setIncludeChatHistory] = useState(false)

  const isComplete = mood && interest && anxiety && worry && sleep && support

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!isComplete || isSubmitting) return

    onSubmit(
      {
        mood,
        interest,
        anxiety,
        worry,
        sleep,
        support,
        coping: coping.trim(),
      },
      includeChatHistory
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* PHQ-2 Depression Screening + GAD-2 Anxiety Screening questions */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <p className="text-sm text-gray-500 mb-6">Over the last 2 weeks, how often have you been bothered by:</p>

        <div className="space-y-6">
          {/* PHQ-2: Depression screening */}
          <QuestionBlock
            question="Feeling down, depressed, or hopeless?"
            value={mood}
            onChange={(v) => setMood(v as FrequencyOption)}
            options={frequencyOptions}
            name="mood"
          />
          <QuestionBlock
            question="Little interest or pleasure in doing things?"
            value={interest}
            onChange={(v) => setInterest(v as FrequencyOption)}
            options={frequencyOptions}
            name="interest"
          />
          {/* GAD-2: Anxiety screening */}
          <QuestionBlock
            question="Feeling nervous, anxious, or on edge?"
            value={anxiety}
            onChange={(v) => setAnxiety(v as FrequencyOption)}
            options={frequencyOptions}
            name="anxiety"
          />
          <QuestionBlock
            question="Not being able to stop or control worrying?"
            value={worry}
            onChange={(v) => setWorry(v as FrequencyOption)}
            options={frequencyOptions}
            name="worry"
          />
        </div>
      </div>

      {/* Additional factors: sleep, support, coping */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div className="space-y-6">
          <QuestionBlock
            question="How would you rate your sleep quality?"
            value={sleep}
            onChange={(v) => setSleep(v as SleepOption)}
            options={sleepOptions}
            name="sleep"
          />
          <QuestionBlock
            question="How would you describe your social support system?"
            value={support}
            onChange={(v) => setSupport(v as SupportOption)}
            options={supportOptions}
            name="support"
          />

          <div>
            <label className="block text-gray-700 font-medium mb-3">
              What coping strategies do you currently use? (optional)
            </label>
            <textarea
              value={coping}
              onChange={(e) => setCoping(e.target.value)}
              placeholder="e.g., exercise, meditation, talking to friends, journaling..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
              rows={3}
            />
          </div>
        </div>
      </div>

      {/* Options */}
      <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={includeChatHistory}
            onChange={(e) => setIncludeChatHistory(e.target.checked)}
            className="mt-1 w-5 h-5 text-primary border-gray-300 rounded focus:ring-primary"
          />
          <div>
            <span className="font-medium text-secondary">Include chat history for context</span>
            <p className="text-sm text-gray-600 mt-1">
              This allows Animoa to provide more personalized recommendations based on your recent conversations.
            </p>
          </div>
        </label>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={!isComplete || isSubmitting}
        className="w-full py-4 bg-primary text-white rounded-xl font-semibold hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-lg"
      >
        {isSubmitting ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Generating Recommendations...
          </span>
        ) : (
          'Get Personalized Recommendations'
        )}
      </button>

      {/* Disclaimer */}
      <p className="text-sm text-gray-500 text-center">
        This assessment is for informational purposes only and is not a substitute for professional medical advice.
      </p>
    </form>
  )
}

// Reusable question block component
interface QuestionBlockProps {
  question: string
  value: string
  onChange: (value: string) => void
  options: { value: string; label: string }[]
  name: string
}

function QuestionBlock({ question, value, onChange, options, name }: QuestionBlockProps) {
  return (
    <div>
      <p className="text-gray-700 font-medium mb-3">{question}</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {options.map((option) => (
          <label
            key={option.value}
            className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
              value === option.value
                ? 'border-primary bg-primary/5 text-primary'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <input
              type="radio"
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={(e) => onChange(e.target.value)}
              className="w-4 h-4 text-primary focus:ring-primary"
            />
            <span className="text-sm">{option.label}</span>
          </label>
        ))}
      </div>
    </div>
  )
}
