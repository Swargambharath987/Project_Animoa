import { generateEmbedding } from '@/lib/embeddings'
import { createClient } from '@/lib/supabase/server'
import type { AssessmentResponses } from '@/types'

export interface KnowledgeResult {
  id: string
  category: string
  subcategory: string | null
  title: string
  content: string
  tags: string[]
  severity_relevance: string[]
  assessment_domains: string[]
  source: string | null
  similarity: number
}

/**
 * Retrieve relevant knowledge base entries for a given query.
 * Returns empty array on any failure (graceful degradation).
 */
export async function retrieveKnowledge(
  query: string,
  options?: {
    matchCount?: number
    category?: string
    domains?: string[]
    similarityThreshold?: number
  }
): Promise<KnowledgeResult[]> {
  const {
    matchCount = 3,
    category = null,
    domains = null,
    similarityThreshold = 0.5,
  } = options || {}

  try {
    const queryEmbedding = await generateEmbedding(query)
    const supabase = createClient()

    const { data, error } = await supabase.rpc('match_knowledge', {
      query_embedding: queryEmbedding,
      match_count: matchCount,
      filter_category: category,
      filter_domains: domains,
      similarity_threshold: similarityThreshold,
    })

    if (error) {
      console.error('RAG retrieval error:', error)
      return []
    }

    return (data as KnowledgeResult[]) || []
  } catch (err) {
    console.error('RAG pipeline error:', err)
    return []
  }
}

/**
 * Format retrieved knowledge into a context string for prompt injection.
 */
export function formatKnowledgeContext(results: KnowledgeResult[]): string {
  if (!results || results.length === 0) return ''

  const entries = results
    .map(
      (r, i) =>
        `[${i + 1}] ${r.title}\n${r.content}${r.source ? `\n(Source: ${r.source})` : ''}`
    )
    .join('\n\n')

  return `\n\n---\nRelevant Evidence-Based Resources:\n${entries}\n---`
}

/**
 * Build a natural language search query from assessment responses.
 * Optimized for embedding similarity against the knowledge base.
 */
export function buildAssessmentQuery(responses: AssessmentResponses): string {
  const parts: string[] = []

  const severityMap: Record<string, string> = {
    not_at_all: 'minimal',
    several_days: 'mild',
    more_than_half: 'moderate',
    nearly_every_day: 'severe',
  }

  const moodSeverity = severityMap[responses.mood] || 'some'
  const anxietySeverity = severityMap[responses.anxiety] || 'some'

  if (responses.mood !== 'not_at_all' || responses.interest !== 'not_at_all') {
    parts.push(`${moodSeverity} depression symptoms, low mood, reduced interest in activities`)
  }
  if (responses.anxiety !== 'not_at_all' || responses.worry !== 'not_at_all') {
    parts.push(`${anxietySeverity} anxiety, nervousness, difficulty controlling worry`)
  }
  if (responses.sleep === 'poor' || responses.sleep === 'very_poor') {
    parts.push('poor sleep quality, sleep difficulties')
  }
  if (responses.support === 'limited' || responses.support === 'none') {
    parts.push('limited social support, feeling isolated')
  }

  parts.push('coping strategies and evidence-based techniques for mental wellness')

  return parts.join('. ')
}

/**
 * Determine which assessment domains to filter on based on responses.
 */
export function getRelevantDomains(responses: AssessmentResponses): string[] {
  const domains: string[] = []

  if (responses.mood !== 'not_at_all' || responses.interest !== 'not_at_all') {
    domains.push('depression')
  }
  if (responses.anxiety !== 'not_at_all' || responses.worry !== 'not_at_all') {
    domains.push('anxiety')
  }
  if (responses.sleep === 'poor' || responses.sleep === 'very_poor' || responses.sleep === 'fair') {
    domains.push('sleep')
  }
  if (responses.support === 'limited' || responses.support === 'none') {
    domains.push('social_support')
  }

  if (domains.length === 0) domains.push('depression', 'anxiety')
  return domains
}
