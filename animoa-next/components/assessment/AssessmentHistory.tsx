'use client'

import { useState } from 'react'
import { formatDateTime } from '@/lib/utils'
import type { Assessment } from '@/types'

interface AssessmentHistoryProps {
  assessments: Assessment[]
  onDelete: (id: string) => void
  onView: (assessment: Assessment) => void
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
    strong: 'Strong support',
    moderate: 'Moderate support',
    limited: 'Limited support',
    none: 'No support',
  },
}

export default function AssessmentHistory({ assessments, onDelete, onView }: AssessmentHistoryProps) {
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)

  const handleDelete = (id: string) => {
    onDelete(id)
    setDeleteConfirm(null)
  }

  const getScoreSummary = (responses: Assessment['responses']) => {
    const frequencyScore: Record<string, number> = {
      not_at_all: 0,
      several_days: 1,
      more_than_half: 2,
      nearly_every_day: 3,
    }

    const phq2 = (frequencyScore[responses.mood] || 0) + (frequencyScore[responses.interest] || 0)
    const gad2 = (frequencyScore[responses.anxiety] || 0) + (frequencyScore[responses.worry] || 0)

    return { phq2, gad2 }
  }

  const getScoreColor = (score: number) => {
    if (score <= 1) return 'text-green-600 bg-green-50'
    if (score <= 3) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  if (assessments.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📋</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No assessments yet</h3>
        <p className="text-gray-500">Complete your first wellness assessment to see your history here.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {assessments.map((assessment) => {
        const { phq2, gad2 } = getScoreSummary(assessment.responses)
        const isDeleting = deleteConfirm === assessment.id

        return (
          <div
            key={assessment.id}
            className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:border-gray-200 transition-colors"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-sm text-gray-500">
                    {formatDateTime(assessment.created_at)}
                  </span>
                  {assessment.used_chat_history && (
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                      Includes chat context
                    </span>
                  )}
                </div>

                <div className="flex gap-4 mb-3">
                  {/* PHQ-2 depression score */}
                  <div className={`px-3 py-1.5 rounded-lg text-sm font-medium ${getScoreColor(phq2)}`}>
                    Mood: {phq2}/6
                  </div>
                  {/* GAD-2 anxiety score */}
                  <div className={`px-3 py-1.5 rounded-lg text-sm font-medium ${getScoreColor(gad2)}`}>
                    Anxiety: {gad2}/6
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                  <div>Sleep: {responseLabels.sleep[assessment.responses.sleep]}</div>
                  <div>Support: {responseLabels.support[assessment.responses.support]}</div>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => onView(assessment)}
                  className="px-4 py-2 text-primary border border-primary rounded-lg hover:bg-primary/5 transition-colors text-sm font-medium"
                >
                  View Details
                </button>
                {isDeleting ? (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDelete(assessment.id)}
                      className="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
                    >
                      Confirm
                    </button>
                    <button
                      onClick={() => setDeleteConfirm(null)}
                      className="px-3 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setDeleteConfirm(assessment.id)}
                    className="px-3 py-2 text-gray-400 hover:text-red-500 transition-colors"
                    title="Delete assessment"
                  >
                    🗑️
                  </button>
                )}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
