# VERSION HISTORY - Animoa Development Journey

> Documentation of Animoa's iterative development from basic chatbot to comprehensive mental health companion

---

## Overview

This document chronicles the evolution of Animoa through 7 major versions, growing from a simple 152-line chatbot prototype to a feature-rich 2,662-line mental health companion application. Each version represents a significant milestone in functionality, user experience, and technical capability.

**Current Production Version**: `main_app_v7.py` (located in root directory)
**Archived Versions**: `archive/` directory contains v1-v6 for reference

---

## Version Timeline

| Version | Lines of Code | Release Focus | File Location |
|---------|---------------|---------------|---------------|
| v1 | 152 | Basic Chat | `archive/v1_main_app.py` |
| v2 | 515 | Profiles & Assessments | `archive/v2_main_app.py` |
| v3 | 1,015 | Multi-language Support | `archive/v3_main_app.py` |
| v4 | 1,209 | Chat Sessions & Feedback | `archive/v4_main_app.py` |
| v5 | 1,327 | Code Refactoring & UI | `archive/v5_main_app.py` |
| v6 | 1,510 | Mood Tracking | `archive/v6_main_app.py` |
| v7 | 2,662 | **Current - Analytics & Reports** | `main_app_v7.py` |

---

## Detailed Version History

### Version 1 - Foundation (152 lines)
**File**: `archive/v1_main_app.py`
**Focus**: Basic mental health chatbot prototype

#### Key Features:
- ✅ Groq LLM API integration (`qwen-2.5-32b` model initially)
- ✅ Supabase authentication (login/signup)
- ✅ In-memory chat history
- ✅ Empathetic system prompts for mental health support
- ✅ Simple Streamlit UI

#### Database Schema:
- `auth.users` (Supabase built-in)

#### Limitations:
- No persistent chat history
- No user profiles
- Single language only (English)
- No structured assessments

---

### Version 2 - User Profiles & Wellness Advisory (515 lines, +239%)
**File**: `archive/v2_main_app.py`
**Focus**: Personalization and evidence-based assessments

#### Major Additions:
- 🆕 **User Profile Management**: Full CRUD for personal details
  - Name, age, date of birth
  - Stress level tracking
  - Mental wellness goals
  - Interests and activities
- 🆕 **Mental Health Advisory Module**: Validated screening tools
  - PHQ-2 (depression screening)
  - GAD-2 (anxiety screening)
  - AI-generated personalized recommendations
- 🆕 **Persistent Chat History**: Database storage of conversations
- 🆕 **CSV Download**: Export recommendations for offline use

#### Database Schema Added:
```sql
profiles (id, email, full_name, age, dob, stress_level, goals, interests)
chat_history (id, user_id, message, sender, timestamp)
questionnaire_responses (id, user_id, responses, recommendations, created_at)
```

#### Technical Improvements:
- Structured data models
- Enhanced error handling
- Supabase database integration

---

### Version 3 - Internationalization (1,015 lines, +97%)
**File**: `archive/v3_main_app.py`
**Focus**: Multi-language support for global accessibility

#### Major Additions:
- 🆕 **Multi-language Support**: 3 languages
  - English (EN)
  - Spanish (ES)
  - Mandarin Chinese (ZH)
- 🆕 **Comprehensive UI Translation**: 80+ translation keys
  - All buttons, labels, and messages
  - Dynamic language switching
  - Embedded translation dictionary
- 🆕 **Language-aware AI**: LLM responds in user's preferred language
- 🆕 **Localized Questionnaires**: Multi-language assessment forms

#### Database Schema Changes:
```sql
ALTER TABLE profiles ADD COLUMN preferred_language TEXT DEFAULT 'en';
```

#### UI Improvements:
- Language selector on login page
- Column-based layout for better visual hierarchy
- Language persistence across sessions

---

### Version 4 - Session Management & Feedback (1,209 lines, +19%)
**File**: `archive/v4_main_app.py`
**Focus**: Multi-conversation support and user feedback

#### Major Additions:
- 🆕 **Chat Sessions Management**: Multiple separate conversations
  - Create new chat sessions
  - Browse session history
  - Session titles and metadata
- 🆕 **Message-level Feedback System**:
  - Thumbs up/down rating for bot responses
  - Feedback persistence in database
- 🆕 **Conversation Translation**: Translate entire chat history using LLM
- 🆕 **Enhanced Chat Interface**: Two-column layout
  - Left: Session browser/selector
  - Right: Active conversation

#### Database Schema Added:
```sql
chat_sessions (id, user_id, title, created_at)
ALTER TABLE chat_history ADD COLUMN session_id UUID;
ALTER TABLE chat_history ADD COLUMN feedback_for_message_index INTEGER;
```

#### UX Improvements:
- Sidebar session list
- Improved navigation
- Better conversation organization

---

### Version 5 - Code Quality & Infrastructure (1,327 lines, +10%)
**File**: `archive/v5_main_app.py`
**Focus**: Refactoring, maintainability, and infrastructure

#### Major Additions:
- 🆕 **External Translations Module**: `translations.py`
  - Separated translations from main codebase
  - `@st.cache_data` decorator for performance
  - Easier translation management
- 🆕 **About Section**: Comprehensive app documentation
  - Feature descriptions
  - Usage instructions
  - Important disclaimers
- 🆕 **Logout Feedback Form**: Exit survey for user insights
- 🆕 **PDF Generation Infrastructure**: ReportLab integration
- 🆕 **Custom CSS Styling**:
  - Branded color scheme (teal/blue theme #4E9BB9)
  - Button hover states
  - Alert styling
  - Visual consistency

#### Technical Improvements:
- Modular code architecture
- `AuthRetryableError` detection
- Enhanced page configuration
- Collapsible sidebar
- Better error messages

#### Database Schema:
- No changes (infrastructure-focused release)

---

### Version 6 - Mood Tracking (1,510 lines, +14%)
**File**: `archive/v6_main_app.py`
**Focus**: Daily emotional wellness monitoring

#### Major Additions:
- 🆕 **Mood Tracker Feature**:
  - Daily emoji-based mood logging (😊 → 😢)
  - 5 emotion levels: Very Happy, Happy, Neutral, Sad, Very Sad
  - Optional mood notes/journal entries
- 🆕 **Mood History Display**: 7-day mood timeline
- 🆕 **Mood Entry Editing**: Modify past mood logs
- 🆕 **Session Deletion**: Users can delete conversations
- 🆕 **Enhanced Feedback Collection**: Improved feedback mechanisms

#### Database Schema Added:
```sql
mood_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID,
    date DATE,
    mood TEXT,
    note TEXT,
    timestamp TIMESTAMP,
    UNIQUE(user_id, date)
)
```

#### Features:
- Date validation (prevent future mood logging)
- Unique constraint (one mood per day)
- Simple list-based mood visualization

---

### Version 7 - Analytics & Professional Reports (2,662 lines, +76%) ⭐ CURRENT
**File**: `main_app_v7.py` (root directory)
**Focus**: Advanced analytics, visualizations, and professional reporting

#### Major Additions:
- 🆕 **Professional PDF Wellness Reports**:
  - ReportLab-styled document generation
  - Formatted headers, sections, and typography
  - Comprehensive assessment summaries
  - Downloadable wellness insights
- 🆕 **Calendar-based Mood Visualization**:
  - HTML/CSS calendar grid with emoji display
  - Visual monthly mood patterns
  - Color-coded mood indicators
- 🆕 **Comprehensive Mood Analytics**:
  - Mood statistics and trends
  - Multiple view modes (list, calendar, stats)
  - Historical mood tracking
- 🆕 **Enhanced Recommendations Engine**:
  - Integrates mood data into AI recommendations
  - Contextual wellness advice
  - Evidence-based suggestions
- 🆕 **Button-based Navigation**: Improved menu system
- 🆕 **Complete UI Redesign**:
  - Professional styling throughout
  - Enhanced About section with full feature docs
  - Improved profile management interface
  - Refined chat message display

#### Database Schema Enhancements:
- Optimized indexing on `user_id` and `created_at`
- Better query performance
- Enhanced data validation

#### Technical Improvements:
- Switched to `llama-3.3-70b-versatile` model (from `qwen-2.5-32b`)
- Advanced error handling
- Improved session state management
- Professional-grade PDF generation
- Enhanced security practices

#### Feature Completeness:
✅ AI-powered conversations
✅ Mental health assessments (PHQ-2, GAD-2)
✅ User profiles with preferences
✅ Multi-language support (EN/ES/ZH)
✅ Session management
✅ Mood tracking with calendar
✅ Analytics and insights
✅ PDF report generation
✅ Feedback system
✅ About/documentation

---

## Database Schema Evolution

### Complete Schema (v7)

```sql
-- User authentication (Supabase built-in)
auth.users (id, email, encrypted_password, created_at, ...)

-- User profiles
profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email TEXT,
    full_name TEXT,
    age INTEGER,
    stress_level TEXT,
    goals TEXT,
    interests TEXT,
    preferred_language TEXT DEFAULT 'en'
)

-- Chat sessions
chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    title TEXT,
    created_at TIMESTAMP DEFAULT NOW()
)

-- Chat history
chat_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    session_id UUID REFERENCES chat_sessions(id),
    message TEXT,
    sender TEXT CHECK (sender IN ('user', 'bot', 'feedback')),
    timestamp TIMESTAMP DEFAULT NOW(),
    feedback_for_message_index INTEGER
)

-- Mood tracking
mood_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    date DATE,
    mood TEXT,
    note TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
)

-- Wellness assessments
questionnaire_responses (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    responses JSONB,
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT NOW()
)
```

---

## Technology Stack Evolution

### External Dependencies (requirements.txt)

| Version | Libraries Added |
|---------|----------------|
| v1 | streamlit, supabase, python-dotenv, groq |
| v2 | (no new deps, schema-focused) |
| v3 | (translations embedded in code) |
| v4 | (session management via DB) |
| v5 | reportlab (PDF generation) |
| v6 | (mood tracking via DB) |
| v7 | (enhanced ReportLab usage) |

**Final Stack**:
- Streamlit (UI framework)
- Groq (LLM API - `llama-3.3-70b-versatile`)
- Supabase (Authentication + PostgreSQL database)
- ReportLab (PDF generation)
- Python-dotenv (Environment variables)

---

## Key Milestones & Learnings

### Phase 1: Foundation (v1)
**Learning**: Basic AI chatbot structure, API integration, authentication flow

### Phase 2: Data & Personalization (v2)
**Learning**: Database design, user profiles, structured assessments, CRUD operations

### Phase 3: Accessibility (v3)
**Learning**: Internationalization, multi-language AI prompts, UI localization

### Phase 4: User Experience (v4-v5)
**Learning**: Session management, user feedback loops, code organization, UI/UX design

### Phase 5: Feature Richness (v6-v7)
**Learning**: Data visualization, analytics, professional reporting, comprehensive mental health platform

---

## Development Metrics

| Metric | v1 → v7 Growth |
|--------|----------------|
| Lines of Code | 152 → 2,662 (1,651% increase) |
| Features | 3 → 10+ major features |
| Database Tables | 1 → 6 tables |
| Languages Supported | 1 → 3 languages |
| UI Components | Basic → Professional |
| File Size | 6KB → 127KB |

---

## Archive Access

All previous versions are preserved in the `archive/` directory:

```
archive/
├── foundation_chatbot.py    # Early prototype (reference only)
├── v1_main_app.py           # Version 1: Basic chat
├── v2_main_app.py           # Version 2: Profiles & assessments
├── v3_main_app.py           # Version 3: Multi-language
├── v4_main_app.py           # Version 4: Sessions & feedback
├── v5_main_app.py           # Version 5: Refactoring & UI
└── v6_main_app.py           # Version 6: Mood tracking
```

**Note**: Each archived file contains a header comment indicating its archived status and key features introduced in that version.

---

## Future Development Considerations

Potential areas for v8 and beyond:
- Crisis detection and resource links
- Integration with wearable devices
- Group chat/support communities
- Therapist dashboard for monitoring
- Advanced analytics (sentiment analysis, trend prediction)
- Mobile app (React Native/Flutter)
- Voice interaction capability
- Integration with calendar apps for mood reminders

---

*This version history demonstrates the iterative development process and continuous improvement philosophy behind Animoa's evolution from concept to comprehensive mental health companion.*

**Last Updated**: November 17, 2025
**Current Version**: v7 (main_app_v7.py)
**Repository**: https://github.com/Swargambharath987/Project_Animoa
