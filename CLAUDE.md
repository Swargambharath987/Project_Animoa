# CLAUDE.md — Animoa

## What is Animoa

Mental health companion web app. Users chat with an empathetic AI, take wellness assessments (PHQ-2/GAD-2), track daily mood, and get personalized recommendations. Built with Next.js 14 + Supabase + Groq (Llama 3.3 70B).

**Repo**: https://github.com/Swargambharath987/Project_Animoa

---

## Repo Structure

```
Project_Animoa/
├── app/                    # Next.js App Router
│   ├── (auth)/             # Auth pages (login, signup, forgot-password, reset-password)
│   ├── (dashboard)/        # Protected pages (chat, mood, assessment, profile)
│   ├── api/                # API routes (see below)
│   ├── auth/callback/      # Supabase OAuth callback
│   ├── layout.tsx          # Root layout (Inter font, metadata)
│   ├── page.tsx            # Landing page
│   └── globals.css         # Tailwind base styles
├── components/
│   ├── assessment/         # QuestionnaireForm, AssessmentDetail, AssessmentHistory
│   ├── chat/               # ChatInput, MessageBubble, FeedbackButtons, SessionList
│   ├── common/             # Sidebar, Skeleton, Toast
│   ├── crisis/             # CrisisAlert
│   └── mood/               # MoodPicker, MoodCalendar, MoodChart
├── lib/
│   ├── supabase/
│   │   ├── client.ts       # Browser Supabase client
│   │   └── server.ts       # Server Supabase client (cookies-based)
│   ├── groq.ts             # Groq client, system prompts, RAG-enhanced prompts
│   ├── rag.ts              # RAG retrieval, context formatting, assessment query builder
│   ├── embeddings.ts       # HuggingFace embedding generation (BAAI/bge-small-en-v1.5)
│   ├── crisis-detection.ts # Crisis keyword detection + resources (988, Crisis Text Line)
│   └── utils.ts            # Shared utilities
├── types/
│   └── index.ts            # All TypeScript interfaces (Profile, Message, MoodEntry, etc.)
├── docs/                   # Planning & logs
│   ├── Development_Log.md  # Session-by-session dev log
│   ├── RAG_PLAN.md         # RAG integration plan (pgvector, knowledge base design)
│   ├── MIGRATION_PLAN.md   # Streamlit → Next.js migration plan
│   └── MCP_MEMORY_PLAN.md  # MCP exploration notes
├── public/
│   └── logo.png            # App logo (served at /logo.png)
├── archive/                # Old Streamlit MVP (main_app_v7.py, translations.py, etc.)
├── middleware.ts            # Auth guard — protects /chat, /mood, /assessment, /profile
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
├── postcss.config.js
├── vercel.json
├── Dockerfile              # Multi-stage Node.js 20 build for production
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── README.md
└── CLAUDE.md               # This file
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| UI | Tailwind CSS, Lucide icons |
| State | Zustand |
| Auth & DB | Supabase (PostgreSQL + Auth + RLS) |
| AI | Groq SDK → Llama 3.3 70B Versatile |
| RAG | pgvector (Supabase), HuggingFace API (bge-small-en-v1.5, 384 dims) |
| PDF | jspdf |
| Deployment | Vercel (primary), Docker (optional) |

---

## API Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/api/chat` | POST | Send message → RAG retrieval → Groq streaming response |
| `/api/assessment` | GET | List user's assessments |
| `/api/assessment` | POST | Submit assessment → RAG-enhanced recommendations |
| `/api/assessment/[id]` | GET | Get single assessment |
| `/api/mood` | GET/POST | List or log mood entries |
| `/api/mood/[id]` | PUT/DELETE | Update or delete mood entry |
| `/api/sessions` | GET/POST | List or create chat sessions |
| `/api/sessions/[sessionId]` | DELETE | Delete a chat session |
| `/api/sessions/[sessionId]/messages` | GET | Get messages for a session |
| `/api/feedback` | POST | Submit feedback on AI response |
| `/api/profile` | GET/PUT | Get or update user profile |
| `/api/pdf` | POST | Generate wellness report PDF |

All API routes authenticate via `supabase.auth.getUser()` and return 401 if not logged in.

---

## Auth Flow

- **Supabase Auth** with email/password
- `middleware.ts` protects dashboard routes — redirects unauthenticated users to `/login`
- Logged-in users on auth pages get redirected to `/chat`
- Two Supabase clients:
  - `lib/supabase/client.ts` — browser-side (`createBrowserClient`)
  - `lib/supabase/server.ts` — server-side (`createServerClient` with cookies)
- OAuth callback at `/auth/callback`

---

## RAG Pipeline

**Status**: Code integrated, needs knowledge base seeding (see `docs/RAG_PLAN.md`).

```
Chat:       user message → embed (HF API) → pgvector search (top 3) → inject into system prompt → Groq
Assessment: responses → build query → embed → pgvector search (top 5, domain-filtered) → inject → Groq
```

- Embeddings: `lib/embeddings.ts` — calls HuggingFace Inference API
- Retrieval: `lib/rag.ts` — calls `match_knowledge` Supabase RPC function
- Prompts: `lib/groq.ts` — `getSystemPromptWithRAG()` for chat, `getAssessmentPromptWithRAG()` for assessments
- **Graceful degradation**: any RAG failure silently falls back to non-RAG behavior (returns empty array)

### RAG remaining work
1. Run pgvector SQL in Supabase (table + indexes + RPC function — see `docs/RAG_PLAN.md`)
2. Get HuggingFace API key, add to `.env.local`
3. Write + run seed script (`scripts/seed-knowledge-base.ts`) with 60-80 knowledge entries
4. Test and tune similarity thresholds

---

## Database Tables (Supabase)

| Table | Purpose |
|-------|---------|
| `profiles` | User profile (name, age, stress_level, goals, interests) |
| `chat_sessions` | Chat session metadata (title, created_at) |
| `chat_history` | Messages (user/bot/feedback) per session |
| `mood_logs` | Daily mood entries with notes (unique per user+date) |
| `questionnaire_responses` | Assessment responses + AI recommendations |
| `knowledge_base` | RAG entries with pgvector embeddings (pending setup) |

All tables use RLS filtered by `user_id`.

---

## Environment Variables

```env
NEXT_PUBLIC_SUPABASE_URL=         # Supabase project URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=    # Supabase anon key
SUPABASE_SERVICE_ROLE_KEY=        # Supabase service role key (server-only)
GROQ_API_KEY=                     # Groq API key
HUGGINGFACE_API_KEY=              # HuggingFace API key (for RAG embeddings)
NEXT_PUBLIC_SITE_URL=             # Site URL for auth redirects
```

---

## Commands

```bash
npm install          # Install dependencies
npm run dev          # Dev server at localhost:3000
npm run build        # Production build (runs TypeScript + ESLint checks)
npm run lint         # ESLint only
npm run seed-knowledge  # Seed RAG knowledge base (npx tsx scripts/seed-knowledge-base.ts)
```

---

## Crisis Detection

`lib/crisis-detection.ts` scans every user message for crisis keywords (suicide, self-harm, etc.). When detected, `components/crisis/CrisisAlert.tsx` displays emergency resources (988 Lifeline, Crisis Text Line, 911). This takes priority over the AI response.

---

## Key Patterns

- **Route groups**: `(auth)` and `(dashboard)` — separate layouts, shared under App Router
- **Streaming**: Chat API uses SSE (`ReadableStream`) for real-time AI responses
- **Session titles**: Auto-generated from first user message in a chat session
- **Imports**: Use `@/` path alias (maps to project root via `tsconfig.json`)
- **AI model**: `llama-3.3-70b-versatile` — temperature 0.7, max 500 tokens (chat) / 1000 tokens (assessment)

---

## Gotchas

- `npm run dev` does NOT check types — only `npm run build` runs full TypeScript + ESLint. Always build before deploying.
- Supabase clients are different for server vs browser — never import `lib/supabase/server.ts` in client components.
- The `middleware.ts` matcher excludes static files and images from auth checks.
- RAG silently fails — if responses seem generic, check that the knowledge base is seeded and `HUGGINGFACE_API_KEY` is set.

---

*Last updated: February 2026*
