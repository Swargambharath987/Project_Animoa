# CLAUDE.md - AI Assistant Guide for Animoa

> Comprehensive guide for AI assistants working with the Animoa mental health companion application

## Table of Contents
1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Architecture & Tech Stack](#architecture--tech-stack)
4. [Development Workflow](#development-workflow)
5. [Code Conventions](#code-conventions)
6. [Key Files & Modules](#key-files--modules)
7. [Database Schema](#database-schema)
8. [API Integrations](#api-integrations)
9. [Session State Management](#session-state-management)
10. [Testing & Deployment](#testing--deployment)
11. [Common Tasks](#common-tasks)
12. [Important Notes](#important-notes)

---

## Project Overview

**Animoa** is a mental health companion web application built with Streamlit that provides:
- AI-powered empathetic conversations using Groq LLM
- Mental wellness assessments (PHQ-2, GAD-2 validated screening tools)
- Personal mood tracking with calendar visualization
- User profile management with language preferences
- Multi-language support (English, Spanish, Mandarin Chinese)
- Secure authentication and data persistence via Supabase

**Target Users**: Individuals seeking mental wellness support through accessible, conversational AI
**Purpose**: Provide a safe, judgment-free space for mental health conversations and personalized insights

---

## Repository Structure

```
Project_Animoa/
├── .devcontainer/
│   └── devcontainer.json          # Dev container config for Codespaces/VS Code
├── .git/                          # Git repository metadata
├── main_app_v7.py                 # ⭐ CURRENT PRODUCTION VERSION
├── main_app_v6.py                 # Previous version
├── main_app_v5.py                 # Previous version
├── main_app_v4.py                 # Previous version
├── main_app_v3.py                 # Previous version
├── main_app_v2.0.py               # Previous version
├── main_app.py                    # Original version
├── foundation_chatbot.py          # Early chatbot prototype
├── translations.py                # Multi-language translations (EN, ES, ZH)
├── requirements.txt               # Python dependencies
├── logo.png                       # Application logo
├── README.md                      # User-facing documentation
├── Animoa_Brochure.pdf           # Marketing/project brochure
└── Capstone_Project_Animoa_12May'25.pptx.pdf  # Project presentation
```

### Version History Notes
- **main_app_v7.py**: Latest version with full feature set (mood tracking, feedback, PDF generation)
- Previous versions (v2-v6): Incremental feature additions (keep for reference)
- **foundation_chatbot.py**: Minimal chatbot prototype using Groq API

---

## Architecture & Tech Stack

### Core Technologies

| Technology | Purpose | Version/Notes |
|------------|---------|---------------|
| **Streamlit** | Web framework & UI | Primary interface layer |
| **Groq** | LLM API for AI responses | Model: `llama-3.3-70b-versatile` |
| **Supabase** | Authentication & database | PostgreSQL backend |
| **ReportLab** | PDF generation | For wellness reports |
| **Pandas** | Data manipulation | Mood tracking analytics |
| **Python** | Programming language | 3.11+ (per devcontainer) |

### Application Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                    │
│  (Page Config, CSS Theming, Navigation, Session State)  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼─────────┐      ┌───────▼────────┐
│   Groq API      │      │   Supabase     │
│  (LLM Calls)    │      │  (Auth & DB)   │
└─────────────────┘      └────────────────┘
        │                         │
        │ Responses              │ User Data
        │                         │
┌───────▼─────────────────────────▼────────┐
│         Application Features              │
│  • Chat (MentalHealthChatbot class)      │
│  • Wellness Advisory                      │
│  • Mood Tracker                           │
│  • Profile Management                     │
│  • Authentication Flow                    │
└───────────────────────────────────────────┘
```

---

## Development Workflow

### Environment Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/Swargambharath987/Project_Animoa.git
   cd Project_Animoa
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file in project root:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   GROQ_API_KEY=your-groq-api-key
   ```

4. **Run Application**
   ```bash
   streamlit run main_app_v7.py
   ```
   App will be available at `http://localhost:8501`

### Development Container (Codespaces/VS Code)

The `.devcontainer/devcontainer.json` provides:
- Python 3.11 environment
- Auto-install dependencies on container creation
- Automatic Streamlit server startup
- Port 8501 forwarding with preview

**Note**: Update `devcontainer.json` line 22 to use `main_app_v7.py` instead of `main_app_v6.py`

---

## Code Conventions

### File Naming
- Main application versions: `main_app_v{X}.py` (increment version for major changes)
- Keep previous versions for rollback capability
- Use descriptive names for utility modules (e.g., `translations.py`)

### Code Style
- **Indentation**: 4 spaces (Python standard)
- **Imports**: Group by standard library → third-party → local modules
- **Functions**: Snake_case naming (e.g., `generate_recommendations()`)
- **Classes**: PascalCase naming (e.g., `MentalHealthChatbot`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `SUPABASE_URL`)

### Streamlit Conventions
- Set page config as **first Streamlit command** (before any other st calls)
- Use `st.session_state` for all stateful data
- Apply custom CSS via `st.markdown(..., unsafe_allow_html=True)`
- Use `@st.cache_data` for expensive operations (e.g., translation loading)

### AI Response Patterns
- Use **system prompts** to set empathetic, supportive tone
- Include language in system prompt for multilingual responses
- Temperature: 0.7 (balanced between creativity and consistency)
- Max tokens: 300 for chat, 800 for recommendations
- Always handle API errors gracefully with fallback messages

---

## Key Files & Modules

### main_app_v7.py (Current Production)

**Primary Sections:**
1. **Page Configuration** (lines 1-91): Theme, CSS, imports
2. **Helper Functions** (lines 93-310): API key retrieval, auth UI, profile management
3. **MentalHealthChatbot Class** (lines 429-1020): Core chat functionality
4. **Wellness Advisory** (lines 1210-1730): PHQ-2/GAD-2 questionnaires
5. **Mood Tracker** (lines 1732-2347): Daily mood logging
6. **Feedback System** (lines 2349-2418): Logout feedback collection
7. **About Section** (lines 2420-2534): App information
8. **Main Function** (lines 2536+): Navigation and routing

**Key Functions:**

| Function | Purpose | Location |
|----------|---------|----------|
| `get_api_key(key_name)` | Retrieve API keys from .env or secrets | Line 117 |
| `auth_ui(supabase)` | Login/signup interface | Line 139 |
| `ensure_profile_exists(user_id, email)` | Create default profile on signup | Line 295 |
| `profile_manager(supabase)` | User profile CRUD | Line 312 |
| `generate_recommendations(responses, chat_history)` | AI wellness insights | Line 1587 |
| `create_wellness_pdf(responses, recommendations)` | PDF generation | Line 1022 |
| `mood_tracker()` | Mood logging interface | Line 1732 |
| `show_logout_feedback_form()` | Collect feedback on logout | Line 2349 |

### translations.py

**Purpose**: Multi-language support for UI strings

**Structure:**
```python
@st.cache_data
def load_translations():
    return {
        "en": {...},  # English translations
        "es": {...},  # Spanish translations
        "zh": {...}   # Mandarin Chinese translations
    }
```

**Usage Pattern:**
```python
t = load_translations()[st.session_state.language]
st.write(t["welcome_message"])
```

**Translation Keys**: 80+ keys covering all UI elements (buttons, labels, messages)

### foundation_chatbot.py

**Purpose**: Early chatbot prototype (reference only)

**Key Differences from main_app_v7.py:**
- No authentication
- Simpler chat interface
- No database persistence
- Uses `qwen-2.5-32b` model (vs `llama-3.3-70b-versatile`)
- No multi-language support

---

## Database Schema

### Supabase Tables

#### 1. profiles
```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email TEXT,
    full_name TEXT,
    age INTEGER,
    stress_level TEXT,
    goals TEXT,
    interests TEXT,
    preferred_language TEXT DEFAULT 'en'
);
```

**Access Pattern**: One-to-one with auth.users

#### 2. chat_sessions
```sql
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    title TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Access Pattern**: One user → Many sessions

#### 3. chat_history
```sql
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    session_id UUID REFERENCES chat_sessions(id),
    message TEXT,
    sender TEXT CHECK (sender IN ('user', 'bot', 'feedback')),
    timestamp TIMESTAMP DEFAULT NOW(),
    feedback_for_message_index INTEGER
);
```

**Access Pattern**: One session → Many messages

#### 4. mood_logs
```sql
CREATE TABLE mood_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    date DATE,
    mood TEXT,  -- mood_key from mood_emojis
    note TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);
```

**Access Pattern**: One user → Many daily mood logs

#### 5. questionnaire_responses
```sql
CREATE TABLE questionnaire_responses (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    responses JSONB,  -- {mood, interest, anxiety, worry, sleep, support, coping, language}
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Access Pattern**: One user → Many assessments

### Data Access Patterns

**Best Practices:**
- Always filter by `user_id` for user-specific data
- Use `.order('created_at', desc=True)` for chronological data
- Handle Supabase errors with try-except blocks
- Refresh tokens on `AuthRetryableError`

---

## API Integrations

### Groq API

**Configuration:**
```python
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
```

**Model**: `llama-3.3-70b-versatile`
- Open-source LLM optimized for speed
- 70B parameters (strong reasoning capability)
- Cost-effective (free tier available)

**Chat Completion Pattern:**
```python
chat_completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ],
    temperature=0.7,
    max_tokens=300
)
response = chat_completion.choices[0].message.content
```

**System Prompts:**
- Chat: Empathetic, supportive, non-judgmental tone
- Recommendations: Structured, evidence-based advice
- Language-specific: Include target language in prompt

### Supabase

**Authentication:**
```python
from supabase import create_client

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Sign up
auth_response = supabase.auth.sign_up({
    "email": email,
    "password": password
})

# Sign in
auth_response = supabase.auth.sign_in_with_password({
    "email": email,
    "password": password
})

# Store tokens
st.session_state.access_token = auth_response.session.access_token
st.session_state.refresh_token = auth_response.session.refresh_token
```

**Database Operations:**
```python
# INSERT
supabase.table('profiles').insert({
    "id": user_id,
    "email": email,
    "full_name": name
}).execute()

# SELECT
response = supabase.table('chat_sessions')\
    .select('*')\
    .eq('user_id', user_id)\
    .order('created_at', desc=True)\
    .execute()

# UPDATE
supabase.table('profiles')\
    .update({"full_name": new_name})\
    .eq('id', user_id)\
    .execute()

# DELETE
supabase.table('chat_sessions')\
    .delete()\
    .eq('id', session_id)\
    .execute()
```

---

## Session State Management

### Core Session Variables

```python
# Authentication
st.session_state.logged_in = False           # Login status
st.session_state.user = None                 # Supabase user object
st.session_state.access_token = None         # JWT access token
st.session_state.refresh_token = None        # JWT refresh token

# Navigation
st.session_state.menu = "Chat"               # Current page

# Language
st.session_state.language = "en"             # User's language preference

# Chat
st.session_state.messages = []               # Current chat messages
st.session_state.chat_sessions = {}          # User's chat sessions
st.session_state.current_session_id = None   # Active session ID

# Mood Tracking
st.session_state.selected_mood = None        # Mood selection
st.session_state.edit_mood = None            # Mood editing state

# Wellness Advisory
st.session_state.viewing_assessment_id = None  # Assessment being viewed

# Feedback
st.session_state.has_feedback_{session_id}_{index} = False
st.session_state.feedback_type_{session_id}_{index} = None
```

### Session State Best Practices

1. **Initialize in `main()` function**:
   ```python
   if 'logged_in' not in st.session_state:
       st.session_state.logged_in = False
   ```

2. **Use descriptive keys**:
   - Bad: `st.session_state.s1`, `st.session_state.data`
   - Good: `st.session_state.current_session_id`, `st.session_state.chat_sessions`

3. **Clear sensitive data on logout**:
   ```python
   st.session_state.logged_in = False
   st.session_state.user = None
   st.session_state.access_token = None
   # Clear other user-specific data
   ```

4. **Dynamic keys for collections**:
   Use formatted strings for feedback, editable items, etc.
   ```python
   key = f"has_feedback_{session_id}_{message_index}"
   st.session_state[key] = True
   ```

---

## Testing & Deployment

### Local Testing

1. **Test with .env file**:
   ```bash
   streamlit run main_app_v7.py
   ```

2. **Test authentication flow**:
   - Sign up with new email
   - Log in with existing credentials
   - Test logout and token expiration

3. **Test all features**:
   - Chat: Send messages, create sessions, delete conversations
   - Wellness: Complete questionnaire, view assessments, download PDF
   - Mood: Log moods, edit entries, view calendar
   - Profile: Update details, change language

### Deployment on Streamlit Cloud

1. **Connect GitHub repository**
2. **Set secrets** (Settings → Secrets):
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   GROQ_API_KEY = "your-groq-api-key"
   ```
3. **Deploy main branch**
4. **Monitor logs** for errors

### Testing Checklist

- [ ] Authentication (signup, login, logout)
- [ ] Chat (send messages, new sessions, delete)
- [ ] Wellness questionnaire (submit, view history, download PDF)
- [ ] Mood tracking (log mood, edit, view calendar)
- [ ] Profile management (update, language change)
- [ ] Multi-language support (switch languages, verify translations)
- [ ] Feedback system (rate responses, logout feedback)
- [ ] Error handling (API failures, database errors)

---

## Common Tasks

### Adding a New Feature

1. **Plan the feature**:
   - Define user flow
   - Identify database changes
   - Design UI mockup

2. **Update database schema** (if needed):
   - Create new table in Supabase
   - Add RLS policies
   - Test CRUD operations

3. **Add translations**:
   Update `translations.py` with new strings for all languages

4. **Implement feature**:
   - Create function in `main_app_v7.py`
   - Add to navigation menu
   - Test with various inputs

5. **Version the file**:
   ```bash
   cp main_app_v7.py main_app_v8.py
   # Make changes in v8
   ```

### Modifying AI Prompts

**Chat System Prompt** (in `MentalHealthChatbot.generate_response()`):
```python
system_content = f"""You are Animoa, a warm and empathetic mental health companion...
Language: {language_map[language]}"""
```

**Recommendation Prompt** (in `generate_recommendations()`):
```python
prompt = f"""As a mental health professional, analyze these responses...
Provide recommendations in {language_map[language]}."""
```

**Best Practices**:
- Keep prompts concise but specific
- Include language instruction for multilingual responses
- Test with edge cases (e.g., crisis mentions, unclear input)
- Adjust temperature for desired creativity level

### Adding a New Language

1. **Update `translations.py`**:
   ```python
   "fr": {  # Add French
       "welcome": "Bienvenue à Animoa🧠💬",
       # ... all translation keys
   }
   ```

2. **Update language selector** (in `main_app_v7.py`):
   ```python
   language_options = {"English": "en", "Español": "es", "中文": "zh", "Français": "fr"}
   ```

3. **Test all UI elements** with new language

### Debugging Session State Issues

1. **Add debug panel**:
   ```python
   if st.checkbox("Debug Session State"):
       st.json(dict(st.session_state))
   ```

2. **Check initialization**:
   Ensure all keys are initialized in `main()` before use

3. **Clear corrupted state**:
   ```python
   if st.button("Reset Session"):
       for key in list(st.session_state.keys()):
           del st.session_state[key]
       st.rerun()
   ```

---

## Important Notes

### Mental Health Considerations

This application deals with sensitive mental health data. When working on features:

1. **Privacy**: Never log user messages or personal data
2. **Crisis Detection**: Consider adding crisis keyword detection (suicide, self-harm) with resource links
3. **Disclaimers**: Maintain clear messaging that Animoa is not a replacement for professional help
4. **Data Security**: Use Supabase RLS policies to protect user data

### Known Issues & TODOs

1. **Devcontainer Configuration**: Update `.devcontainer/devcontainer.json` line 22 to use `main_app_v7.py`
2. **Version Cleanup**: Consider archiving old versions (v1-v5) to reduce repository size
3. **Translation Completeness**: Verify all new UI strings have translations in all languages
4. **PDF Styling**: Enhance `create_wellness_pdf()` with better formatting

### Performance Optimization

- **Groq API**: Fast inference (~1-2s response time), but rate-limited on free tier
- **Supabase Queries**: Add indexes on `user_id`, `created_at` for faster queries
- **Session State**: Minimize large objects in session state (cache database results sparingly)
- **Image Loading**: `logo.png` is 196KB—consider optimizing for web

### Security Best Practices

1. **Never commit `.env` file** to repository
2. **Use Supabase RLS** to restrict data access by user
3. **Validate user input** before database operations
4. **Sanitize chat messages** to prevent injection attacks
5. **Rotate API keys** periodically

---

## Quick Reference

### Useful Commands

```bash
# Run application
streamlit run main_app_v7.py

# Run with custom port
streamlit run main_app_v7.py --server.port 8080

# Disable CORS (for dev)
streamlit run main_app_v7.py --server.enableCORS false

# Install dependencies
pip install -r requirements.txt

# Freeze current dependencies
pip freeze > requirements.txt

# View Git status
git status

# Commit changes
git add .
git commit -m "feat: add new feature"
git push origin main
```

### Streamlit Shortcuts

- `R` - Rerun app
- `C` - Clear cache
- `Ctrl+C` - Stop server

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `AuthRetryableError` | Token expired | Refresh token or re-login |
| `Invalid API key` | Wrong Groq/Supabase key | Check `.env` file |
| `Table not found` | Database schema issue | Verify table exists in Supabase |
| `Session state key error` | Uninitialized key | Initialize in `main()` |

---

## Contact & Resources

- **Repository**: https://github.com/Swargambharath987/Project_Animoa
- **Streamlit Docs**: https://docs.streamlit.io
- **Groq API Docs**: https://console.groq.com/docs
- **Supabase Docs**: https://supabase.com/docs

---

*Last Updated: November 17, 2025*
*Current Version: main_app_v7.py*
