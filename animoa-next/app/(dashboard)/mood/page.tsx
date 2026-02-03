'use client'

import { useState, useEffect, useCallback } from 'react'
import MoodPicker from '@/components/mood/MoodPicker'
import MoodCalendar from '@/components/mood/MoodCalendar'
import MoodChart from '@/components/mood/MoodChart'
import Toast from '@/components/common/Toast'
import { MOOD_CONFIG } from '@/components/mood/MoodPicker'
import type { MoodEntry, MoodType } from '@/types'

export default function MoodPage() {
  const [moods, setMoods] = useState<MoodEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  const [selectedEntry, setSelectedEntry] = useState<MoodEntry | null>(null)
  const [toast, setToast] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const today = new Date().toISOString().split('T')[0]
  const todayEntry = moods.find((m) => m.date === today)

  const fetchMoods = useCallback(async () => {
    try {
      // Fetch last 90 days of moods
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - 90)
      const response = await fetch(
        `/api/mood?start=${startDate.toISOString().split('T')[0]}&end=${today}`
      )
      if (response.ok) {
        const data = await response.json()
        setMoods(data.moods || [])
      }
    } catch (error) {
      console.error('Failed to fetch moods:', error)
    } finally {
      setIsLoading(false)
    }
  }, [today])

  useEffect(() => {
    fetchMoods()
  }, [fetchMoods])

  const handleSaveMood = async (mood: MoodType, note: string) => {
    const date = selectedDate || today
    setIsSubmitting(true)

    try {
      const response = await fetch('/api/mood', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date, mood, note }),
      })

      if (response.ok) {
        await fetchMoods()
        setSelectedDate(null)
        setSelectedEntry(null)
        setToast({ type: 'success', text: 'Mood saved!' })
      } else {
        setToast({ type: 'error', text: 'Failed to save mood. Please try again.' })
      }
    } catch (error) {
      console.error('Failed to save mood:', error)
      setToast({ type: 'error', text: 'Something went wrong. Please try again.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDateClick = (date: string, entry?: MoodEntry) => {
    if (date === today) {
      setSelectedDate(null)
      setSelectedEntry(null)
    } else {
      setSelectedDate(date)
      setSelectedEntry(entry || null)
    }
  }

  const handleCancelEdit = () => {
    setSelectedDate(null)
    setSelectedEntry(null)
  }

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="p-6 max-w-6xl mx-auto overflow-y-auto h-full">
      {toast && <Toast message={toast.text} type={toast.type} onClose={() => setToast(null)} />}
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-secondary mb-2">Mood Tracker</h1>
        <p className="text-gray-500">
          Track your daily mood and discover patterns in your emotional well-being.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          {/* Editing past date notice */}
          {selectedDate && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-700 font-medium">
                  {selectedEntry ? 'Editing' : 'Logging'} mood for{' '}
                  {new Date(selectedDate).toLocaleDateString('en-US', {
                    weekday: 'long',
                    month: 'long',
                    day: 'numeric',
                  })}
                </p>
              </div>
              <button
                onClick={handleCancelEdit}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Cancel
              </button>
            </div>
          )}

          {/* Today's mood section or selected date */}
          <MoodPicker
            selectedMood={selectedDate ? selectedEntry?.mood : todayEntry?.mood}
            note={selectedDate ? selectedEntry?.note : todayEntry?.note}
            onSave={handleSaveMood}
            isSubmitting={isSubmitting}
          />

          {/* Today's summary */}
          {!selectedDate && todayEntry && (
            <div className="bg-gradient-to-br from-primary/5 to-blue-50 rounded-xl p-5 border border-primary/10">
              <div className="flex items-center gap-4">
                <span className="text-4xl">{MOOD_CONFIG[todayEntry.mood as MoodType]?.emoji}</span>
                <div>
                  <p className="font-medium text-secondary">
                    Today you're feeling {MOOD_CONFIG[todayEntry.mood as MoodType]?.label.toLowerCase()}
                  </p>
                  {todayEntry.note && (
                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">{todayEntry.note}</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Mood Chart */}
          <MoodChart moods={moods} />
        </div>

        {/* Right Column */}
        <div>
          <MoodCalendar moods={moods} onDateClick={handleDateClick} />

          {/* Quick stats */}
          <div className="mt-6 bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h4 className="font-medium text-secondary mb-4">Recent Activity</h4>
            {moods.length > 0 ? (
              <div className="space-y-3">
                {moods.slice(0, 5).map((entry) => (
                  <div
                    key={entry.id}
                    className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                    onClick={() => handleDateClick(entry.date, entry)}
                  >
                    <span className="text-2xl">
                      {MOOD_CONFIG[entry.mood as MoodType]?.emoji}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-secondary">
                        {new Date(entry.date).toLocaleDateString('en-US', {
                          weekday: 'short',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </p>
                      {entry.note && (
                        <p className="text-xs text-gray-500 truncate">{entry.note}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 text-center py-4">
                No mood entries yet. Start tracking today!
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
