# Animoa Next.js Migration Plan

**Version**: 2.0 (Next.js)
**Created**: January 21, 2026
**Status**: Planning Phase

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current Application Analysis](#current-application-analysis)
3. [Target Architecture](#target-architecture)
4. [Migration Phases](#migration-phases)
5. [Feature Migration Checklist](#feature-migration-checklist)
6. [Database Schema](#database-schema)
7. [API Routes Design](#api-routes-design)
8. [Component Architecture](#component-architecture)
9. [MCP Server Integration Ideas](#mcp-server-integration-ideas)
10. [Personalization Enhancement Ideas](#personalization-enhancement-ideas)
11. [Deployment Strategy](#deployment-strategy)
12. [Future Evolution Path](#future-evolution-path)

---

## Executive Summary

This document outlines the migration of Animoa from a Streamlit (Python) application to a modern Next.js (React/TypeScript) application. The new version will be:

- **English-only** (removing multi-language complexity)
- **Vercel-deployable** (free tier compatible)
- **Evolvable** (minimum evolvable product approach)
- **Cloud-ready** (adaptable for future scaling)

### Key Changes from v7

| Aspect | Current (v7) | New (v2.0) |
|--------|--------------|------------|
| Framework | Streamlit (Python) | Next.js 14 (TypeScript) |
| Languages | EN/ES/ZH | English only |
| Styling | Streamlit CSS | Tailwind CSS + shadcn/ui |
| Deployment | Manual | Vercel (auto CI/CD) |
| State | Streamlit session | React state + Zustand |

---

## Current Application Analysis

### Features to Migrate (from main_app_v7.py)

#### 1. Authentication System (Lines 139-292)
- Email/password login and signup
- Supabase Auth integration
- Session management with access/refresh tokens
- Profile creation on signup

#### 2. User Profile Management (Lines 312-426)
- Full name, age (min 13)
- Stress level selection
- Mental wellness goals
- Interests
- ~~Language preference~~ (REMOVING)

#### 3. Crisis Detection System (Lines 428-504)
- Keyword-based crisis detection
- ~~Multi-language crisis resources~~ (English only)
- Immediate resource display on detection

#### 4. AI Chat System (Lines 506-1058)
- Groq LLM integration (llama-3.3-70b-versatile)
- Multi-session chat management
- Message persistence in Supabase
- Feedback system (emoji reactions)
- ~~Chat translation~~ (REMOVING)
- Chat deletion

#### 5. Mental Health Advisory/Assessment (Lines 1293-1667)
- PHQ-2 depression screening questions
- GAD-2 anxiety screening questions
- Sleep quality assessment
- Social support assessment
- Coping strategies input
- AI-generated personalized recommendations
- PDF report generation
- Assessment history viewing/deletion

#### 6. Mood Tracker (Lines 1815-2099+)
- Daily mood logging (5 levels)
- Journal notes with mood
- Calendar view
- Trend visualization
- Pattern analysis

#### 7. PDF Generation (Lines 1104-1291)
- ReportLab-based PDF creation
- Wellness report formatting
- Assessment summary tables

---

## Target Architecture

### Tech Stack

```
Frontend:
├── Next.js 14 (App Router)
├── TypeScript
├── Tailwind CSS
├── shadcn/ui components
├── Zustand (state management)
└── React Query (data fetching)

Backend:
├── Next.js API Routes (serverless)
├── Supabase (Auth + Database)
└── Groq SDK (LLM)

Infrastructure:
├── Vercel (hosting)
├── Supabase (BaaS)
└── GitHub (CI/CD)
```

### Project Structure

```
animoa-next/
├── app/
│   ├── layout.tsx                 # Root layout with providers
│   ├── page.tsx                   # Landing/auth page
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx             # Dashboard layout with sidebar
│   │   ├── chat/
│   │   │   ├── page.tsx           # Chat interface
│   │   │   └── [sessionId]/page.tsx
│   │   ├── mood/page.tsx          # Mood tracker
│   │   ├── assessment/page.tsx    # Mental health advisory
│   │   └── profile/page.tsx       # User profile
│   └── api/
│       ├── chat/route.ts          # Chat endpoint (streaming)
│       ├── mood/route.ts          # Mood CRUD
│       ├── assessment/
│       │   ├── route.ts           # Assessment CRUD
│       │   └── recommendations/route.ts
│       └── pdf/route.ts           # PDF generation
├── components/
│   ├── ui/                        # shadcn components
│   ├── chat/
│   │   ├── ChatWindow.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── ChatInput.tsx
│   │   ├── SessionList.tsx
│   │   └── FeedbackButtons.tsx
│   ├── mood/
│   │   ├── MoodPicker.tsx
│   │   ├── MoodCalendar.tsx
│   │   └── MoodChart.tsx
│   ├── assessment/
│   │   ├── QuestionnaireForm.tsx
│   │   ├── RecommendationsCard.tsx
│   │   └── AssessmentHistory.tsx
│   ├── crisis/
│   │   └── CrisisAlert.tsx
│   └── common/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── LoadingSpinner.tsx
├── lib/
│   ├── supabase/
│   │   ├── client.ts              # Browser client
│   │   ├── server.ts              # Server client
│   │   └── middleware.ts          # Auth middleware
│   ├── groq.ts                    # Groq client
│   ├── crisis-detection.ts        # Crisis keyword logic
│   ├── pdf-generator.ts           # PDF creation (jsPDF or @react-pdf/renderer)
│   └── utils.ts
├── hooks/
│   ├── useChat.ts
│   ├── useMood.ts
│   └── useAssessment.ts
├── store/
│   └── useStore.ts                # Zustand store
├── types/
│   └── index.ts                   # TypeScript types
├── middleware.ts                  # Next.js middleware for auth
├── tailwind.config.ts
├── next.config.js
└── package.json
```

---

## Migration Phases

### Phase 1: Foundation (Week 1) - COMPLETED
- [x] Initialize Next.js 14 project with TypeScript
- [x] Set up Tailwind CSS and shadcn/ui
- [x] Configure Supabase client (reuse existing project)
- [x] Set up environment variables
- [x] Create basic layout and routing structure
- [x] Implement authentication (login/signup)
- [ ] Deploy skeleton to Vercel

### Phase 2: Core Chat (Week 2) - COMPLETED
- [x] Create chat UI components
- [x] Implement Groq API route with streaming
- [x] Build chat session management
- [x] Migrate crisis detection (English only)
- [x] Add message persistence
- [x] Implement feedback system

### Phase 3: Assessment & Mood (Week 3) - COMPLETED
- [x] Build questionnaire form component
- [x] Create recommendations API route
- [x] Implement assessment history
- [x] Build mood tracker UI
- [x] Create mood calendar visualization
- [x] Add mood trends chart

### Phase 4: Polish & PDF (Week 4) - COMPLETED
- [x] Implement PDF generation (jsPDF)
- [x] User profile management
- [x] Error handling and loading states
- [x] Mobile responsiveness
- [ ] Performance optimization
- [ ] Final testing and bug fixes

---

## Feature Migration Checklist

### Authentication
- [x] Login form with email/password
- [x] Signup form with password confirmation
- [ ] Forgot password flow
- [x] Protected routes middleware
- [x] Session persistence

### Profile
- [x] Full name input
- [x] Age input (min: 13)
- [x] Stress level selector (Low/Moderate/High/Very High)
- [x] Goals textarea
- [x] Interests textarea
- [x] Save/update functionality

### Chat
- [x] Real-time message display
- [x] Message streaming from Groq
- [x] Multiple chat sessions
- [x] Session switching
- [x] New chat creation
- [x] Chat deletion with confirmation
- [x] Message history loading
- [x] Feedback emoji buttons
- [x] Crisis keyword detection
- [x] Crisis resources display (English)

### Assessment
- [x] PHQ-2 questions (mood, interest)
- [x] GAD-2 questions (anxiety, worry)
- [x] Sleep quality question
- [x] Social support question
- [x] Coping strategies textarea
- [x] Form validation
- [x] AI recommendation generation
- [x] Recommendation display
- [x] PDF download
- [x] Assessment history list
- [x] View past assessment
- [x] Delete assessment

### Mood Tracker
- [x] 5-level mood picker (emoji buttons)
- [x] Journal note textarea
- [x] Save mood entry
- [x] Edit today's mood
- [x] Calendar view (week/month)
- [x] Trend line chart
- [x] Pattern insights

### PDF Generation
- [x] Wellness report header
- [x] Assessment summary table
- [x] Recommendations section
- [x] Disclaimer footer
- [x] Download functionality

---

## Database Schema

Reusing existing Supabase tables:

```sql
-- profiles (existing)
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  email TEXT,
  full_name TEXT,
  age INTEGER,
  stress_level TEXT,
  goals TEXT,
  interests TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- chat_sessions (existing)
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  title TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- chat_history (existing)
CREATE TABLE chat_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  session_id UUID REFERENCES chat_sessions(id),
  message TEXT,
  sender TEXT, -- 'user', 'bot', 'feedback'
  feedback_for_message_index INTEGER,
  timestamp TIMESTAMP DEFAULT NOW()
);

-- questionnaire_responses (existing)
CREATE TABLE questionnaire_responses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  responses JSONB,
  recommendations TEXT,
  used_chat_history BOOLEAN,
  created_at TIMESTAMP DEFAULT NOW()
);

-- mood_logs (existing)
CREATE TABLE mood_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  date DATE,
  mood TEXT,
  note TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Migration Note**: Remove `preferred_language` column from profiles table (optional cleanup).

---

## API Routes Design

### POST /api/chat
Stream chat responses from Groq.

```typescript
// Request
{
  message: string;
  sessionId: string;
  conversationHistory: Message[];
}

// Response: Server-Sent Events stream
```

### GET/POST /api/mood
Mood tracking CRUD.

```typescript
// GET: Fetch mood logs for date range
// POST: Create/update mood entry
{
  date: string;
  mood: 'very_happy' | 'happy' | 'neutral' | 'sad' | 'very_sad';
  note?: string;
}
```

### POST /api/assessment
Create assessment and get recommendations.

```typescript
// Request
{
  responses: {
    mood: string;
    interest: string;
    anxiety: string;
    worry: string;
    sleep: string;
    support: string;
    coping: string;
  };
  includeHistory?: boolean;
}

// Response
{
  id: string;
  recommendations: string;
}
```

### POST /api/pdf
Generate wellness report PDF.

```typescript
// Request
{
  assessmentId: string;
}

// Response: PDF binary
```

---

## Component Architecture

### ChatWindow Component

```typescript
interface ChatWindowProps {
  sessionId: string;
}

// Features:
// - Displays message list
// - Handles message input
// - Triggers crisis detection
// - Shows loading states
// - Supports message streaming
```

### MoodPicker Component

```typescript
interface MoodPickerProps {
  selectedMood?: MoodType;
  onSelect: (mood: MoodType) => void;
}

// Features:
// - 5 emoji buttons in a row
// - Visual feedback for selection
// - Animated hover states
```

### CrisisAlert Component

```typescript
interface CrisisAlertProps {
  isVisible: boolean;
  onDismiss: () => void;
}

// Features:
// - Full-screen modal or prominent banner
// - Crisis hotline numbers (English/US)
// - Calming design
// - Dismissible but prominent
```

---

## MCP Server Integration Ideas

MCP (Model Context Protocol) servers could enhance Animoa in several ways:

### 1. Memory/Context MCP Server
**Purpose**: Persistent memory across sessions for deeper personalization.

```
User: "I mentioned my dog Max last week..."
Animoa: "Yes, you shared that Max helps with your anxiety. How's he doing?"
```

**Implementation**: MCP server stores key facts, preferences, and conversation summaries that persist beyond chat sessions.

### 2. Calendar/Scheduling MCP Server
**Purpose**: Integration with user's calendar for contextual awareness.

```
Animoa: "I notice you have a job interview tomorrow. Would you like to
do a quick anxiety-relief exercise to prepare?"
```

**Implementation**: MCP server connects to Google Calendar/Outlook to understand user's upcoming events.

### 3. Health Data MCP Server
**Purpose**: Connect with fitness trackers/health apps for holistic insights.

```
Animoa: "Your sleep tracker shows you've been getting less sleep this week.
This might be connected to the stress you mentioned. Let's work on sleep hygiene."
```

**Implementation**: MCP server integrates with Apple Health, Fitbit, or similar APIs.

### 4. Journal/Notes MCP Server
**Purpose**: Access to user's personal notes/journal for deeper context.

**Implementation**: MCP server reads from Notion, Obsidian, or local markdown files.

### 5. Resource Library MCP Server
**Purpose**: Curated mental health resources, exercises, and content.

```
Animoa: "Based on your anxiety patterns, here's a 5-minute breathing
exercise from our library that's helped users with similar concerns."
```

**Implementation**: MCP server provides access to a structured database of exercises, articles, and techniques.

---

## Personalization Enhancement Ideas

### Current Approach (v7)
The current app uses profile data (age, stress level, goals, interests) to customize LLM prompts.

### Enhanced Personalization Brainstorm

#### 1. Conversation Pattern Analysis
- Track common topics user discusses
- Identify emotional triggers
- Note time-of-day patterns (e.g., user often anxious at night)

```typescript
interface UserPatterns {
  frequentTopics: string[];        // ['work', 'relationships', 'sleep']
  emotionalTriggers: string[];     // ['deadline', 'conflict', 'uncertainty']
  peakAnxietyTimes: string[];      // ['22:00-00:00', 'Monday mornings']
  preferredCopingMethods: string[]; // ['breathing', 'journaling', 'walking']
  responsePreference: 'concise' | 'detailed' | 'questions';
}
```

#### 2. Adaptive Response Style
- Learn if user prefers questions vs. advice
- Adjust formality based on user's language patterns
- Match energy level (upbeat vs. calm)

#### 3. Progress Tracking Integration
- Reference mood trends in conversations
- Celebrate improvements
- Gently address declining patterns

```
Animoa: "I noticed your mood has been improving over the past week!
What do you think has been helping?"
```

#### 4. Contextual Prompting
- Use recent assessment data in chat
- Reference previous conversations
- Connect current conversation to past insights

```typescript
const enhancedSystemPrompt = `
You are Animoa. Here's what you know about this user:

PROFILE:
- Name: ${profile.fullName}
- Stress Level: ${profile.stressLevel}
- Goals: ${profile.goals}

RECENT PATTERNS:
- Mood trend: ${moodTrend}  // 'improving', 'stable', 'declining'
- Last assessment showed: ${lastAssessment.summary}
- Common topics: ${patterns.frequentTopics.join(', ')}

CONVERSATION STYLE:
- User prefers: ${patterns.responsePreference} responses
- Energy match: ${determineEnergyLevel(recentMessages)}

Use this context to provide personalized, relevant support.
`;
```

#### 5. Smart Follow-ups
- Remember unfinished topics
- Check in on previously mentioned concerns
- Track commitments and gently follow up

```
Animoa: "Last time you mentioned trying the morning meditation.
How did that go?"
```

#### 6. Personalized Resource Recommendations
- Match exercises to user's preferences
- Suggest content based on patterns
- Learn what resonates and what doesn't

---

## Deployment Strategy

### Environment Variables (Vercel)

```env
# Supabase (reuse existing)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# Groq
GROQ_API_KEY=your_groq_api_key
```

### Vercel Configuration

```json
// vercel.json
{
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "NODE_ENV": "production"
  }
}
```

### CI/CD Flow

```
Push to main → Vercel auto-deploys → Production
Push to dev  → Vercel preview deploy → Testing
```

---

## Future Evolution Path

### Phase 1: MVP (Current Plan)
- Core features migrated
- English only
- Vercel free tier

### Phase 2: Enhanced Personalization
- Implement conversation pattern analysis
- Add adaptive response styles
- Smart follow-ups

### Phase 3: MCP Integration
- Memory server for persistent context
- Resource library server

### Phase 4: Scale (If Needed)
- Upgrade Vercel plan
- Add Redis caching
- Multi-region deployment
- Consider dedicated database

### Phase 5: Platform Expansion
- Mobile app (React Native, shared components)
- API for third-party integrations
- Enterprise/therapist dashboard

---

## Development Commands

```bash
# Initialize project
npx create-next-app@latest animoa-next --typescript --tailwind --eslint --app --src-dir=false

# Add dependencies
npm install @supabase/supabase-js @supabase/ssr groq-sdk zustand @tanstack/react-query

# Add shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input textarea dialog alert

# Add PDF generation
npm install jspdf jspdf-autotable
# OR
npm install @react-pdf/renderer

# Development
npm run dev

# Build
npm run build

# Deploy (auto via Vercel)
git push origin main
```

---

## Notes

- **Translations Removed**: All multi-language code (TRANSLATIONS dict, language selectors, translate_messages function) will not be migrated
- **Existing Database**: Reuse the same Supabase project - no data migration needed
- **Groq API**: Same API key and model (llama-3.3-70b-versatile)
- **Crisis Resources**: English-only (US hotlines: 988, 741741)

---

*Last Updated: January 21, 2026*
