# Animoa

A mental health companion that provides AI-powered conversations, validated wellness assessments, mood tracking, and personalized wellness reports.

## Features

- **AI Chat** - Empathetic conversations powered by Groq LLM with crisis detection and multi-session support
- **Wellness Assessments** - PHQ-2 and GAD-2 validated screening tools with AI-generated recommendations
- **Mood Tracker** - Daily emoji-based logging with calendar visualization and trend analytics
- **PDF Reports** - Downloadable professional wellness reports
- **Multi-Language** - English, Spanish, and Mandarin Chinese
- **Crisis Safety** - Detects distress signals and surfaces emergency resources (988, Crisis Text Line)

## Tech Stack

- **Streamlit** - Web UI
- **Groq** - LLM API (llama-3.3-70b-versatile)
- **Supabase** - Auth + PostgreSQL
- **ReportLab** - PDF generation
- **Python 3.11+**

## Quick Start

```bash
git clone https://github.com/Swargambharath987/Project_Animoa.git
cd Project_Animoa
pip install -r requirements.txt
```

Create a `.env` file:

```env
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
GROQ_API_KEY=your-groq-api-key
```

Run:

```bash
streamlit run main_app_v7.py
```

App runs at `http://localhost:8501`.

## Docker

```bash
docker compose up --build
```

## Database Setup

Set up the required tables in your Supabase SQL Editor. The schema includes `profiles`, `chat_sessions`, `chat_history`, `mood_logs`, and `questionnaire_responses`. See [CLAUDE.md](./CLAUDE.md#database-schema) for the complete SQL schema and RLS policies.

## Project Structure

```
main_app_v7.py       # Production app (v7)
translations.py      # UI translations (EN/ES/ZH)
Dockerfile           # Container config
archive/             # Previous versions (v1-v6)
animoa-next/         # Next.js version
```

## Next.js Version

A modern rewrite is available in [`animoa-next/`](./animoa-next/) with server-side rendering, streaming AI responses, and a refreshed UI. Deployed on Vercel.

## Version History

Seven iterations from a 152-line prototype to a 2,662-line application. See [VERSION_HISTORY.md](./VERSION_HISTORY.md) for details.

## Disclaimer

Animoa is an AI companion, not a substitute for professional mental health care. If you are in crisis, call or text **988** (Suicide & Crisis Lifeline) or text **HOME** to **741741** (Crisis Text Line).
