'use client'

import { useState, useEffect, useCallback } from 'react'
import QuestionnaireForm from '@/components/assessment/QuestionnaireForm'
import AssessmentHistory from '@/components/assessment/AssessmentHistory'
import AssessmentDetail from '@/components/assessment/AssessmentDetail'
import Toast from '@/components/common/Toast'
import { AssessmentHistorySkeleton } from '@/components/common/Skeleton'
import type { Assessment, AssessmentResponses } from '@/types'

type Tab = 'new' | 'history'

export default function AssessmentPage() {
  const [activeTab, setActiveTab] = useState<Tab>('new')
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [selectedAssessment, setSelectedAssessment] = useState<Assessment | null>(null)
  const [latestAssessment, setLatestAssessment] = useState<Assessment | null>(null)
  const [toast, setToast] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const fetchAssessments = useCallback(async () => {
    try {
      const response = await fetch('/api/assessment')
      if (response.ok) {
        const data = await response.json()
        setAssessments(data.assessments || [])
      }
    } catch (error) {
      console.error('Failed to fetch assessments:', error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAssessments()
  }, [fetchAssessments])

  const handleSubmit = async (responses: AssessmentResponses, includeChatHistory: boolean) => {
    setIsSubmitting(true)
    try {
      const response = await fetch('/api/assessment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ responses, includeChatHistory }),
      })

      if (response.ok) {
        const data = await response.json()
        setLatestAssessment(data.assessment)
        setSelectedAssessment(data.assessment)
        await fetchAssessments()
      } else {
        setToast({ type: 'error', text: 'Failed to submit assessment. Please try again.' })
      }
    } catch (error) {
      console.error('Assessment submission error:', error)
      setToast({ type: 'error', text: 'Something went wrong. Please try again.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      const response = await fetch(`/api/assessment/${id}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        setAssessments((prev) => prev.filter((a) => a.id !== id))
        if (selectedAssessment?.id === id) {
          setSelectedAssessment(null)
        }
        if (latestAssessment?.id === id) {
          setLatestAssessment(null)
        }
      }
    } catch (error) {
      console.error('Failed to delete assessment:', error)
    }
  }

  const handleView = (assessment: Assessment) => {
    setSelectedAssessment(assessment)
  }

  const handleBack = () => {
    setSelectedAssessment(null)
  }

  const handleNewAssessment = () => {
    setSelectedAssessment(null)
    setLatestAssessment(null)
    setActiveTab('new')
  }

  // If viewing a specific assessment
  if (selectedAssessment) {
    return (
      <div className="p-6 max-w-4xl mx-auto overflow-y-auto h-full">
        {toast && <Toast message={toast.text} type={toast.type} onClose={() => setToast(null)} />}
        <AssessmentDetail assessment={selectedAssessment} onBack={handleBack} />
        {latestAssessment?.id === selectedAssessment.id && (
          <div className="mt-6 text-center">
            <button
              onClick={handleNewAssessment}
              className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors font-medium"
            >
              Take Another Assessment
            </button>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl mx-auto overflow-y-auto h-full">
      {toast && <Toast message={toast.text} type={toast.type} onClose={() => setToast(null)} />}
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-secondary mb-2">Wellness Assessment</h1>
        <p className="text-gray-500">
          Complete a brief questionnaire to receive personalized wellness recommendations.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg mb-6">
        <button
          onClick={() => setActiveTab('new')}
          className={`flex-1 py-2.5 px-4 rounded-md font-medium transition-colors ${
            activeTab === 'new'
              ? 'bg-white text-secondary shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          New Assessment
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`flex-1 py-2.5 px-4 rounded-md font-medium transition-colors ${
            activeTab === 'history'
              ? 'bg-white text-secondary shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          History {assessments.length > 0 && `(${assessments.length})`}
        </button>
      </div>

      {/* Content */}
      {activeTab === 'new' ? (
        <QuestionnaireForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
      ) : isLoading ? (
        <AssessmentHistorySkeleton />
      ) : (
        <AssessmentHistory
          assessments={assessments}
          onDelete={handleDelete}
          onView={handleView}
        />
      )}
    </div>
  )
}
