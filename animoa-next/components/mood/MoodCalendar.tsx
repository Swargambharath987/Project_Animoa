'use client'

import { useState, useMemo } from 'react'
import type { MoodEntry, MoodType } from '@/types'
import { MOOD_CONFIG } from './MoodPicker'

interface MoodCalendarProps {
  moods: MoodEntry[]
  onDateClick: (date: string, entry?: MoodEntry) => void
}

export default function MoodCalendar({ moods, onDateClick }: MoodCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date())

  const moodByDate = useMemo(() => {
    const map: Record<string, MoodEntry> = {}
    moods.forEach((entry) => {
      map[entry.date] = entry
    })
    return map
  }, [moods])

  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()

  const firstDayOfMonth = new Date(year, month, 1)
  const lastDayOfMonth = new Date(year, month + 1, 0)
  const startingDayOfWeek = firstDayOfMonth.getDay()
  const daysInMonth = lastDayOfMonth.getDate()

  const prevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1))
  }

  const nextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1))
  }

  const goToToday = () => {
    setCurrentDate(new Date())
  }

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  const today = new Date()
  const todayString = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  const days: (number | null)[] = []
  for (let i = 0; i < startingDayOfWeek; i++) {
    days.push(null)
  }
  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i)
  }

  const formatDateString = (day: number) => {
    return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-secondary">Mood Calendar</h3>
        <div className="flex items-center gap-2">
          <button
            onClick={prevMonth}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-500 hover:text-gray-700"
          >
            ←
          </button>
          <button
            onClick={goToToday}
            className="px-3 py-1.5 text-sm font-medium text-primary hover:bg-primary/10 rounded-lg transition-colors"
          >
            Today
          </button>
          <button
            onClick={nextMonth}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-500 hover:text-gray-700"
          >
            →
          </button>
        </div>
      </div>

      {/* Month/Year */}
      <div className="text-center mb-4">
        <span className="text-xl font-semibold text-secondary">
          {monthNames[month]} {year}
        </span>
      </div>

      {/* Day names */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {dayNames.map((day) => (
          <div key={day} className="text-center text-xs font-medium text-gray-500 py-2">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-1">
        {days.map((day, index) => {
          if (day === null) {
            return <div key={`empty-${index}`} className="aspect-square" />
          }

          const dateString = formatDateString(day)
          const entry = moodByDate[dateString]
          const isToday = dateString === todayString
          const isFuture = dateString > todayString

          return (
            <button
              key={dateString}
              onClick={() => !isFuture && onDateClick(dateString, entry)}
              disabled={isFuture}
              className={`aspect-square rounded-lg flex flex-col items-center justify-center transition-all ${
                isFuture
                  ? 'text-gray-300 cursor-not-allowed'
                  : isToday
                  ? 'bg-primary/10 ring-2 ring-primary'
                  : entry
                  ? 'hover:bg-gray-50 cursor-pointer'
                  : 'hover:bg-gray-50 cursor-pointer'
              }`}
            >
              <span className={`text-sm ${isToday ? 'font-bold text-primary' : 'text-gray-600'}`}>
                {day}
              </span>
              {entry && (
                <span className="text-lg leading-none mt-0.5">
                  {MOOD_CONFIG[entry.mood as MoodType]?.emoji || '•'}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-100">
        <p className="text-xs text-gray-500 mb-2">Mood legend:</p>
        <div className="flex flex-wrap gap-3">
          {Object.entries(MOOD_CONFIG).map(([key, config]) => (
            <div key={key} className="flex items-center gap-1">
              <span className="text-sm">{config.emoji}</span>
              <span className="text-xs text-gray-500">{config.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
