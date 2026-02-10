'use client'

import { useState } from 'react'
import { formatDateTime } from '@/lib/utils'
import type { Assessment } from '@/types'

interface AssessmentDetailProps {
  assessment: Assessment
  onBack: () => void
}

const responseLabels: Record<string, Record<string, string>> = {
  mood: {
    not_at_all: 'Not at all',
    several_days: 'Several days',
    more_than_half: 'More than half the days',
    nearly_every_day: 'Nearly every day',
  },
  interest: {
    not_at_all: 'Not at all',
    several_days: 'Several days',
    more_than_half: 'More than half the days',
    nearly_every_day: 'Nearly every day',
  },
  anxiety: {
    not_at_all: 'Not at all',
    several_days: 'Several days',
    more_than_half: 'More than half the days',
    nearly_every_day: 'Nearly every day',
  },
  worry: {
    not_at_all: 'Not at all',
    several_days: 'Several days',
    more_than_half: 'More than half the days',
    nearly_every_day: 'Nearly every day',
  },
  sleep: {
    very_good: 'Very good',
    good: 'Good',
    fair: 'Fair',
    poor: 'Poor',
    very_poor: 'Very poor',
  },
  support: {
    strong: 'Strong support network',
    moderate: 'Moderate support',
    limited: 'Limited support',
    none: 'Little to no support',
  },
}

export default function AssessmentDetail({ assessment, onBack }: AssessmentDetailProps) {
  const [isDownloading, setIsDownloading] = useState(false)
  const { responses, recommendations, created_at, used_chat_history } = assessment

  const handleDownloadPDF = async () => {
    setIsDownloading(true)
    try {
      const response = await fetch('/api/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ assessmentId: assessment.id }),
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `animoa-wellness-report-${assessment.id.slice(0, 8)}.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('PDF download error:', error)
    } finally {
      setIsDownloading(false)
    }
  }

  const frequencyScore: Record<string, number> = {
    not_at_all: 0,
    several_days: 1,
    more_than_half: 2,
    nearly_every_day: 3,
  }

  const phq2 = (frequencyScore[responses.mood] || 0) + (frequencyScore[responses.interest] || 0)
  const gad2 = (frequencyScore[responses.anxiety] || 0) + (frequencyScore[responses.worry] || 0)

  const getScoreInterpretation = (score: number, type: 'phq' | 'gad') => {
    if (score <= 1) return { text: 'Minimal symptoms', color: 'text-green-600' }
    if (score <= 3) return { text: 'Mild symptoms', color: 'text-yellow-600' }
    return { text: 'Consider further evaluation', color: 'text-red-600' }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            ← Back
          </button>
          <div>
            <h2 className="text-xl font-semibold text-secondary">Assessment Details</h2>
            <p className="text-sm text-gray-500">
              {formatDateTime(created_at)}
              {used_chat_history && ' • Includes chat context'}
            </p>
          </div>
        </div>
        <button
          onClick={handleDownloadPDF}
          disabled={isDownloading}
          className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 transition-colors text-sm font-medium flex items-center gap-2"
        >
          {isDownloading ? (
            <>
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Generating...
            </>
          ) : (
            'Download PDF'
          )}
        </button>
      </div>

      {/* Scores Summary */}
      <div className="grid grid-cols-2 gap-4">
        {/* PHQ-2 depression score */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Mood Score</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-secondary">{phq2}</span>
            <span className="text-gray-400">/ 6</span>
          </div>
          <p className={`text-sm mt-1 ${getScoreInterpretation(phq2, 'phq').color}`}>
            {getScoreInterpretation(phq2, 'phq').text}
          </p>
        </div>
        {/* GAD-2 anxiety score */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Anxiety Score</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-secondary">{gad2}</span>
            <span className="text-gray-400">/ 6</span>
          </div>
          <p className={`text-sm mt-1 ${getScoreInterpretation(gad2, 'gad').color}`}>
            {getScoreInterpretation(gad2, 'gad').text}
          </p>
        </div>
      </div>

      {/* Responses */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold text-secondary mb-4">Your Responses</h3>
        <div className="space-y-4">
          <ResponseRow
            label="Feeling down, depressed, or hopeless"
            value={responseLabels.mood[responses.mood]}
          />
          <ResponseRow
            label="Little interest or pleasure in doing things"
            value={responseLabels.interest[responses.interest]}
          />
          <ResponseRow
            label="Feeling nervous, anxious, or on edge"
            value={responseLabels.anxiety[responses.anxiety]}
          />
          <ResponseRow
            label="Not being able to stop or control worrying"
            value={responseLabels.worry[responses.worry]}
          />
          <ResponseRow
            label="Sleep quality"
            value={responseLabels.sleep[responses.sleep]}
          />
          <ResponseRow
            label="Social support"
            value={responseLabels.support[responses.support]}
          />
          {responses.coping && (
            <ResponseRow label="Coping strategies" value={responses.coping} />
          )}
        </div>
      </div>

      {/* Recommendations */}
      {recommendations && (
        <div className="bg-gradient-to-br from-primary/5 to-blue-50 rounded-xl p-6 shadow-sm border border-primary/10">
          <h3 className="text-lg font-semibold text-secondary mb-4 flex items-center gap-2">
            <span>✨</span> Personalized Recommendations
          </h3>
          <div className="prose prose-sm max-w-none text-gray-700">
            {recommendations.split('\n').map((line, i) => {
              if (line.startsWith('**') && line.endsWith('**')) {
                return (
                  <h4 key={i} className="font-semibold text-secondary mt-4 mb-2">
                    {line.replace(/\*\*/g, '')}
                  </h4>
                )
              }
              if (line.startsWith('- ') || line.startsWith('• ')) {
                return (
                  <p key={i} className="ml-4 mb-1">
                    • {line.replace(/^[-•]\s*/, '')}
                  </p>
                )
              }
              if (line.match(/^\d+\.\s/)) {
                return (
                  <p key={i} className="ml-4 mb-1">
                    {line}
                  </p>
                )
              }
              if (line.trim()) {
                return (
                  <p key={i} className="mb-2">
                    {line}
                  </p>
                )
              }
              return null
            })}
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <p className="text-sm text-gray-500 text-center">
        This assessment is for informational purposes only and is not a substitute for professional medical advice.
        If you're experiencing severe symptoms, please seek help from a mental health professional.
      </p>
    </div>
  )
}

function ResponseRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-start gap-4 py-2 border-b border-gray-100 last:border-0">
      <span className="text-gray-600">{label}</span>
      <span className="text-secondary font-medium text-right">{value}</span>
    </div>
  )
}
