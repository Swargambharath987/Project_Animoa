'use client'

import { CRISIS_RESOURCES } from '@/lib/crisis-detection'

interface CrisisAlertProps {
  isVisible: boolean
  onDismiss: () => void
}

export default function CrisisAlert({ isVisible, onDismiss }: CrisisAlertProps) {
  if (!isVisible) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="bg-red-500 text-white p-4 rounded-t-xl">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <span>🆘</span>
            {CRISIS_RESOURCES.title}
          </h2>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="prose prose-sm max-w-none">
            {CRISIS_RESOURCES.message.split('\n\n').map((paragraph, i) => (
              <p key={i} className="mb-4 whitespace-pre-wrap">
                {paragraph.split('**').map((part, j) =>
                  j % 2 === 1 ? <strong key={j}>{part}</strong> : part
                )}
              </p>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 flex justify-end">
          <button
            onClick={onDismiss}
            className="px-6 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            I understand
          </button>
        </div>
      </div>
    </div>
  )
}
