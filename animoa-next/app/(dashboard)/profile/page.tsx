'use client'

import { useState, useEffect, useCallback } from 'react'
import type { Profile } from '@/types'

const stressLevelOptions = ['Low', 'Moderate', 'High', 'Very High'] as const

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  // Form state
  const [fullName, setFullName] = useState('')
  const [age, setAge] = useState('')
  const [stressLevel, setStressLevel] = useState('')
  const [goals, setGoals] = useState('')
  const [interests, setInterests] = useState('')

  const fetchProfile = useCallback(async () => {
    try {
      const response = await fetch('/api/profile')
      if (response.ok) {
        const data = await response.json()
        const p = data.profile as Profile
        setProfile(p)
        setFullName(p.full_name || '')
        setAge(p.age ? String(p.age) : '')
        setStressLevel(p.stress_level || '')
        setGoals(p.goals || '')
        setInterests(p.interests || '')
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error)
      setMessage({ type: 'error', text: 'Failed to load profile.' })
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProfile()
  }, [fetchProfile])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setMessage(null)

    const ageNum = age ? parseInt(age, 10) : undefined
    if (age && (isNaN(ageNum!) || ageNum! < 13 || ageNum! > 120)) {
      setMessage({ type: 'error', text: 'Age must be between 13 and 120.' })
      setIsSaving(false)
      return
    }

    try {
      const response = await fetch('/api/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: fullName.trim() || null,
          age: ageNum || null,
          stress_level: stressLevel || null,
          goals: goals.trim() || null,
          interests: interests.trim() || null,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setProfile(data.profile)
        setMessage({ type: 'success', text: 'Profile updated successfully!' })
        setTimeout(() => setMessage(null), 3000)
      } else {
        const data = await response.json()
        setMessage({ type: 'error', text: data.error || 'Failed to update profile.' })
      }
    } catch (error) {
      console.error('Profile save error:', error)
      setMessage({ type: 'error', text: 'Something went wrong. Please try again.' })
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="p-6 max-w-2xl mx-auto overflow-y-auto h-full">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-secondary mb-2">Profile Settings</h1>
        <p className="text-gray-500">
          Manage your personal information. This helps Animoa provide more personalized support.
        </p>
      </div>

      {/* Status message */}
      {message && (
        <div
          className={`mb-6 p-4 rounded-lg text-sm font-medium ${
            message.type === 'success'
              ? 'bg-green-50 text-green-700 border border-green-200'
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}
        >
          {message.text}
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Email (read-only) */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-secondary mb-4">Account</h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={profile?.email || ''}
              disabled
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-500 cursor-not-allowed"
            />
            <p className="text-xs text-gray-400 mt-1">Email cannot be changed.</p>
          </div>
        </div>

        {/* Personal Info */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-secondary mb-4">Personal Information</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Enter your name"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Age</label>
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                min={13}
                max={120}
                placeholder="Minimum age: 13"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
              <p className="text-xs text-gray-400 mt-1">Must be 13 or older to use Animoa.</p>
            </div>
          </div>
        </div>

        {/* Wellness Profile */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-secondary mb-4">Wellness Profile</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Current Stress Level
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {stressLevelOptions.map((level) => (
                  <label
                    key={level}
                    className={`flex items-center justify-center p-3 rounded-lg border cursor-pointer transition-all text-sm ${
                      stressLevel === level
                        ? 'border-primary bg-primary/5 text-primary font-medium'
                        : 'border-gray-200 hover:border-gray-300 text-gray-600'
                    }`}
                  >
                    <input
                      type="radio"
                      name="stressLevel"
                      value={level}
                      checked={stressLevel === level}
                      onChange={(e) => setStressLevel(e.target.value)}
                      className="sr-only"
                    />
                    {level}
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mental Wellness Goals
              </label>
              <textarea
                value={goals}
                onChange={(e) => setGoals(e.target.value)}
                placeholder="e.g., Reduce anxiety, improve sleep quality, build better habits..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                rows={3}
              />
              <p className="text-xs text-gray-400 mt-1">
                Your goals help Animoa tailor conversations and recommendations.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Interests &amp; Hobbies
              </label>
              <textarea
                value={interests}
                onChange={(e) => setInterests(e.target.value)}
                placeholder="e.g., Reading, yoga, hiking, cooking, music..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                rows={3}
              />
              <p className="text-xs text-gray-400 mt-1">
                Interests help Animoa suggest relevant coping activities.
              </p>
            </div>
          </div>
        </div>

        {/* Save button */}
        <button
          type="submit"
          disabled={isSaving}
          className="w-full py-4 bg-primary text-white rounded-xl font-semibold hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-lg"
        >
          {isSaving ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Saving...
            </span>
          ) : (
            'Save Changes'
          )}
        </button>
      </form>
    </div>
  )
}
