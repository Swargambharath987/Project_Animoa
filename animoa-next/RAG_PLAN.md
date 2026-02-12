# RAG Integration Plan — Animoa Mental Health Companion

## Context

Animoa's AI (Groq/Llama 3.3 70B) currently generates recommendations using only its training knowledge + user profile + assessment scores. The responses are generic — they don't reference specific, evidence-based mental health techniques. Adding RAG gives the AI a curated knowledge base of CBT techniques, coping strategies, mindfulness exercises, etc., so responses become specific, actionable, and grounded in real therapeutic practices.

---

## How It Works (Simple)

```
Current:  User message → Groq LLM → generic response

With RAG: User message → embed message → search knowledge base →
          pass relevant techniques to Groq → specific, grounded response
```

---

## Tech Choices

| Component | Choice | Why |
|-----------|--------|-----|
| Vector DB | Supabase pgvector | Free extension, already using Supabase |
| Embedding model | TBD (leaning `BAAI/bge-small-en-v1.5` via HuggingFace API) | Free tier, 384 dimensions (compact), English-only matches app. OpenAI `text-embedding-3-small` is an alternative ($0.02/1M tokens) |
| Vector dimensions | 384 | Small = fast search, good quality for this model |
| New dependencies | `tsx` (dev only, for seed script) | No new runtime deps — uses native `fetch()` for HF API |

**New env variable:** `HUGGINGFACE_API_KEY` (free from huggingface.co/settings/tokens)

**Status:** Embedding model choice is open — to be decided before implementation.

---

## Database Changes (Supabase SQL Editor)

### 1. Enable pgvector
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. Create knowledge_base table
```sql
CREATE TABLE knowledge_base (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category TEXT NOT NULL,
  subcategory TEXT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  tags TEXT[] DEFAULT '{}',
  severity_relevance TEXT[] DEFAULT '{}'::TEXT[],
  assessment_domains TEXT[] DEFAULT '{}'::TEXT[],
  embedding VECTOR(384) NOT NULL,
  source TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX knowledge_base_embedding_idx
  ON knowledge_base USING ivfflat (embedding vector_cosine_ops) WITH (lists = 20);
CREATE INDEX knowledge_base_category_idx ON knowledge_base (category);
CREATE INDEX knowledge_base_tags_idx ON knowledge_base USING GIN (tags);
CREATE INDEX knowledge_base_assessment_domains_idx ON knowledge_base USING GIN (assessment_domains);
```

### 3. Create vector search function
```sql
CREATE OR REPLACE FUNCTION match_knowledge(
  query_embedding VECTOR(384),
  match_count INT DEFAULT 5,
  filter_category TEXT DEFAULT NULL,
  filter_domains TEXT[] DEFAULT NULL,
  similarity_threshold FLOAT DEFAULT 0.5
)
RETURNS TABLE (
  id UUID, category TEXT, subcategory TEXT, title TEXT, content TEXT,
  tags TEXT[], severity_relevance TEXT[], assessment_domains TEXT[],
  source TEXT, similarity FLOAT
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT kb.id, kb.category, kb.subcategory, kb.title, kb.content,
    kb.tags, kb.severity_relevance, kb.assessment_domains, kb.source,
    1 - (kb.embedding <=> query_embedding) AS similarity
  FROM knowledge_base kb
  WHERE (filter_category IS NULL OR kb.category = filter_category)
    AND (filter_domains IS NULL OR kb.assessment_domains && filter_domains)
    AND (1 - (kb.embedding <=> query_embedding)) > similarity_threshold
  ORDER BY kb.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

---

## Knowledge Base Content

**9 categories, ~60-80 entries total.** Each entry is 150-400 words — self-contained, actionable.

| Category | Examples | ~Count |
|----------|----------|--------|
| `cbt_techniques` | Cognitive restructuring, thought records, ABC model | 8-10 |
| `anxiety_management` | 5-4-3-2-1 grounding, 4-7-8 breathing, PMR | 8-10 |
| `depression_coping` | Behavioral activation, pleasure scheduling, self-compassion | 8-10 |
| `mindfulness` | Body scan, mindful breathing, present moment awareness | 6-8 |
| `sleep_hygiene` | Sleep schedule, wind-down routine, stimulus control | 6-8 |
| `social_support` | Building connections, communication skills, boundary setting | 5-6 |
| `stress_management` | Time management, relaxation techniques, lifestyle changes | 5-6 |
| `coping_strategies` | Emotion regulation, distress tolerance, self-care routines | 6-8 |
| `psychoeducation` | Understanding anxiety, mood-thought connection, nervous system | 6-8 |

Each entry has: `category`, `subcategory`, `title`, `content`, `tags[]`, `severity_relevance[]` (mild/moderate/severe), `assessment_domains[]` (depression/anxiety/sleep/social_support), `source`.

---

## New Files to Create

### `lib/embeddings.ts` — Embedding generation
- `generateEmbedding(text: string): Promise<number[]>` — calls embedding API (HuggingFace or OpenAI)
- Single function, easy to swap provider later

### `lib/rag.ts` — Core RAG logic
- `retrieveKnowledge(query, options?)` — embed query → pgvector search → return results
- `formatKnowledgeContext(results)` — format results into prompt-ready text
- `buildAssessmentQuery(responses)` — convert assessment answers into a natural language search query
- `getRelevantDomains(responses)` — determine which domains to filter on (depression/anxiety/sleep/social_support)

### `scripts/seed-knowledge-base.ts` — Seed script
- Contains all 60-80 knowledge entries as a typed array
- Loops through, generates embeddings, inserts into Supabase
- Rate-limited for free tier APIs
- Run with: `npx tsx scripts/seed-knowledge-base.ts`

---

## Existing Files to Modify

### `lib/groq.ts` — Add RAG-aware prompts
- Add `getSystemPromptWithRAG(profile, knowledgeContext)` — extends chat system prompt with instructions to naturally reference retrieved knowledge
- Add `getAssessmentPromptWithRAG(knowledgeContext)` — assessment prompt that prioritizes recommending specific techniques from retrieved resources

### `app/api/chat/route.ts` — RAG in chat
- Before building Groq messages: embed user message → retrieve 3 knowledge entries → inject into system prompt
- Added latency: ~200-400ms (masked by streaming)
- Falls back to non-RAG if retrieval fails

### `app/api/assessment/route.ts` — RAG in assessments
- In `generateRecommendations()`: build assessment query → retrieve 5 domain-filtered entries → inject into assessment prompt
- More results than chat (5 vs 3) because assessment needs broader coverage

### `types/index.ts` — Add types
- `KnowledgeEntry` and `KnowledgeSearchResult` interfaces

### `.env.example` — Add embedding API key variable

### `package.json` — Add seed script + tsx dev dependency

---

## RAG Flow: Chat

```
1. User: "I can't sleep and feel anxious"
2. Embed message → [0.023, -0.112, ...] (384 dims)
3. pgvector search → top 3 matches:
   - "Progressive Muscle Relaxation for Sleep" (0.82)
   - "4-7-8 Breathing Technique" (0.78)
   - "Sleep Hygiene: Wind-Down Routine" (0.71)
4. Inject into system prompt as "Evidence-Based Resources"
5. Groq responds: "One thing that can really help is the 4-7-8
   breathing technique — breathe in for 4 counts, hold for 7..."
```

## RAG Flow: Assessment

```
1. User scores: moderate depression, severe anxiety, poor sleep
2. Build query: "moderate depression, low mood. severe anxiety,
   nervousness. poor sleep quality. coping strategies"
3. Filter domains: ['depression', 'anxiety', 'sleep']
4. pgvector search → top 5 domain-filtered matches
5. Assessment prompt prioritizes these specific techniques
6. Recommendations include: named CBT exercises, specific breathing
   techniques, concrete sleep hygiene steps
```

---

## Graceful Degradation

If any part of RAG fails (embedding API down, pgvector error, no matches above threshold), the app falls back silently to its current non-RAG behavior. No user-facing errors.

---

## Implementation Steps

1. **Database setup** — Run SQL in Supabase (pgvector, table, indexes, RPC function)
2. **Environment** — Get embedding API key, add to `.env.local` + Vercel
3. **Create `lib/embeddings.ts`** — Embedding function
4. **Create `lib/rag.ts`** — Retrieval + context formatting
5. **Create seed script + write knowledge content** — 60-80 entries (most time-intensive step)
6. **Run seed script** — Populate knowledge base
7. **Modify `lib/groq.ts`** — Add RAG-aware prompt functions
8. **Modify `app/api/chat/route.ts`** — Integrate RAG into chat
9. **Modify `app/api/assessment/route.ts`** — Integrate RAG into assessments
10. **Update types + .env.example + package.json**
11. **Test & tune** — Verify chat and assessment both use retrieved knowledge

---

## Verification

1. **Seed check**: Query `SELECT count(*) FROM knowledge_base;` — should show 60-80 entries
2. **Chat test**: Send "I feel anxious" → response should mention specific techniques (grounding, breathing)
3. **Assessment test**: Complete with high anxiety scores → recommendations should include named CBT exercises
4. **Fallback test**: Temporarily break embedding API key → app should still work with generic responses
5. **Build test**: `npm run build` passes with no type errors

---

## Open Decisions

- [ ] **Embedding model**: HuggingFace `bge-small-en-v1.5` (free) vs OpenAI `text-embedding-3-small` ($0.02/1M tokens)
- [ ] If OpenAI chosen, vector dimensions change to 1536 (update table + function accordingly)
