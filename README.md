# Animoa

A mental health companion web app with AI-powered conversations, validated wellness assessments, mood tracking, and personalized recommendations.

## Features

- **AI Chat** — Empathetic conversations powered by Groq LLM with streaming responses and crisis detection
- **Wellness Assessments** — PHQ-2 and GAD-2 validated screening tools with AI-generated recommendations
- **Mood Tracker** — Daily emoji-based logging with calendar visualization and trend charts
- **RAG-Enhanced Responses** — Evidence-based mental health techniques retrieved from a curated knowledge base
- **PDF Reports** — Downloadable wellness reports
- **Crisis Safety** — Detects distress signals and surfaces emergency resources (988, Crisis Text Line)

## Tech Stack

- **Next.js 14** — App Router, server-side rendering
- **TypeScript** — Strict mode
- **Tailwind CSS** — Styling with custom Animoa brand colors
- **Supabase** — Auth, PostgreSQL, pgvector (RAG)
- **Groq** — LLM API (Llama 3.3 70B Versatile)
- **HuggingFace** — Embedding API for RAG (bge-small-en-v1.5)

## Quick Start

```bash
git clone https://github.com/Swargambharath987/Project_Animoa.git
cd Project_Animoa
npm install
```

Copy `.env.example` to `.env.local` and fill in your keys:

```bash
cp .env.example .env.local
```

Run the dev server:

```bash
npm run dev
```

App runs at `http://localhost:3000`.

## Docker

```bash
docker compose up --build
```

## Project Structure

```
app/           # Next.js routes and API endpoints
components/    # React components (chat, mood, assessment, crisis)
lib/           # Utilities (groq, rag, embeddings, supabase, crisis-detection)
types/         # TypeScript interfaces
docs/          # Planning docs and development log
archive/       # Old Streamlit MVP (v1–v7)
public/        # Static assets (logo)
```

## Disclaimer

Animoa is an AI companion, not a substitute for professional mental health care. If you are in crisis, call or text **988** (Suicide & Crisis Lifeline) or text **HOME** to **741741** (Crisis Text Line).
