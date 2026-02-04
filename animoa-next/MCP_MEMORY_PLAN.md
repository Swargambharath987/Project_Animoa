# Phase 3: MCP Memory Server for Animoa

## Goal
Give Animoa persistent memory that works like a real therapist - remembers key facts about the user but only surfaces them **when they'd actually help**, not every single message. Expose the memory system as an MCP server.

## Core Principle: Trigger-Based Retrieval

Memories are NOT injected into every prompt. They are retrieved only when specific conditions are met:

| Trigger | What happens | Example |
|---------|-------------|---------|
| **Explicit reference** | User says "remember", "last time", "I told you", "you know" | "Remember when I told you about my dog?" |
| **Session start** | First message in a new session gets 2-3 core facts for natural continuity | User opens new chat → inject name + 1-2 key facts |
| **Topic match** | User message contains keywords matching a memory category | User mentions "work" → fetch work-related memories only |
| **Crisis skip** | Crisis keywords detected → zero memory injection, focus on safety | User expresses self-harm → pure crisis response |
| **Default** | No trigger matched → no memories injected, just listen | User says "I had a nice lunch" → respond naturally |

This means most messages get **zero** memory overhead. The AI earns trust by remembering things at the right moment, not by constantly proving it remembers.

## New Files

```
animoa-next/
  lib/mcp/
    memory-service.ts       # Core: extract, store, retrieve, deduplicate
    memory-triggers.ts      # Trigger detection: should we fetch memories?
    memory-tools.ts         # MCP tool definitions
    memory-resources.ts     # MCP resource definitions
    server.ts               # MCP server factory
  app/api/
    memory/route.ts         # REST API for memory management page (GET/DELETE)
    mcp/route.ts            # HTTP endpoint for remote MCP clients
  app/(dashboard)/
    memory/page.tsx         # User memory management page
  components/memory/
    MemoryList.tsx           # Grouped memory display with delete
    MemoryEmpty.tsx          # Empty state
  mcp-stdio.ts              # Standalone stdio server (Claude Desktop)
```

## Modified Files

- `types/index.ts` - Add Memory, MemoryCategory, MemoryTrigger types
- `lib/groq.ts` - Add optional `memoryContext` param to `getSystemPrompt()`
- `app/api/chat/route.ts` - Add trigger check + conditional memory retrieval + async extraction
- `components/common/Sidebar.tsx` - Add Memory nav item
- `package.json` - Add `@modelcontextprotocol/sdk`, `zod`

## Database

New `user_memories` table:

```sql
CREATE TABLE user_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    category TEXT NOT NULL DEFAULT 'general',
    content TEXT NOT NULL,
    source_session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
    confidence REAL DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_memories_active ON user_memories (user_id) WHERE is_active = TRUE;
ALTER TABLE user_memories ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own memories" ON user_memories FOR ALL USING (auth.uid() = user_id);
```

Categories: `personal`, `emotional`, `health`, `relationship`, `work`, `goal`, `preference`, `general`

## Implementation Steps

### Step 1: Types + Dependencies
- Add types to `types/index.ts`: `Memory`, `MemoryCategory`, `MemoryTriggerResult`
- Install `@modelcontextprotocol/sdk` and `zod`

### Step 2: Memory Trigger System (`lib/mcp/memory-triggers.ts`)
The brain of the system. Pure functions, no DB calls:

```
shouldRetrieveMemories(message, isFirstInSession, isCrisis) → {
  shouldRetrieve: boolean
  triggerType: 'explicit_recall' | 'session_start' | 'topic_match' | 'none'
  matchedCategories?: MemoryCategory[]  // for topic_match, which categories to fetch
}
```

Logic:
- Check crisis keywords first → return `{ shouldRetrieve: false }` immediately
- Check explicit recall phrases → return `{ shouldRetrieve: true, triggerType: 'explicit_recall' }`
- Check if first message in session → return `{ shouldRetrieve: true, triggerType: 'session_start' }`
- Check topic keywords against category keyword maps → return matched categories
- Default → `{ shouldRetrieve: false }`

Category keyword map (e.g.):
- `work`: job, work, boss, colleague, office, deadline, career, promotion
- `relationship`: family, friend, partner, spouse, parent, child, mom, dad, sister, brother
- `health`: sleep, exercise, medication, doctor, therapy, headache, tired, energy
- `emotional`: anxious, depressed, stressed, happy, sad, angry, lonely, overwhelmed
- etc.

### Step 3: Memory Service (`lib/mcp/memory-service.ts`)
Core logic, no MCP dependency:
- `extractMemoriesFromExchange(userMsg, botMsg)` - Groq extraction (temp 0.1, max 300 tokens), with instruction to avoid storing traumatic details as blunt facts
- `storeMemory(supabase, userId, content, category, sessionId?, confidence?)` - deduplicate via `contentOverlaps()`, then insert
- `recallMemories(supabase, userId, options)` - options: `{ categories?, limit?, coreOnly? }`
  - `coreOnly: true` → fetch top 3 by confidence + access count (for session_start trigger)
  - `categories` → fetch only those categories (for topic_match trigger)
  - no filter → fetch all active (for explicit_recall trigger), capped at 30
- `searchMemories(supabase, userId, query)` - ILIKE keyword search
- `deleteMemory(supabase, userId, memoryId)` - soft delete
- `buildMemoryContext(memories, triggerType)` - format differs by trigger:
  - `session_start`: "Some things you know about this user: [2-3 facts]. Only reference these if naturally relevant."
  - `explicit_recall`: "The user is asking about something from the past. Here's what you remember: [relevant facts]"
  - `topic_match`: "Context that may be relevant to this topic: [category-specific facts]"

### Step 4: Integrate into Chat (`app/api/chat/route.ts`)
Modifications to the chat route:

1. Import trigger + memory modules
2. After profile fetch (line 28), before building groqMessages:
   ```
   - Determine if this is the first message in the session (check conversationHistory length)
   - Check if crisis keywords present (reuse existing crisis detection)
   - Call shouldRetrieveMemories(message, isFirst, isCrisis)
   - If shouldRetrieve: call recallMemories with appropriate options
   - Build memoryContext string (or empty string if no retrieval)
   ```
3. Line 42: `getSystemPrompt(profile ?? undefined, memoryContext)`
4. After saving bot response (line 83): fire-and-forget extraction:
   ```
   extractMemoriesFromExchange(message, fullResponse)
     .then(extracted => storeExtractedMemories(...))
     .catch(console.error)
   ```

### Step 5: Update System Prompt (`lib/groq.ts`)
- Add `memoryContext?: string` param to `getSystemPrompt()`
- Append to end of prompt if present
- Existing behavior preserved when called without memories

### Step 6: Memory Management API (`app/api/memory/route.ts`)
- `GET` - Fetch all active memories for authenticated user, grouped by category
- `DELETE` - Soft-delete a memory by ID (set `is_active = false`)

### Step 7: Memory Management Page
**`app/(dashboard)/memory/page.tsx`** - User-facing memory management

Layout:
- Header: "What Animoa Remembers" with brief explainer text
- Memories grouped by category with category headers
- Each memory card shows: content, when it was learned (date), confidence dot (high/medium/low)
- Delete button on each card with confirmation
- Empty state when no memories exist yet
- Total memory count in header

**`components/memory/MemoryList.tsx`** - Grouped display component
**`components/memory/MemoryEmpty.tsx`** - Empty state with friendly message

**Sidebar update** (`components/common/Sidebar.tsx`):
- Add `{ href: '/memory', label: 'Memory', emoji: '🧠' }` to navItems (after Profile)

### Step 8: MCP Tools (`lib/mcp/memory-tools.ts`)
4 tools with zod schemas:
- `store_memory` - content, category, confidence
- `recall_memories` - optional category, limit
- `search_memories` - keyword query
- `delete_memory` - memory UUID

### Step 9: MCP Resources (`lib/mcp/memory-resources.ts`)
3 resources:
- `animoa://user/profile` - user profile JSON
- `animoa://user/mood-summary` - 30-day mood stats
- `animoa://user/assessment-summary` - latest assessment

### Step 10: MCP Server + Endpoints
- `lib/mcp/server.ts` - factory, registers tools + resources
- `app/api/mcp/route.ts` - HTTP transport (Vercel-hosted)
- `mcp-stdio.ts` - stdio transport (Claude Desktop, uses service role key)

## Chat Flow After Changes

```
User message
    ↓
Auth + Profile fetch (existing)
    ↓
Trigger check ← NEW (pure function, <1ms)
    ↓
┌─ trigger matched? ──→ Fetch relevant memories (~50-100ms)
│                            ↓
│                      Build memory context string
│
└─ no trigger ────────→ memoryContext = '' (zero overhead)
    ↓
Build system prompt (with or without memory context)
    ↓
Groq stream → Response sent (existing)
    ↓
Async: Extract memories from exchange → Store new facts (fire-and-forget)
```

## Memory Page Design

```
┌─────────────────────────────────────────┐
│  What Animoa Remembers          12 items │
│  Things I've learned from our chats.    │
│  You can remove anything here.          │
│                                         │
│  ── Personal ──────────────────────     │
│  ┌─────────────────────────────┐        │
│  │ Has a golden retriever       │  🗑   │
│  │ named Max                    │       │
│  │ Learned Jan 28 · ●●● high   │       │
│  └─────────────────────────────┘        │
│  ┌─────────────────────────────┐        │
│  │ Lives in Austin, Texas       │  🗑   │
│  │ Learned Jan 30 · ●●○ med    │       │
│  └─────────────────────────────┘        │
│                                         │
│  ── Work ──────────────────────────     │
│  ┌─────────────────────────────┐        │
│  │ Software engineer, stressed  │  🗑   │
│  │ about upcoming deadline      │       │
│  │ Learned Feb 1 · ●●● high    │       │
│  └─────────────────────────────┘        │
│                                         │
│  ── Emotional ─────────────────────     │
│  │ ...                          │       │
└─────────────────────────────────────────┘
```

## Verification

1. **Trigger logic**: Send messages with/without trigger words, verify memories are only fetched when appropriate
2. **Extraction**: Mention personal facts in chat, check `user_memories` table has them
3. **Session continuity**: Start new session → AI naturally references a core fact
4. **Crisis safety**: Send crisis message → verify zero memory injection, pure safety response
5. **Memory page**: View memories, delete one, verify it's gone from future retrievals
6. **MCP tools**: Test via MCP Inspector or Claude Desktop
7. **No regression**: Chat, assessment, mood features work unchanged
8. **Build**: `npm run build` passes with no errors
