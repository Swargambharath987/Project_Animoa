// Crisis keywords that indicate potential mental health emergency
export const CRISIS_KEYWORDS = [
  'suicide',
  'suicidal',
  'kill myself',
  'end my life',
  'want to die',
  "don't want to live",
  'no reason to live',
  'better off dead',
  'self-harm',
  'self harm',
  'hurt myself',
  'cutting myself',
  'overdose',
  'end it all',
  'take my life',
  'not worth living',
]

// Crisis resources (English only)
export const CRISIS_RESOURCES = {
  title: 'Crisis Support Resources',
  message: `If you're experiencing a mental health crisis, please reach out for help:

**988 Suicide & Crisis Lifeline** - Call or text **988** (Available 24/7)

**Crisis Text Line** - Text **HOME** to **741741**

**International Association for Suicide Prevention** - https://www.iasp.info/resources/Crisis_Centres/

**Emergency Services** - Call **911** if you're in immediate danger

---

**You are not alone. Professional help is available right now.**

Animoa cares about your wellbeing, but I'm an AI companion and not a substitute for professional mental health care. Please reach out to the resources above if you're in crisis.`,
}

/**
 * Detect if a message contains crisis-related keywords
 * @param message - The message to check
 * @returns true if crisis keywords are detected
 */
export function detectCrisis(message: string): boolean {
  if (!message) return false

  const messageLower = message.toLowerCase()

  for (const keyword of CRISIS_KEYWORDS) {
    if (messageLower.includes(keyword)) {
      return true
    }
  }

  return false
}
