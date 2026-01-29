'use client'

import { useMemo, useState } from 'react'
import type { MoodEntry, MoodType } from '@/types'
import { MOOD_CONFIG } from './MoodPicker'

interface MoodChartProps {
  moods: MoodEntry[]
}

type TimeRange = '7d' | '14d' | '30d'

export default function MoodChart({ moods }: MoodChartProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('14d')

  const { chartData, stats } = useMemo(() => {
    const days = timeRange === '7d' ? 7 : timeRange === '14d' ? 14 : 30
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(endDate.getDate() - days + 1)

    // Create date range
    const dateRange: string[] = []
    for (let i = 0; i < days; i++) {
      const d = new Date(startDate)
      d.setDate(startDate.getDate() + i)
      dateRange.push(d.toISOString().split('T')[0])
    }

    // Map moods by date
    const moodMap: Record<string, MoodEntry> = {}
    moods.forEach((entry) => {
      moodMap[entry.date] = entry
    })

    // Build chart data
    const data = dateRange.map((date) => ({
      date,
      entry: moodMap[date] || null,
      value: moodMap[date] ? MOOD_CONFIG[moodMap[date].mood as MoodType]?.value || 0 : null,
    }))

    // Calculate stats
    const filledDays = data.filter((d) => d.value !== null)
    const avgMood = filledDays.length > 0
      ? filledDays.reduce((sum, d) => sum + (d.value || 0), 0) / filledDays.length
      : 0

    const moodCounts: Record<MoodType, number> = {
      very_happy: 0,
      happy: 0,
      neutral: 0,
      sad: 0,
      very_sad: 0,
    }
    filledDays.forEach((d) => {
      if (d.entry) {
        moodCounts[d.entry.mood as MoodType]++
      }
    })

    const mostFrequentMood = Object.entries(moodCounts)
      .sort((a, b) => b[1] - a[1])
      .find(([, count]) => count > 0)?.[0] as MoodType | undefined

    return {
      chartData: data,
      stats: {
        totalDays: days,
        loggedDays: filledDays.length,
        avgMood,
        mostFrequentMood,
      },
    }
  }, [moods, timeRange])

  // SVG Chart dimensions
  const width = 100
  const height = 40
  const padding = 2

  // Calculate chart points
  const points = useMemo(() => {
    const filledData = chartData.filter((d) => d.value !== null)
    if (filledData.length < 2) return null

    const xStep = (width - padding * 2) / (chartData.length - 1)
    const yScale = (height - padding * 2) / 4 // 5 levels (1-5) = 4 range

    return chartData
      .map((d, i) => {
        if (d.value === null) return null
        const x = padding + i * xStep
        const y = height - padding - (d.value - 1) * yScale
        return { x, y, entry: d.entry }
      })
      .filter(Boolean) as { x: number; y: number; entry: MoodEntry | null }[]
  }, [chartData])

  const pathD = points
    ? `M ${points.map((p) => `${p.x},${p.y}`).join(' L ')}`
    : ''

  const getMoodLabel = (value: number): string => {
    if (value >= 4.5) return 'Great'
    if (value >= 3.5) return 'Good'
    if (value >= 2.5) return 'Okay'
    if (value >= 1.5) return 'Low'
    return 'Struggling'
  }

  const getMoodColor = (value: number): string => {
    if (value >= 4.5) return '#22c55e'
    if (value >= 3.5) return '#84cc16'
    if (value >= 2.5) return '#eab308'
    if (value >= 1.5) return '#f97316'
    return '#ef4444'
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-secondary">Mood Trends</h3>
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
          {(['7d', '14d', '30d'] as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                timeRange === range
                  ? 'bg-white text-secondary shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {range === '7d' ? '7 days' : range === '14d' ? '14 days' : '30 days'}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      {points && points.length >= 2 ? (
        <div className="mb-6">
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="w-full h-32"
            preserveAspectRatio="none"
          >
            {/* Background grid lines */}
            {[1, 2, 3, 4, 5].map((level) => {
              const y = height - padding - (level - 1) * ((height - padding * 2) / 4)
              return (
                <line
                  key={level}
                  x1={padding}
                  y1={y}
                  x2={width - padding}
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth="0.3"
                />
              )
            })}

            {/* Gradient fill */}
            <defs>
              <linearGradient id="moodGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#4E9BB9" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#4E9BB9" stopOpacity="0.05" />
              </linearGradient>
            </defs>

            {/* Area fill */}
            {points.length >= 2 && (
              <path
                d={`${pathD} L ${points[points.length - 1].x},${height - padding} L ${points[0].x},${height - padding} Z`}
                fill="url(#moodGradient)"
              />
            )}

            {/* Line */}
            <path
              d={pathD}
              fill="none"
              stroke="#4E9BB9"
              strokeWidth="0.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Points */}
            {points.map((point, i) => (
              <circle
                key={i}
                cx={point.x}
                cy={point.y}
                r="1.2"
                fill="white"
                stroke="#4E9BB9"
                strokeWidth="0.6"
              />
            ))}
          </svg>

          {/* X-axis labels */}
          <div className="flex justify-between mt-2 px-1">
            <span className="text-xs text-gray-400">
              {new Date(chartData[0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            </span>
            <span className="text-xs text-gray-400">
              {new Date(chartData[chartData.length - 1].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            </span>
          </div>
        </div>
      ) : (
        <div className="h-32 flex items-center justify-center bg-gray-50 rounded-lg mb-6">
          <p className="text-gray-400 text-sm">
            Log at least 2 days to see your mood trends
          </p>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-secondary">
            {stats.loggedDays}/{stats.totalDays}
          </div>
          <div className="text-xs text-gray-500">Days logged</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          {stats.avgMood > 0 ? (
            <>
              <div
                className="text-2xl font-bold"
                style={{ color: getMoodColor(stats.avgMood) }}
              >
                {getMoodLabel(stats.avgMood)}
              </div>
              <div className="text-xs text-gray-500">Average mood</div>
            </>
          ) : (
            <>
              <div className="text-2xl font-bold text-gray-300">—</div>
              <div className="text-xs text-gray-500">Average mood</div>
            </>
          )}
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          {stats.mostFrequentMood ? (
            <>
              <div className="text-2xl">
                {MOOD_CONFIG[stats.mostFrequentMood].emoji}
              </div>
              <div className="text-xs text-gray-500">Most frequent</div>
            </>
          ) : (
            <>
              <div className="text-2xl text-gray-300">—</div>
              <div className="text-xs text-gray-500">Most frequent</div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
