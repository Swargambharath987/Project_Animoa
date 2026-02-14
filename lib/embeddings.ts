const EMBEDDING_MODEL = 'BAAI/bge-small-en-v1.5'
const HF_API_URL = `https://api-inference.huggingface.co/pipeline/feature-extraction/${EMBEDDING_MODEL}`

export const EMBEDDING_DIMENSIONS = 384

/**
 * Generate a 384-dimensional embedding vector for a text string.
 * Uses HuggingFace Inference API with BAAI/bge-small-en-v1.5.
 */
export async function generateEmbedding(text: string): Promise<number[]> {
  const apiKey = process.env.HUGGINGFACE_API_KEY
  if (!apiKey) {
    throw new Error('HUGGINGFACE_API_KEY is not set')
  }

  const response = await fetch(HF_API_URL, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      inputs: text,
      options: { wait_for_model: true },
    }),
  })

  if (!response.ok) {
    throw new Error(`Embedding API error: ${response.status} ${response.statusText}`)
  }

  const embedding: number[] = await response.json()
  return embedding
}
