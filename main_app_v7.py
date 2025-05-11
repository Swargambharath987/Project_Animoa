# Add this as the first thing in your script, even before other imports
import streamlit as st

# More reliable theme setting
st.set_page_config(
    page_title="Animoa | Mental Health Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# Apply custom CSS directly
st.markdown("""
<style>
    /* Primary button color */
    .stButton>button {
        background-color: #4E9BB9;
        color: white;
    }
    
    /* Hover state for primary button */
    .stButton>button:hover {
        background-color: #3A7A94;
        color: white;
    }
    
    /* Secondary button color */
    .stButton>button[kind="secondary"] {
        background-color: transparent;
        color: #4E9BB9;
        border: 1px solid #4E9BB9;
    }
    
    /* Hover state for secondary button */
    .stButton>button[kind="secondary"]:hover {
        border-color: #3A7A94;
        color: #3A7A94;
    }
    
    /* Success elements */
    .element-container div[data-testid="stAlert"][kind="success"] {
        background-color: #E2F0E6;
        border-left-color: #4CAF50;
    }
    
    /* Warning elements */
    .element-container div[data-testid="stAlert"][kind="warning"] {
        background-color: #FFF8E1;
        border-left-color: #FFC107;
    }
    
    /* Info elements */
    .element-container div[data-testid="stAlert"][kind="info"] {
        background-color: #E2EEF3;
        border-left-color: #4E9BB9;
    }
    
    /* Error elements */
    .element-container div[data-testid="stAlert"][kind="error"] {
        background-color: #FDEDEB;
        border-left-color: #F44336;
    }
    
    /* General text color */
    body {
        color: #31505E;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #31505E;
    }
    
    /* Improve radio buttons and checkboxes */
    .stRadio > div[role="radiogroup"] > label > div:first-child,
    .stCheckbox > label > div:first-child {
        background-color: #4E9BB9 !important;
    }
    
    /* Widget labels */
    .stRadio label, .stCheckbox label, .stSelectbox label {
        color: #31505E;
    }
    
    /* Sidebar */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #F0F4F8;
    }
</style>
""", unsafe_allow_html=True)

# Rest of your imports and code follow

from groq import Groq
from supabase import create_client, Client
from dotenv import load_dotenv
import datetime
import os
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from gotrue.errors import AuthRetryableError
import pandas as pd


from translations import load_translations
# Dictionary for UI translations - English, Spanish, and Mandarin Chinese
TRANSLATIONS = load_translations()

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables (for local development)
# or from Streamlit secrets (for deployment)
def get_api_key(key_name):
    """Get API key from environment variables or Streamlit secrets"""
    try:
        # Try to get from environment variables first
        env_value = os.getenv(key_name)
        if env_value:
            return env_value
        # If not found, try to get from Streamlit secrets
        return st.secrets[key_name]
    except Exception:
        st.error(f"Missing API key: {key_name}")
        st.stop()

# Initialize API keys
supabase_url = get_api_key("SUPABASE_URL")
supabase_key = get_api_key("SUPABASE_KEY")
groq_api_key = get_api_key("GROQ_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Function to log in or sign up
def auth_ui(supabase):
    # Get current language and translations
    current_lang = st.session_state.language if "language" in st.session_state else 'en'
    translations = TRANSLATIONS.get(current_lang, TRANSLATIONS['en'])
    
    if "logged_in" in st.session_state and st.session_state.logged_in:
        # If already logged in, show user info in sidebar
        st.sidebar.success(f"Logged in as: {st.session_state.user.email}")
        
        # Language selector in sidebar
        language_options = {
            'en': 'English',
            'es': 'Español',
            'zh': '中文 (Chinese)'
        }
        selected_lang = st.sidebar.selectbox(
            translations['language'],
            options=list(language_options.keys()),
            format_func=lambda x: language_options[x],
            index=list(language_options.keys()).index(current_lang) if current_lang in language_options else 0,
            key="sidebar_language_selector"
        )
        
        # Update language if changed
        if selected_lang != current_lang:
            st.session_state.language = selected_lang
            # If logged in, save preference
            if "user" in st.session_state:
                try:
                    supabase.table('profiles').update({
                        'preferred_language': selected_lang
                    }).eq('id', st.session_state.user.id).execute()
                except:
                    pass
            st.rerun()
        return True
    
    # If not logged in, show login/signup form
    st.title(translations["welcome"])
    
    # Add language selector for login page too
    col_lang, col_empty = st.columns([1, 3])
    with col_lang:
        language_options = {
            'en': 'English',
            'es': 'Español',
            'zh': '中文 (Chinese)'
        }
        selected_lang = st.selectbox(
            translations['language'],
            options=list(language_options.keys()),
            format_func=lambda x: language_options[x],
            index=list(language_options.keys()).index(current_lang) if current_lang in language_options else 0,
            key="login_language_selector"
        )
        
        # Update language if changed
        if selected_lang != current_lang:
            st.session_state.language = selected_lang
            st.rerun()    
    
    st.markdown("""
    <div style="padding: 20px; border-radius: 10px; background-color: rgba(78, 155, 185, 0.1); margin-bottom: 25px;">
        <h3 style="margin-top: 0;">Your Mental Health Companion</h3>
        <p style="font-size: 1.1rem; margin-bottom: 15px;">
            <i>"A companion for your mental wellness journey, available whenever you need support."</i>
        </p>
        <p>
            Animoa provides a safe space for self-reflection and emotional support through thoughtful conversations, 
            mood tracking, and personalized wellness insights. Whether you're feeling anxious, need someone to talk to, 
            or simply want to maintain your mental well-being, Animoa is here to help. Sign in to access personalized mental health support
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication tabs
    tab1, tab2 = st.tabs([translations["login"], translations["signup"]])
    
    with tab1:  # Login tab
        login_email = st.text_input(translations["email"], key="login_email")
        login_password = st.text_input(translations["password"], type="password", key="login_password")
        
        if st.button(translations["login"], use_container_width=True):
            if not login_email or not login_password:
                st.error("Please enter both email and password")
            else:
                try:
                    result = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                    if hasattr(result, 'error') and result.error is not None:
                        st.error(f"Login failed: {result.error.message}")
                    else:
                        # Store user data in session state
                        st.session_state.user = result.user
                        st.session_state.logged_in = True
                        st.session_state.access_token = result.session.access_token
                        st.session_state.refresh_token = result.session.refresh_token
                        
                        # Get user's preferred language
                        try:
                            response = supabase.table('profiles').select('preferred_language').eq('id', result.user.id).execute()
                            if response.data and len(response.data) > 0 and response.data[0]['preferred_language']:
                                st.session_state.language = response.data[0]['preferred_language']
                        except:
                            pass
                            
                        st.success("Login successful!")
                        # Enable RLS for this user
                        supabase.auth.set_session(result.session.access_token, result.session.refresh_token)
                        st.rerun()
                except Exception as e:
                    st.error(f"Authentication error: {str(e)}")
    
    with tab2:  # Sign Up tab
        signup_email = st.text_input(translations["email"], key="signup_email")
        signup_password = st.text_input(translations["password"], type="password", key="signup_password")
        confirm_password = st.text_input(translations["confirm_password"], type="password")
        
        if st.button(translations["signup"], use_container_width=True):
            if not signup_email or not signup_password:
                st.error("Please enter both email and password")
            elif signup_password != confirm_password:
                st.error("Passwords do not match")
            else:
                try:
                    result = supabase.auth.sign_up({"email": signup_email, "password": signup_password})
                    if hasattr(result, 'error') and result.error is not None:
                        st.error(f"Signup failed: {result.error.message}")
                    else:
                        st.success("""
                        Signup successful! Please check your email to confirm your account.
                        
                        Once confirmed, you can log in with your credentials.
                        """)
                except Exception as e:
                    st.error(f"Signup error: {str(e)}")
        
    st.info("""
    **About Animoa**

    - Animoa uses AI technology to provide supportive conversations and wellness insights.
    - Your conversations and assessments are stored securely to personalize your experience.
    - You can delete your data at any time through your profile settings.
    """)

    st.warning("""
    **Important Disclaimer**

    Animoa is designed to provide support and general wellness information, not to replace professional mental health care. 
    If you're experiencing a crisis or need immediate help, please contact a qualified healthcare provider or emergency services.

    By creating an account, you agree to our Terms of Service and Privacy Policy.
    """)
    
    return False  # Return False if not logged in

# Function to ensure user has a profile
def ensure_profile_exists(user_id, email):
    """Make sure a profile exists for the user"""
    try:
        # Check if profile exists
        response = supabase.table('profiles').select('*').eq('id', user_id).execute()
        
        if not response.data:
            # Create a new profile if it doesn't exist
            supabase.table('profiles').insert({
                'id': user_id,
                'email': email
            }).execute()
            
    except Exception as e:
        st.sidebar.warning(f"Profile setup issue: {str(e)}")

# Profile management functionality
def profile_manager(supabase):
    # Get current language and translations
    current_lang = st.session_state.language if "language" in st.session_state else 'en'
    translations = TRANSLATIONS.get(current_lang, TRANSLATIONS['en'])
    
    st.header(translations["profile_title"])
    
    # Get existing profile data
    user_id = st.session_state.user.id
    email = st.session_state.user.email
    
    # Ensure profile exists
    ensure_profile_exists(user_id, email)
    
    try:
        response = supabase.table('profiles').select('*').eq('id', user_id).execute()
        profile_data = response.data
        
        if profile_data and len(profile_data) > 0:
            existing_data = profile_data[0]
        else:
            existing_data = {'full_name': '', 'age': None, 'goals': '', 'stress_level': '', 'interests': '', 'preferred_language': 'en'}
            
    except Exception as e:
        st.error(f"Error retrieving profile: {str(e)}")
        return
    
    # Get current language code
    current_lang = existing_data.get('preferred_language', 'en')
    
    # Translate stress level options
    stress_levels = {
        'en': ["Low", "Moderate", "High", "Very High"],
        'es': ["Bajo", "Moderado", "Alto", "Muy Alto"],
        'zh': ["低", "中等", "高", "非常高"]    
    }
    current_stress_levels = stress_levels.get(current_lang, stress_levels['en'])
    
    # Profile form with enhanced UI
    st.markdown(f"### {translations['personal_details']}")
    st.write(translations["profile_subtitle"])
    
    col1, col2 = st.columns(2)
    
    with st.form("profile_form"):
        with col1:
            full_name = st.text_input(translations["name"], value=existing_data.get('full_name', ''))
            age = st.number_input(translations["age"], min_value=13, max_value=120, value=existing_data.get('age', 30))
        
        with col2:
            # Get current stress level index or default to moderate (index 1)
            current_stress_level = existing_data.get('stress_level', 'Moderate')
            stress_level_index = 1  # Default to moderate
            
            # Try to find the index in the current language
            if current_stress_level in current_stress_levels:
                stress_level_index = current_stress_levels.index(current_stress_level)
            # If not found, try to find equivalent index from English
            elif current_stress_level in stress_levels['en']:
                stress_level_index = stress_levels['en'].index(current_stress_level)
                
            stress_level = st.selectbox(
                translations["stress_level"], 
                current_stress_levels,
                index=stress_level_index
            )
            
            # Add language preference dropdown
            language_options = {
                'en': 'English',
                'es': 'Español',
                'zh': '中文 (Chinese)'
            }
            preferred_language = st.selectbox(
                translations['language'],
                options=list(language_options.keys()),
                format_func=lambda x: language_options[x],
                index=list(language_options.keys()).index(current_lang) if current_lang in language_options else 0
            )
        
        st.markdown(f"### {translations['mental_wellness_goals']}")
        goals = st.text_area(
            translations["goals_placeholder"], 
            value=existing_data.get('goals', ''),
            placeholder=translations["goals_placeholder"]
        )
        
        interests = st.text_area(
            translations["interests"], 
            value=existing_data.get('interests', ''),
            placeholder=translations["interests_placeholder"]
        )
        
        submit_button = st.form_submit_button(translations["save_profile"])
        
        if submit_button:
            try:
                supabase.table('profiles').update({
                    'full_name': full_name,
                    'age': age,
                    'stress_level': stress_level,
                    'goals': goals,
                    'interests': interests,
                    'preferred_language': preferred_language
                }).eq('id', user_id).execute()
                
                # Update session state with new language preference
                if 'language' not in st.session_state or st.session_state.language != preferred_language:
                    st.session_state.language = preferred_language
                
                st.success(translations["profile_updated"])
                # Force refresh to update UI language
                st.rerun()
            except Exception as e:
                st.error(f"Error updating profile: {str(e)}")
                
                              
class MentalHealthChatbot:
    def __init__(self):
        # Initialize Groq client
        self.client = Groq(api_key=groq_api_key)
        
        # Initialize session state variables if they don't exist
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "chat_sessions" not in st.session_state:
            st.session_state.chat_sessions = {}
            
        if "current_session_id" not in st.session_state:
            st.session_state.current_session_id = None
        
        # Initialize language preference
        if "language" not in st.session_state and "user" in st.session_state:
            try:
                # Get user's preferred language from profile
                response = supabase.table('profiles').select('preferred_language').eq('id', st.session_state.user.id).execute()
                if response.data and len(response.data) > 0 and response.data[0]['preferred_language']:
                    st.session_state.language = response.data[0]['preferred_language']
                else:
                    st.session_state.language = 'en'  # Default to English
            except:
                st.session_state.language = 'en'  # Default to English if error
        elif "language" not in st.session_state:
            st.session_state.language = 'en'  # Default for non-logged users
            
        # Load sessions for logged-in user
        if "user" in st.session_state:
            self.load_chat_sessions()
    
    def load_chat_sessions(self):
        """Load chat sessions metadata from Supabase"""
        try:
            # First, load session metadata
            response = supabase.table('chat_sessions').select('*').eq('user_id', st.session_state.user.id).order('created_at', desc=True).execute()
            
            # Initialize chat sessions dictionary
            st.session_state.chat_sessions = {}
            
            if response and response.data:
                for session in response.data:
                    session_id = session['id']
                    st.session_state.chat_sessions[session_id] = {
                        'title': session['title'],
                        'created_at': session['created_at']
                    }
                
                # Set current session to the most recent one if not already set
                if st.session_state.current_session_id is None and response.data:
                    st.session_state.current_session_id = response.data[0]['id']
                    self.load_chat_history(st.session_state.current_session_id)
        except Exception as e:
            st.warning(f"Could not load chat sessions: {str(e)}")
    
    def load_chat_history(self, session_id=None):
        """Load chat history for a specific session from Supabase"""
        # Clear current messages
        st.session_state.messages = []
        
        if session_id is None:
            return
            
        try:
            # Get chat history for the session
            response = supabase.table('chat_history').select('*').eq('session_id', session_id).order('timestamp', desc=False).execute()
            
            if response and response.data:
                message_data = []
                feedback_data = {}
                
                # First, separate messages from feedback
                for msg in response.data:
                    if msg['sender'] == 'user':
                        message_data.append({"role": "user", "content": msg['message']})
                    elif msg['sender'] == 'bot':
                        message_data.append({"role": "assistant", "content": msg['message']})
                    elif msg['sender'] == 'feedback':
                        # Store feedback data with message index as key
                        if 'feedback_for_message_index' in msg:
                            index = msg['feedback_for_message_index']
                            feedback_data[index] = msg['message']
                
                # Add messages to session state
                st.session_state.messages = message_data
                
                # Process feedback and update session state
                for index, feedback in feedback_data.items():
                    if index < len(message_data):
                        feedback_key = f"has_feedback_{session_id}_{index}"
                        feedback_type_key = f"feedback_type_{session_id}_{index}"
                        st.session_state[feedback_key] = True
                        st.session_state[feedback_type_key] = feedback
        except Exception as e:
            st.warning(f"Could not load chat history: {str(e)}")
    
    def create_new_session(self):
        """Create a new chat session"""
        try:
            # Generate a default session title
            current_time = datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")
            session_title = f"Chat {current_time}"
            
            # Create session in database
            response = supabase.table('chat_sessions').insert({
                'user_id': st.session_state.user.id,
                'title': session_title,
                'created_at': datetime.datetime.now().isoformat()
            }).execute()
            
            # Get the new session ID
            new_session_id = response.data[0]['id']
            
            # Update session state
            st.session_state.chat_sessions[new_session_id] = {
                'title': session_title,
                'created_at': datetime.datetime.now().isoformat()
            }
            
            # Set as current session
            st.session_state.current_session_id = new_session_id
            st.session_state.messages = []  # Clear messages for new session
            
            # Clear any feedback-related session state variables for previous sessions
            for key in list(st.session_state.keys()):
                if key.startswith("has_feedback_") or key.startswith("feedback_type_") or key.startswith("show_detailed_feedback_"):
                    del st.session_state[key]
            
            return new_session_id
        except Exception as e:
            st.warning(f"Could not create new session: {str(e)}")
            return None
                
    def save_message(self, role, content, message_index=None):
        """Save a message to the database, including feedback"""
        if "user" in st.session_state:
            try:
                # Ensure we have a current session
                if st.session_state.current_session_id is None:
                    session_id = self.create_new_session()
                else:
                    session_id = st.session_state.current_session_id
                
                # Save message
                message_data = {
                    'user_id': st.session_state.user.id,
                    'session_id': session_id,
                    'message': content,
                    'sender': 'user' if role == 'user' else 'bot',
                    'timestamp': datetime.datetime.now().isoformat()  # Add timestamp
                }
                
                if role == "feedback" and message_index is not None:
                    # For feedback, properly set the fields
                    message_data['feedback_for_message_index'] = message_index
                    message_data['sender'] = 'feedback'  # overwrite the sender
                    
                    # Check if feedback already exists for this message to avoid duplicates
                    existing = supabase.table('chat_history').select('id')\
                        .eq('user_id', st.session_state.user.id)\
                        .eq('session_id', session_id)\
                        .eq('sender', 'feedback')\
                        .eq('feedback_for_message_index', message_index)\
                        .execute()
                        
                    if existing.data and len(existing.data) > 0:
                        # Update existing feedback instead of creating a new one
                        supabase.table('chat_history').update({
                            'message': content,
                            'timestamp': datetime.datetime.now().isoformat()
                        }).eq('id', existing.data[0]['id']).execute()
                        
                        # Update the session state to reflect this change
                        feedback_key = f"has_feedback_{session_id}_{message_index}"
                        feedback_type_key = f"feedback_type_{session_id}_{message_index}"
                        st.session_state[feedback_key] = True
                        st.session_state[feedback_type_key] = content
                        
                        return
                
                # Insert new message/feedback
                result = supabase.table('chat_history').insert(message_data).execute()
                
                # If this is a feedback message, update the session state
                if role == "feedback" and message_index is not None:
                    feedback_key = f"has_feedback_{session_id}_{message_index}"
                    feedback_type_key = f"feedback_type_{session_id}_{message_index}"
                    st.session_state[feedback_key] = True
                    st.session_state[feedback_type_key] = content
                    
            except Exception as e:
                st.warning(f"Could not save message to database: {str(e)}")
    def generate_response(self, user_input, conversation_history):
        """Generate response using Groq API with conversation context and in user's language"""
        try:
            # Get user's preferred language
            user_language = st.session_state.language
            
            # Language mapping for prompt
            language_names = {
                'en': 'English',
                'es': 'Spanish',
                'zh': 'Mandarin Chinese'
            }
            
            language_name = language_names.get(user_language, 'English')
            
            # Create a more empathetic and warm system prompt with language instruction
            system_prompt = f"""You are Animoa, a warm and empathetic wellness companion. Your responses should feel like 
            talking with a supportive friend who genuinely cares about helping people feel better. Be conversational 
            and natural - avoid sounding clinical or robotic.

            Key approach:
            - Be genuinely curious about the person's feelings and experiences
            - Respond with warmth, understanding, and gentle encouragement
            - Ask thoughtful follow-up questions that help people explore their thoughts
            - Keep your responses concise and focused (2-3 sentences is often enough)
            - Use a calming, positive tone that makes people feel comfortable sharing

            IMPORTANT: Respond in {language_name}. The user is communicating in {language_name}, 
            so your entire response must be in {language_name} only. Maintain the same supportive tone and style.

            Your goal is to create a safe space for reflection and emotional support through natural conversation.
            """
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add previous conversation messages
            messages.extend(conversation_history)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Generate response using Groq
            chat_completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7
            )
            
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"I'm having trouble responding right now. Error: {str(e)}"
    
    
    def prepare_conversation_history(self):
        """Prepare conversation history for context"""
        return [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.messages
        ]

    def run(self):
        """Main Streamlit application for chat"""
        # Get current language and translations
        current_lang = st.session_state.language
        translations = TRANSLATIONS.get(current_lang, TRANSLATIONS['en'])
        
        # Create two columns - one for session list, one for chat
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"### {translations['chat']}")
            
            # Language selector
            language_options = {
                'en': 'English',
                'es': 'Español',
                'zh': '中文 (Chinese)'
            }
            selected_lang = st.selectbox(
                translations['language'],
                options=list(language_options.keys()),
                format_func=lambda x: language_options[x],
                index=list(language_options.keys()).index(current_lang) if current_lang in language_options else 0,
                key="language_selector"
            )
            
            # Update language if changed
            if selected_lang != current_lang:
                st.session_state.language = selected_lang
                # If logged in, save preference
                if "user" in st.session_state:
                    try:
                        supabase.table('profiles').update({
                            'preferred_language': selected_lang
                        }).eq('id', st.session_state.user.id).execute()
                    except:
                        pass
                st.rerun()
            
            # New chat button
            if st.button(f"{translations['new_chat']}", use_container_width=True, key="new_chat_button"):
                self.create_new_session()
                st.rerun()
            
            # Session list
            st.markdown("---")
            for session_id, session_info in st.session_state.chat_sessions.items():
                # Format the title and date
                title = session_info['title']
                # Shorten title if needed
                if len(title) > 20:
                    title = title[:17] + "..."
                
                # Determine if this is the active session
                is_active = session_id == st.session_state.current_session_id
                
                # Use a button with conditional formatting
                button_style = "primary" if is_active else "secondary"
                if st.button(f"{title}", key=f"session_{session_id}", use_container_width=True, type=button_style):
                    st.session_state.current_session_id = session_id
                    self.load_chat_history(session_id)
                    st.rerun()
        
        with col2:
            # Create chat interface inside a container for better control
            chat_interface = st.container()
            
            # delete chat option at the top
            #add_delete_chat_option(self)  
            
            with chat_interface:
                # Add delete option and translation options in a row
                # Inside the MentalHealthChatbot.run() method, in the chat_interface section:

                # Inside the MentalHealthChatbot.run() method, in the chat_interface section:

                # Add delete option and translation options in a row at the top
                if st.session_state.messages:
                    cols = st.columns([1, 1])
                    with cols[0]:
                        if st.button(translations['translate_history']):
                            with st.spinner("Translating..."):
                                st.session_state.messages = self.translate_messages(st.session_state.messages, current_lang)
                            st.rerun()
                    with cols[1]:
                        if st.button("🗑️ Delete Chat", key="simple_delete_chat"):
                            if st.session_state.current_session_id:
                                # Use session state to track confirmation state
                                st.session_state.show_delete_confirm = True
                                st.session_state.delete_session_id = st.session_state.current_session_id
                                st.rerun()

                    # Handle deletion confirmation outside other containers
                    if "show_delete_confirm" in st.session_state and st.session_state.show_delete_confirm:
                        # Check if we're still on the same session that was marked for deletion
                        if st.session_state.get("delete_session_id") == st.session_state.current_session_id:
                            st.warning("Are you sure you want to delete this conversation? This cannot be undone.")
                            
                            # Use layout without nested columns
                            if st.button("Yes, delete it", key="confirm_delete_simple"):
                                try:
                                    # Delete all messages in this chat
                                    supabase.table('chat_history').delete().eq('session_id', st.session_state.current_session_id).execute()
                                    
                                    # Delete the session itself
                                    supabase.table('chat_sessions').delete().eq('id', st.session_state.current_session_id).execute()
                                    
                                    # Clear local state
                                    if st.session_state.current_session_id in st.session_state.chat_sessions:
                                        del st.session_state.chat_sessions[st.session_state.current_session_id]
                                    
                                    # Clear current session and messages
                                    st.session_state.current_session_id = None
                                    st.session_state.messages = []
                                    
                                    # Clear the confirmation states
                                    del st.session_state.show_delete_confirm
                                    del st.session_state.delete_session_id
                                    
                                    st.success("Conversation deleted successfully.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting conversation: {str(e)}")
                            
                            if st.button("Cancel", key="cancel_delete_simple"):
                                del st.session_state.show_delete_confirm
                                if "delete_session_id" in st.session_state:
                                    del st.session_state.delete_session_id
                                st.rerun()
                        else:
                            # If user switched to another session, clear the delete confirmation
                            del st.session_state.show_delete_confirm
                            if "delete_session_id" in st.session_state:
                                del st.session_state.delete_session_id
                            st.rerun()
                
                # First create a container for messages
                messages_container = st.container()
                
                # Then create the input BELOW the messages container
                prompt = st.chat_input(translations['chat_placeholder'], key="chat_input")
                
                # Display messages in the messages container
                with messages_container:
                    # Welcome message if no messages yet
                    if not st.session_state.messages:
                        st.markdown(f"""
                                    <div style="padding: 1.5rem; text-align: center; color: #6c757d; margin-top: 2rem;">
                                    <h3>{translations['welcome_message']}</h3>
                                    <p>{translations['welcome_subtitle']}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                    
                    # Display chat history                   
                    for i, message in enumerate(st.session_state.messages):
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
                            # For the latest assistant message only, show feedback UI
                            # For the latest assistant message only, show feedback UI
                            # Replace the feedback section in the MentalHealthChatbot.run method with this improved code

                            # For the latest assistant message only, show feedback UI
                            if message["role"] == "assistant" and i == len(st.session_state.messages) - 1:  # Only for the latest assistant message
                                # Create a container for the feedback options
                                feedback_container = st.container()
                                with feedback_container:
                                    # Check if feedback exists in database for this message
                                    has_feedback = False
                                    feedback_type = None
                                    
                                    if "user" in st.session_state:
                                        try:
                                            # Message index in session is used as reference in database
                                            # Check if feedback exists for this message
                                            response = supabase.table('chat_history').select('*')\
                                                .eq('user_id', st.session_state.user.id)\
                                                .eq('session_id', st.session_state.current_session_id)\
                                                .eq('sender', 'feedback')\
                                                .eq('feedback_for_message_index', i)\
                                                .execute()
                                                
                                            if response.data and len(response.data) > 0:
                                                has_feedback = True
                                                feedback_type = response.data[0]['message']
                                        except Exception as e:
                                            print(f"Error checking feedback: {str(e)}")

                                    # Store has_feedback in session state to ensure consistency across reruns
                                    feedback_key = f"has_feedback_{st.session_state.current_session_id}_{i}"
                                    if feedback_key not in st.session_state:
                                        st.session_state[feedback_key] = has_feedback
                                        st.session_state[f"feedback_type_{st.session_state.current_session_id}_{i}"] = feedback_type
                                    
                                    # Only show feedback options if feedback hasn't been given yet
                                    if not st.session_state[feedback_key]:
                                        # Use columns to create a horizontal layout
                                        fb_col1, fb_col2, fb_col3, fb_col4, fb_col5, fb_col6 = st.columns([1, 1, 1, 1, 1, 3])
                                        
                                        with fb_col1:
                                            if st.button("😊", key=f"happy_{st.session_state.current_session_id}_{i}", help="Helpful response"):
                                                self.save_message("feedback", "😊 Helpful", i)
                                                st.session_state[feedback_key] = True
                                                st.session_state[f"feedback_type_{st.session_state.current_session_id}_{i}"] = "😊 Helpful"
                                                st.success("Thank you for your feedback!")
                                                time.sleep(0.5)
                                                st.rerun()
                                                
                                        with fb_col2:
                                            if st.button("🤔", key=f"thinking_{st.session_state.current_session_id}_{i}", help="Made me think"):
                                                self.save_message("feedback", "🤔 Thoughtful", i)
                                                st.session_state[feedback_key] = True
                                                st.session_state[f"feedback_type_{st.session_state.current_session_id}_{i}"] = "🤔 Thoughtful"
                                                st.success("Thank you for your feedback!")
                                                time.sleep(0.5)
                                                st.rerun()
                                        
                                        with fb_col3:
                                            if st.button("❤️", key=f"heart_{st.session_state.current_session_id}_{i}", help="Love this response"):
                                                self.save_message("feedback", "❤️ Love it", i)
                                                st.session_state[feedback_key] = True
                                                st.session_state[f"feedback_type_{st.session_state.current_session_id}_{i}"] = "❤️ Love it"
                                                st.success("Thank you for your feedback!")
                                                time.sleep(0.5)
                                                st.rerun()
                                                
                                        with fb_col4:
                                            if st.button("👍", key=f"thumbs_up_{st.session_state.current_session_id}_{i}", help="Great response"):
                                                self.save_message("feedback", "👍 Great", i)
                                                st.session_state[feedback_key] = True
                                                st.session_state[f"feedback_type_{st.session_state.current_session_id}_{i}"] = "👍 Great"
                                                st.success("Thank you for your feedback!")
                                                time.sleep(0.5)
                                                st.rerun()
                                                
                                        with fb_col5:
                                            if st.button("👎", key=f"thumbs_down_{st.session_state.current_session_id}_{i}", help="Not helpful"):
                                                # Show a small popup for more detailed feedback if negative
                                                st.session_state[f"show_detailed_feedback_{st.session_state.current_session_id}_{i}"] = True
                                                self.save_message("feedback", "👎 Not helpful", i)
                                                st.session_state[feedback_key] = True
                                                st.session_state[f"feedback_type_{st.session_state.current_session_id}_{i}"] = "👎 Not helpful"
                                                st.warning("Sorry this wasn't helpful.")
                                                time.sleep(0.5)
                                                st.rerun()
                                        
                                        with fb_col6:
                                            # Only show the detailed feedback field if thumbs down was clicked
                                            feedback_detail_key = f"show_detailed_feedback_{st.session_state.current_session_id}_{i}"
                                            if feedback_detail_key in st.session_state and st.session_state[feedback_detail_key]:
                                                with st.form(key=f"detailed_feedback_form_{st.session_state.current_session_id}_{i}"):
                                                    st.write("What could be improved?")
                                                    detailed_feedback = st.text_area("", key=f"detailed_feedback_{st.session_state.current_session_id}_{i}", label_visibility="collapsed")
                                                    submit_btn = st.form_submit_button("Submit")
                                                    
                                                    if submit_btn and detailed_feedback:
                                                        self.save_message("feedback", f"Comment: {detailed_feedback}", i)
                                                        # Keep the main feedback status but update the type to include the comment
                                                        st.session_state[f"feedback_type_{st.session_state.current_session_id}_{i}"] += f" - {detailed_feedback}"
                                                        # Remove detailed feedback form flag
                                                        del st.session_state[feedback_detail_key]
                                                        st.success("Thank you for your detailed feedback!")
                                                        time.sleep(0.5)
                                                        st.rerun()
                                    else:
                                        # If feedback was already given, just show what was selected with a small info message
                                        feedback_type_key = f"feedback_type_{st.session_state.current_session_id}_{i}"
                                        if feedback_type_key in st.session_state:
                                            displayed_feedback = st.session_state[feedback_type_key]
                                        else:
                                            displayed_feedback = feedback_type if feedback_type else "Feedback received"
                                            
                                        st.info(f"You rated this response: {displayed_feedback}")
                                                                                                
            # Process user input - needs to be outside the chat_interface container
            if prompt:
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})
                self.save_message("user", prompt)
                
                # Prepare conversation history
                conversation_history = self.prepare_conversation_history()
                
                # Generate and display bot response
                with st.spinner("Thinking..."):
                    response = self.generate_response(prompt, conversation_history)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    self.save_message("assistant", response)
                
                # Force a rerun to update the UI with new messages
                st.rerun()
                
    def translate_messages(self, messages, target_language):
        """
        Translate the content of messages to the target language
        In a production app, you would use a translation API like Google Translate
        For demo purposes, we'll simulate translation
        """
        # In production, replace this with actual API call to a translation service
        try:
            # Use Groq for translation for demo/prototype purposes
            translated_messages = []
            
            language_names = {
                'en': 'English',
                'es': 'Spanish',
                'zh': 'Mandarin Chinese'
            }
            
            target_lang_name = language_names.get(target_language, 'English')
            
            for msg in messages:
                # For both user and assistant messages, use Groq to generate proper translations
                system_prompt = f"You are a precise translator. Translate the following message to {target_lang_name}. Keep the same tone and meaning.do not give any additional notes or comments."
                
                translation_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": msg["content"]}
                ]
                
                completion = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=translation_messages,
                    temperature=0.3
                )
                
                translated_content = completion.choices[0].message.content
                translated_messages.append({
                    "role": msg["role"],
                    "content": translated_content
                })
                    
            return translated_messages
        except Exception as e:
            st.warning(f"Translation error: {str(e)}")
            return messages  # Return original messages if translation fails
    
# Add this function before the mental_health_advisory() function to make the PDF creation reusable
def create_wellness_pdf(responses, recommendations):
    """Create a PDF for wellness insights"""
    buffer = BytesIO()
    # Use ReportLab for better PDF styling
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)

    # Get and modify styles instead of adding new ones with the same names
    styles = getSampleStyleSheet()
    # Modify existing styles
    styles['Title'].alignment = TA_CENTER
    styles['Title'].fontSize = 18
    styles['Title'].spaceAfter = 12

    # Add custom styles with unique names - use standard font names
    styles.add(ParagraphStyle(name='AnimoaSubtitle',
                             fontName='Helvetica-Bold',
                             fontSize=14,
                             alignment=TA_CENTER,
                             spaceAfter=12))
    styles.add(ParagraphStyle(name='AnimoaSection',
                             fontName='Helvetica-Bold',
                             fontSize=12,
                             spaceAfter=6))
    styles.add(ParagraphStyle(name='AnimoaNormal',
                             fontName='Helvetica',
                             fontSize=10,
                             spaceAfter=6))

    # Add content to the PDF
    content = []

    # Try to add logo (if available)
    try:
        # Path to the logo - adjust path as needed
        logo_path = "logo.png"  # Place your logo in the same directory as the script
        img = Image(logo_path)
        img.hAlign = 'CENTER'
        content.append(img)
        content.append(Spacer(1, 12))
    except Exception as e:
        # If logo not found, just add title with more space
        print(f"Logo not found: {e}")
        content.append(Spacer(1, 0.5*inch))

    # Add title and current date
    content.append(Paragraph("MENTAL WELLNESS INSIGHTS", styles['Title']))
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    content.append(Paragraph(f"Generated on {current_date}", styles['AnimoaSubtitle']))
    content.append(Spacer(1, 0.25*inch))

    # Add user's responses summary in a table
    content.append(Paragraph("ASSESSMENT SUMMARY", styles['AnimoaSection']))

    # Translate the responses to readable format
    mood_map = {"Not at all": "None", "Several days": "Mild", "More than half the days": "Moderate", "Nearly every day": "Severe"}
    sleep_map = {"Very poor": "Very Poor", "Poor": "Poor", "Fair": "Fair", "Good": "Good", "Very good": "Excellent"}
    support_map = {"No support": "None", "Limited support": "Limited", "Moderate support": "Moderate", "Strong support": "Strong"}

    # Create a neat table for the assessment summary
    assessment_data = [
        ["Assessment Area", "Response", "Severity/Quality"],
        ["Feeling down or depressed", responses["mood"], mood_map.get(responses["mood"], "-")],
        ["Little interest or pleasure", responses["interest"], mood_map.get(responses["interest"], "-")],
        ["Feeling anxious", responses["anxiety"], mood_map.get(responses["anxiety"], "-")],
        ["Uncontrollable worry", responses["worry"], mood_map.get(responses["worry"], "-")],
        ["Sleep quality", responses["sleep"], sleep_map.get(responses["sleep"], "-")],
        ["Social support", responses["support"], support_map.get(responses["support"], "-")]
    ]

    # Create table and set style
    assessment_table = Table(assessment_data, colWidths=[2.2*inch, 2.2*inch, 1.6*inch])
    assessment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (2, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (2, 0), colors.black),
        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (2, 0), 10),
        ('BOTTOMPADDING', (0, 0), (2, 0), 6),
        ('BACKGROUND', (0, 1), (2, 6), colors.white),
        ('GRID', (0, 0), (2, 6), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (2, -1), 'CENTER'),
    ]))

    content.append(assessment_table)
    content.append(Spacer(1, 0.1*inch))

    # Add coping strategies separately as they can be longer text
    content.append(Paragraph("Current Coping Strategies:", styles['AnimoaSection']))
    coping_text = responses["coping"] if responses["coping"] else "No coping strategies provided."
    content.append(Paragraph(coping_text, styles['AnimoaNormal']))
    content.append(Spacer(1, 0.2*inch))

    # Add recommendations with proper formatting
    content.append(Paragraph("PERSONALIZED RECOMMENDATIONS", styles['AnimoaSection']))
    content.append(Spacer(1, 0.1*inch))

    # Simple, efficient approach with fixed bold text handling
    for line in recommendations.split('\n'):
        line = line.strip()
        if not line:
            # Empty line - add space
            content.append(Spacer(1, 6))
        elif line.startswith('### '):
            # Section header (H3)
            content.append(Paragraph(line[4:], styles['AnimoaSection']))
        elif line.startswith('## '):
            # Section header (H2)
            content.append(Paragraph(line[3:], styles['AnimoaSection']))
        elif line.startswith('# '):
            # Main header (H1)
            content.append(Paragraph(line[2:], styles['AnimoaSubtitle']))
        elif line.startswith('* ') or line.startswith('• '):
            # Bullet point - convert to a proper bullet in the PDF
            text = line[2:]  # Remove bullet marker
            
            # Fixed approach for bold text - explicitly handle pairs of **
            text_with_tags = ""
            i = 0
            bold_open = False
            
            while i < len(text):
                if text[i:i+2] == '**':
                    if not bold_open:
                        text_with_tags += '<b>'
                        bold_open = True
                    else:
                        text_with_tags += '</b>'
                        bold_open = False
                    i += 2
                else:
                    text_with_tags += text[i]
                    i += 1
                    
            # Ensure bold tags are closed
            if bold_open:
                text_with_tags += '</b>'
                
            content.append(Paragraph(f"• {text_with_tags}", styles['AnimoaNormal']))
        else:
            # Regular text with same bold handling
            text_with_tags = ""
            i = 0
            bold_open = False
            
            while i < len(line):
                if line[i:i+2] == '**':
                    if not bold_open:
                        text_with_tags += '<b>'
                        bold_open = True
                    else:
                        text_with_tags += '</b>'
                        bold_open = False
                    i += 2
                else:
                    text_with_tags += line[i]
                    i += 1
                    
            # Ensure bold tags are closed
            if bold_open:
                text_with_tags += '</b>'
                
            content.append(Paragraph(text_with_tags, styles['AnimoaNormal']))

    # Add disclaimer at the bottom
    content.append(Spacer(1, 0.3*inch))
    disclaimer_text = ("Disclaimer: This assessment is generated based on your responses using evidence-based protocols. "
                      "It is not a clinical diagnosis. Animoa AI creates these insights to support your mental wellness journey. "
                      "Please consult with a mental health professional for clinical advice.")
    content.append(Paragraph(disclaimer_text, styles['AnimoaNormal']))

    # Build the PDF
    doc.build(content)
    buffer.seek(0)
    
    return buffer
    
def mental_health_advisory():
    """Mental Health Advisory questionnaire and recommendations"""
    # Get current language and translations
    current_lang = st.session_state.language if "language" in st.session_state else 'en'
    translations = TRANSLATIONS.get(current_lang, TRANSLATIONS['en'])
    
    st.header("Mental Health Advisory") # Keep this for consistency
    st.subheader("Explore your personalized wellness insights") # Add a friendly subtitle
    #st.write(translations["answer_questions"])
    
    if "questionnaire_submitted" not in st.session_state:
        st.session_state.questionnaire_submitted = False
    
    # Add a section to view previous assessments, but in an expander to keep it clean
    if "user" in st.session_state:
        with st.expander("View Previous Assessments", expanded=False):
            try:
                response = supabase.table('questionnaire_responses').select('id, created_at, responses, recommendations').eq('user_id', st.session_state.user.id).order('created_at', desc=True).execute()
                
                if response.data and len(response.data) > 0:
                    # Process and display assessments as before
                    # Create a DataFrame for display
                    assessments = []
                    
                    for record in response.data:                        
                        created_date = "Unknown date"
                        if 'created_at' in record:
                            import pandas as pd
                            created_date = pd.to_datetime(record['created_at']).strftime('%b %d, %Y %I:%M %p')
                        
                        # Extract mood info from responses
                        mood = "N/A"
                        if 'responses' in record and record['responses'] and 'mood' in record['responses']:
                            mood = record['responses']['mood']
                        
                        assessments.append({
                            'Date': created_date,
                            'Mood': mood,
                            'ID': record['id']
                        })
                    
                    if assessments:
                        # Display as a table with view buttons
                        df = pd.DataFrame(assessments)
                        
                        # Use columns to create a table with buttons
                        cols = st.columns([3, 2, 1, 1])
                        cols[0].write("**Date**")
                        cols[1].write("**Mood**")
                        cols[2].write("**View**")
                        cols[3].write("**Delete**")
                        
                        for i, row in df.iterrows():
                            cols = st.columns([3, 2, 1, 1])
                            cols[0].write(row['Date'])
                            cols[1].write(row['Mood'])
                            
                            # View Button
                            if cols[2].button("📄", key=f"view_{row['ID']}"):
                                st.session_state.viewing_assessment_id = row['ID']
                                st.rerun()
                            
                            # Delete Button
                            if cols[3].button("🗑️", key=f"delete_{row['ID']}"):
                                st.session_state.delete_assessment_id = row['ID']
                                st.rerun()
                    else:
                        st.info("No previous assessments found.")
                else:
                    st.info("Assessment history will be available after your first assessment.")
                    
            except Exception as e:
                st.info("Assessment history will be available after your first assessment.")
                print(f"Error with previous assessments: {str(e)}")
    
    # Handle viewing a specific assessment
    if "viewing_assessment_id" in st.session_state:
        try:
            # Fetch the specific assessment with better error handling
            response = supabase.table('questionnaire_responses').select('*').eq('id', st.session_state.viewing_assessment_id).execute()
            
            if response.data and len(response.data) > 0:
                assessment = response.data[0]
                
                with st.container():  # Change from expander to container
                # Add a back button at the top for easier navigation
                    if st.button("← Back to Assessment", key="back_to_list"):
                        del st.session_state.viewing_assessment_id
                        st.rerun()
                    # Format date - handle case where created_at might be missing
                    created_date = "Unknown date"
                    if 'created_at' in assessment and assessment['created_at']:
                        import pandas as pd
                        created_date = pd.to_datetime(assessment['created_at']).strftime('%B %d, %Y %I:%M %p')
                    
                    st.subheader(f"Assessment from {created_date}")
                    
                    # Display responses with error handling
                    if 'responses' in assessment and assessment['responses']:
                        st.markdown("### Responses:")
                        for key, value in assessment['responses'].items():
                            if key != 'language':  # Skip language field
                                # Handle value formatting
                                display_value = value
                                if isinstance(value, dict) or isinstance(value, list):
                                    # Format complex values
                                    import json
                                    display_value = json.dumps(value, indent=2)
                                st.markdown(f"**{key.capitalize()}**: {display_value}")
                    else:
                        st.info("No detailed responses available for this assessment.")
                    
                    # Display recommendations with error handling
                    if 'recommendations' in assessment and assessment['recommendations']:
                        st.markdown("### Recommendations:")
                        st.markdown(assessment['recommendations'])
                    else:
                        st.info("No recommendations available for this assessment.")
                    
                    # Offer download of this assessment if we have all needed data
                    if 'responses' in assessment and assessment['responses']:
                        # For PDF generation, we need both responses and recommendations
                        recommendations = assessment.get('recommendations', "No recommendations were generated for this assessment.")
                        
                        # Create PDF with error handling
                        try:
                            buffer = create_wellness_pdf(assessment['responses'], recommendations)
                            
                            st.download_button(
                                label="Download This Assessment",
                                data=buffer,
                                file_name=f"Wellness_Assessment_{created_date.replace(':', '-').replace(' ', '_')}.pdf",
                                mime="application/pdf"
                            )
                        except Exception as pdf_error:
                            st.error(f"Could not generate PDF: {str(pdf_error)}")
                            st.write("Please try downloading a more recent assessment instead.")
                    
                    if st.button("Close", key="close_assessment_view"):
                        del st.session_state.viewing_assessment_id
                        st.rerun()
            else:
                st.error("Assessment not found or may have been deleted.")
                # Auto-clear the viewing state after displaying error
                if "viewing_assessment_id" in st.session_state:
                    del st.session_state.viewing_assessment_id
                st.rerun()
        except Exception as e:
            st.error(f"Error viewing assessment: {str(e)}")
            # Add detailed debugging information
            st.write("Assessment ID:", st.session_state.viewing_assessment_id)
            import traceback
            st.text(traceback.format_exc())
            
            back_col, delete_col = st.columns([3, 1])
            with back_col:
                if st.button("← Back to Assessment List", key="back_to_list"):
                    del st.session_state.viewing_assessment_id
                    st.rerun()
            with delete_col:
                if st.button("🗑️ Delete", key="delete_from_view", type="secondary"):
                    st.session_state.delete_assessment_id = st.session_state.viewing_assessment_id
                    st.rerun()
                
    # Handle delete confirmation - make it always appear at the top
    if "delete_assessment_id" in st.session_state:
        # Use a container instead of an expander for consistent positioning
        delete_container = st.container()
        
        with delete_container:
            st.warning("⚠️ Are you sure you want to delete this assessment? This cannot be undone.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Delete It", key="confirm_delete_assessment", type="primary"):
                    try:
                        supabase.table('questionnaire_responses').delete().eq('id', st.session_state.delete_assessment_id).execute()
                        st.success("Assessment deleted successfully.")
                        
                        # Clear both viewing and delete states
                        if "viewing_assessment_id" in st.session_state:
                            del st.session_state.viewing_assessment_id
                        del st.session_state.delete_assessment_id
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting assessment: {str(e)}")
            
            with col2:
                if st.button("Cancel", key="cancel_delete_assessment"):
                    del st.session_state.delete_assessment_id
                    st.rerun()
        
        # Add a separator
        st.markdown("---")
        
    # Define the questions - we'll translate these dynamically based on the selected language
    questions = {
        "en": {
            "mood": "Over the past 2 weeks, how often have you felt down, depressed, or hopeless?",
            "interest": "Over the past 2 weeks, how often have you felt little interest or pleasure in doing things?",
            "anxiety": "Over the past 2 weeks, how often have you felt nervous, anxious, or on edge?",
            "worry": "Over the past 2 weeks, how often have you not been able to stop or control worrying?",
            "sleep": "How would you rate your sleep quality over the past week?",
            "support": "Do you feel you have adequate social support in your life?",
            "coping": "What coping strategies do you currently use when feeling stressed or overwhelmed?"
        },
        "es": {
            "mood": "Durante las últimas 2 semanas, ¿con qué frecuencia se ha sentido deprimido/a o sin esperanzas?",
            "interest": "Durante las últimas 2 semanas, ¿con qué frecuencia ha sentido poco interés o placer en hacer cosas?",
            "anxiety": "Durante las últimas 2 semanas, ¿con qué frecuencia se ha sentido nervioso/a, ansioso/a o con los nervios de punta?",
            "worry": "Durante las últimas 2 semanas, ¿con qué frecuencia no ha sido capaz de parar o controlar sus preocupaciones?",
            "sleep": "¿Cómo calificaría su calidad de sueño durante la última semana?",
            "support": "¿Siente que tiene un apoyo social adecuado en su vida?",
            "coping": "¿Qué estrategias de afrontamiento utiliza actualmente cuando se siente estresado/a o abrumado/a?"
        },
        "zh": {
            "mood": "在过去的2周内，您有多少时间感到情绪低落、沮丧或绝望？",
            "interest": "在过去的2周内，您有多少时间对做事情没有兴趣或乐趣？",
            "anxiety": "在过去的2周内，您有多少时间感到紧张、焦虑或坐立不安？",
            "worry": "在过去的2周内，您有多少时间无法停止或控制担忧？",
            "sleep": "您如何评价过去一周的睡眠质量？",
            "support": "您觉得在生活中有足够的社会支持吗？",
            "coping": "当您感到压力或不知所措时，您目前使用哪些应对策略？"
        }
    }
    
    # Get questions for current language
    current_questions = questions.get(current_lang, questions["en"])
    
    # Options for the rating questions - also translate these
    rating_options = {
        "en": ["Not at all", "Several days", "More than half the days", "Nearly every day"],
        "es": ["En absoluto", "Varios días", "Más de la mitad de los días", "Casi todos los días"],
        "zh": ["完全没有", "有几天", "一半以上的天数", "几乎每天"]
    }
    
    sleep_options = {
        "en": ["Very poor", "Poor", "Fair", "Good", "Very good"],
        "es": ["Muy mala", "Mala", "Regular", "Buena", "Muy buena"],
        "zh": ["非常差", "差", "一般", "好", "非常好"]
    }
    
    support_options = {
        "en": ["No support", "Limited support", "Moderate support", "Strong support"],
        "es": ["Sin apoyo", "Apoyo limitado", "Apoyo moderado", "Apoyo fuerte"],
        "zh": ["没有支持", "有限支持", "适度支持", "强力支持"]
    }
    
    # Get options for current language
    current_rating_options = rating_options.get(current_lang, rating_options["en"])
    current_sleep_options = sleep_options.get(current_lang, sleep_options["en"])
    current_support_options = support_options.get(current_lang, support_options["en"])
    
    # Only show questionnaire if not viewing or deleting past assessments
    if "viewing_assessment_id" not in st.session_state and "delete_assessment_id" not in st.session_state:
        # Create the questionnaire form
        if not st.session_state.questionnaire_submitted:
            with st.form("mental_health_questionnaire"):
                st.write(translations["answer_questions"])
                
                responses = {}
                # No default selections - user must make an active choice
                responses["mood"] = st.radio(current_questions["mood"], current_rating_options, index=None)
                responses["interest"] = st.radio(current_questions["interest"], current_rating_options, index=None)
                responses["anxiety"] = st.radio(current_questions["anxiety"], current_rating_options, index=None)
                responses["worry"] = st.radio(current_questions["worry"], current_rating_options, index=None)
                responses["sleep"] = st.radio(current_questions["sleep"], current_sleep_options, index=None)
                responses["support"] = st.radio(current_questions["support"], current_support_options, index=None)
                responses["coping"] = st.text_area(current_questions["coping"], height=100)
                
                # Add option to include chat history for personalization
                include_chat_history = False
                if "user" in st.session_state and "messages" in st.session_state and st.session_state.messages:
                    st.markdown("---")
                    include_chat_history = st.checkbox(translations["include_chat_history"], 
                                                   help="This will analyze your recent conversations to provide more tailored suggestions")
                
                submit_button = st.form_submit_button(translations["submit_questionnaire"])
                
                if submit_button:
                    # Validate form
                    if None in [responses["mood"], responses["interest"], responses["anxiety"], 
                               responses["worry"], responses["sleep"], responses["support"]] or not responses["coping"]:
                        st.error(translations["questionnaire_error"])
                    else:
                        # Also store the user's language preference with the responses
                        responses["language"] = current_lang
                        
                        # Save responses to database if user is logged in
                        if "user" in st.session_state:
                            try:
                                # Ensure user exists in profiles first
                                ensure_profile_exists(st.session_state.user.id, st.session_state.user.email)
                                
                                # Convert responses to a format suitable for storage
                                response_data = {
                                    'user_id': st.session_state.user.id,
                                    'responses': responses,
                                    'used_chat_history': include_chat_history,
                                    'created_at': datetime.datetime.now().isoformat()  # Add timestamp
                                }
                                
                                # Store in questionnaire_responses table
                                result = supabase.table('questionnaire_responses').insert(response_data).execute()
                                
                                # Check if insertion was successful
                                if result and result.data:
                                    # Get the ID of the new entry to reference it later
                                    st.session_state.latest_assessment_id = result.data[0]['id']
                                
                                st.session_state.questionnaire_submitted = True
                                st.session_state.responses = responses
                                st.session_state.include_chat_history = include_chat_history
                                st.rerun()
                            except Exception as e:
                                st.warning(f"Could not save responses: {str(e)}")
                                
                        # If not logged in or error saving, still show recommendations
                        st.session_state.questionnaire_submitted = True
                        st.session_state.responses = responses
                        st.session_state.include_chat_history = include_chat_history
                        st.rerun()
    
    # Show recommendations if questionnaire is submitted
    if st.session_state.questionnaire_submitted:
        # Generate personalized advice based on responses
        with st.spinner(translations["analyzing_responses"]):
            # Pass the chat history if requested
            chat_history = None
            if st.session_state.get("include_chat_history", False) and "messages" in st.session_state:
                chat_history = st.session_state.messages    
            recommendations = generate_recommendations(st.session_state.responses, chat_history)
            
        # Display recommendations
        st.success(translations["based_on_responses"])
        st.markdown(recommendations)
        
        # Store recommendations if not already stored
        if "user" in st.session_state and "latest_assessment_id" in st.session_state:
            try:
                # Check if recommendations already saved
                if "recommendations_saved" not in st.session_state:
                    # Save recommendations to the database
                    update_data = {
                        'recommendations': recommendations
                    }
                    supabase.table('questionnaire_responses').update(update_data).eq('id', st.session_state.latest_assessment_id).execute()
                    st.session_state.recommendations_saved = True
            except Exception as e:
                print(f"Could not save recommendations: {str(e)}")
                
        # Create the PDF
        buffer = create_wellness_pdf(st.session_state.responses, recommendations)
        
        # Options for the user
        col1, col2 = st.columns(2)
        
        with col1:
            # Download PDF button
            st.download_button(
                label="Download Your Wellness Report",
                data=buffer,
                file_name="Animoa_Wellness_Report.pdf",
                mime="application/pdf"
            )
        
        with col2:
            # Retake Assessment button
            if st.button("Retake Assessment", key="retake_assessment_button", type="secondary"):
                st.session_state.questionnaire_submitted = False
                if "latest_assessment_id" in st.session_state:
                    del st.session_state.latest_assessment_id
                if "recommendations_saved" in st.session_state:
                    del st.session_state.recommendations_saved
                st.rerun()
        
                
def generate_recommendations(responses, chat_history=None):
    """Generate personalized mental health recommendations with optional chat history"""
    try:
        # Get the user's language preference
        user_language = responses.get('language', 'en')
        
        # Language mapping for prompt
        language_names = {
            'en': 'English',
            'es': 'Spanish',
            'zh': 'Mandarin Chinese'
        }
        
        language_name = language_names.get(user_language, 'English')
        
        # Create a base prompt
        system_prompt = f"""You are Animoa, a compassionate mental health companion designed to provide personalized, evidence-based guidance. 
        
        ## USER ASSESSMENT DATA
        A user has completed a validated mental health screening with these responses:
        
        - PHQ-2 Depression Screening:
          * Feeling down or depressed: {responses['mood']}
          * Little interest or pleasure: {responses['interest']}
        
        - GAD-2 Anxiety Screening:
          * Feeling anxious: {responses['anxiety']}
          * Uncontrollable worry: {responses['worry']}
        
        - Additional Wellbeing Factors:
          * Sleep quality: {responses['sleep']}
          * Social support: {responses['support']}
          * Current coping strategies: "{responses['coping']}"
        """
        
        # Add chat history context if available
        if chat_history and len(chat_history) > 0:
            system_prompt += "\n\n## CHAT HISTORY CONTEXT\n"
            system_prompt += "The user has also had conversations with you. Here are relevant excerpts that may provide additional context:\n\n"
            
            # Include up to 10 most recent messages
            recent_messages = chat_history[-min(10, len(chat_history)):]
            for msg in recent_messages:
                role = "User" if msg["role"] == "user" else "You"
                system_prompt += f"- {role}: {msg['content']}\n"
        
        system_prompt += f"""
        ## YOUR TASK
        Analyze these responses using clinical frameworks (like CBT principles, ACT, positive psychology) to provide personalized recommendations. Use a stepped-care approach where appropriate, focusing on self-help strategies while acknowledging when professional support may be beneficial.
        
        IMPORTANT: Provide your response in {language_name}. The user's preferred language is {language_name}, so all of your recommendations should be in {language_name} only.
        
        ## RESPONSE FORMAT
        1. Begin with a brief, compassionate summary of their current situation (2-3 sentences)
        2. Provide 3-4 evidence-based, actionable techniques they can implement immediately
        3. Add 1-2 medium-term practices that could help if consistently applied
        4. If needed, include a gentle suggestion about professional support (without being alarmist)
        
        ## RESPONSE CHARACTERISTICS
        - Warm, encouraging tone that normalizes their experiences
        - Practical, specific suggestions (not generic advice)
        - Focus on small, achievable steps
        - Accessible language (avoid jargon)
        - Maximum 400 words total
        - Use markdown formatting for clarity
        - Balance empathy with practical guidance
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Based on my assessment, what personalized mental wellness recommendations would you suggest?"}
        ]
        
        # Generate response using Groq
        client = Groq(api_key=groq_api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        # Get fallback message in appropriate language
        if 'language' in responses:
            if responses['language'] == 'es':
                return f"""
                # Sus Recomendaciones de Bienestar
                
                Basado en lo que ha compartido, aquí hay algunas prácticas basadas en evidencia que podrían ayudar:
                
                ## Estrategias de Apoyo Inmediato
                * Practique respiración profunda durante 5 minutos cuando se sienta abrumado
                * Establezca una rutina de sueño consistente con un período de relajación
                * Conéctese con una persona que le apoye, aunque sea brevemente
                
                ## Construyendo Resiliencia
                * Considere llevar un diario sobre tres momentos positivos cada día
                * Incorpore gradualmente movimiento físico que se sienta bien para usted
                
                ¡Recuerde que los pequeños pasos importan! Intente solo uno de estos hoy y vea cómo se siente.
                
                (Tuvimos un pequeño problema técnico: {str(e)})
                """
            elif responses['language'] == 'zh':
                return f"""
                # 您的健康见解
                
                根据您分享的内容，以下是一些可能有帮助的循证实践：
                
                ## 即时支持策略
                * 感到不知所措时，进行5分钟的深呼吸练习
                * 建立一个有放松时间的一致睡眠常规
                * 与支持您的人建立联系，即使是短暂的
                
                ## 建立韧性
                * 考虑每天记录三个积极的时刻
                * 逐渐加入让您感觉良好的体育活动
                
                记住小步骤很重要！今天尝试其中一个，看看感觉如何。
                
                (我们遇到了一个小技术问题：{str(e)})
                """
        
        # Default to English
        return f"""
        # Your Wellness Insights
        
        Based on what you've shared, here are some evidence-based practices that might help:
        
        ## Immediate Support Strategies
        * Practice deep breathing for 5 minutes when feeling overwhelmed
        * Establish a consistent sleep routine with a wind-down period
        * Connect with a supportive person, even briefly
        
        ## Building Resilience
        * Consider journaling about three positive moments each day
        * Gradually incorporate physical movement that feels good for you
        
        Remember that small steps matter! Try just one of these today and see how it feels.
        
        (We had a small technical issue: {str(e)})
        """
        
def mood_tracker():
    """Beautiful mood tracking functionality with improved UI and fixed issues"""
    # Get current language and translations
    current_lang = st.session_state.language if "language" in st.session_state else 'en'
    translations = TRANSLATIONS.get(current_lang, TRANSLATIONS['en'])
    
    # Use custom CSS for better styling
    st.markdown("""
    <style>
        .mood-button {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 15px 5px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            height: 100%;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .mood-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .mood-emoji {
            font-size: 2rem;
            margin-bottom: 8px;
        }
        .mood-label {
            font-size: 0.85rem;
        }
        .mood-today {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .mood-today-emoji {
            font-size: 2.5rem;
            margin-right: 15px;
        }
        .mood-calendar-day {
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            color: white;
            min-height: 70px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: 2px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .calendar-date {
            font-size: 0.8rem;
            margin-bottom: 5px;
        }
        .calendar-emoji {
            font-size: 1.5rem;
        }
        .calendar-note {
            font-size: 0.7rem;
            margin-top: 5px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 100%;
        }
        .insights-card {
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            background-color: rgba(255, 255, 255, 0.1);  /* Semi-transparent white background */
            border: 1px solid rgba(255, 255, 255, 0.2);  /* Subtle border */
        }
        .edit-button {
            color: #4e79a7;
            cursor: pointer;
            margin-left: 10px;
            font-size: 1.2rem;
        }
        .edit-button:hover {
            color: #2c5282;
        }
        .toggle-bar {
            display: flex;
            background-color: rgba(240, 242, 246, 0.1);
            border-radius: 8px;
            padding: 5px;
            margin: 10px 0;
        }
        .toggle-option {
            flex: 1;
            text-align: center;
            padding: 8px 0;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
        }
        .toggle-option.active {
            background-color: rgba(255, 255, 255, 0.2); 
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.header("Mood Tracker")
    st.markdown("<p style='font-size: 1.1rem; color: #6c757d; margin-bottom: 25px;'>Track your emotional wellbeing journey</p>", unsafe_allow_html=True)
    
    # Define moods with emojis and colors
    moods = {
        "very_happy": {"emoji": "😊", "label": "Very Happy", "value": 5, "color": "#28a745", "message": "That's wonderful to hear! What contributed to your happiness today?"},
        "happy": {"emoji": "🙂", "label": "Happy", "value": 4, "color": "#8bc34a", "message": "Great! Consider what positive elements made your day good."},
        "neutral": {"emoji": "😐", "label": "Neutral", "value": 3, "color": "#ffc107", "message": "Taking time to reflect on your day can help identify what influences your mood."},
        "sad": {"emoji": "😔", "label": "Sad", "value": 2, "color": "#fd7e14", "message": "It's okay to feel down sometimes. Consider using our chat feature to process your feelings."},
        "very_sad": {"emoji": "😢", "label": "Very Sad", "value": 1, "color": "#dc3545", "message": "I'm sorry you're feeling this way. Reaching out to someone you trust might help."}
    }
    
    # Today's date
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Create tabs for different sections
    st.markdown("### How are you feeling today?")  
      
    # Check if user has already logged mood for today
    has_logged_today = False
    today_mood = None
    today_note = ""
    today_entry_id = None
    
    if "user" in st.session_state:
        try:
            # Check for today's mood entry
            response = supabase.table('mood_logs').select('*').eq('user_id', st.session_state.user.id).eq('date', today).execute()
            
            if response.data and len(response.data) > 0:
                has_logged_today = True
                today_mood = response.data[0]['mood']
                today_note = response.data[0].get('note', '')
                today_entry_id = response.data[0]['id']
        except Exception as e:
            st.warning(f"Could not check mood logs: {str(e)}")
    
    # Display previous mood if logged today
    if has_logged_today and "edit_mood" not in st.session_state:
        mood_data = moods[today_mood]
        
        # Nice display for today's mood with edit button
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(f"""
            <div class="mood-today" style="background-color: {mood_data['color']}20; border-left: 5px solid {mood_data['color']};">
                <div class="mood-today-emoji">{mood_data['emoji']}</div>
                <div>
                    <h3 style="margin: 0; color: {mood_data['color']};">{mood_data['label']}</h3>
                    <p style="font-style: italic; margin-top: 5px;">{today_note if today_note else 'No notes added'}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("✏️", help="Edit"):
                st.session_state.edit_mood = True
                st.rerun()
    
    # Show mood logging interface if not yet logged today or in edit mode
    if not has_logged_today or "edit_mood" in st.session_state:
        if "edit_mood" in st.session_state:
            st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
        
        # Create a row of mood buttons with better styling
        cols = st.columns(len(moods))
        
        # For tracking selected mood in session state
        if "selected_mood" not in st.session_state:
            st.session_state.selected_mood = today_mood if today_mood else None
        
        # Replace the mood selection code with this simpler approach:
        for i, (mood_key, mood_data) in enumerate(moods.items()):
            with cols[i]:
                # Create a simple button with emojis
                button_label = f"{mood_data['emoji']}\n{mood_data['label']}"
                
                # Add custom styling for selected mood
                is_selected = st.session_state.selected_mood == mood_key
                button_type = "primary" if is_selected else "secondary"
                
                # Create the button with styling
                if st.button(
                    button_label,
                    key=f"mood_{mood_key}",
                    use_container_width=True,
                    type=button_type
                ):
                    st.session_state.selected_mood = mood_key
                    st.rerun()
        
        # If a mood is selected
        if st.session_state.selected_mood:
            selected_mood = st.session_state.selected_mood
            mood_data = moods[selected_mood]
            
            # Show feedback based on selected mood
            st.markdown(f"""
            <div style="background-color: {mood_data['color']}20; padding: 15px; border-radius: 10px; margin: 20px 0; border-left: 5px solid {mood_data['color']};">
                <p style="margin: 0;">{mood_data['message']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Journal prompt based on mood
            st.markdown("### Reflect on your day")
            st.markdown("_Taking a moment to reflect can help you understand your emotions better._")
            journal_placeholder = "You may add something like: What contributed to your mood today? What happened that made you feel this way?, this is optional"
            mood_note = st.text_area("", value=today_note if today_mood else "", 
                        placeholder=journal_placeholder, key="mood_note", 
                        height=100)
            
            # Save button with better styling
            save_col1, save_col2 = st.columns([3, 1])
            with save_col2:
                if st.button("Save", type="primary", use_container_width=True):
                    try:
                        # Check if updating or creating
                        if today_entry_id:
                            # Update existing entry
                            supabase.table('mood_logs').update({
                                'mood': selected_mood,
                                'note': mood_note
                            }).eq('id', today_entry_id).execute()
                        else:
                            # Create new entry
                            supabase.table('mood_logs').insert({
                                'user_id': st.session_state.user.id,
                                'date': today,
                                'mood': selected_mood,
                                'note': mood_note
                            }).execute()
                        
                        # Reset selected mood and edit mode and show success
                        st.session_state.selected_mood = None
                        if "edit_mood" in st.session_state:
                            del st.session_state.edit_mood
                        st.success("Your mood has been saved successfully!")
                        time.sleep(1)  # Brief pause for user to see success
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not save mood: {str(e)}")
            
            with save_col1:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.selected_mood = None
                    if "edit_mood" in st.session_state:
                        del st.session_state.edit_mood
                    st.rerun()
    
    st.markdown("---")
    st.markdown("### Your Mood Journey")
    
    # Initialize session state variables if they don't exist
    if "selected_time_range" not in st.session_state:
        st.session_state.selected_time_range = "week"
        
    if "selected_view" not in st.session_state:
        st.session_state.selected_view = "calendar"
    
    # Custom dropdowns for display options and time range
    col1, col2 = st.columns(2)

    with col1:
        # View options in a dropdown
        view_options = {
            "calendar": "Calendar View",
            "trend": "Mood Trend",
            "patterns": "Mood Patterns" 
        }
        
        selected_view = st.selectbox(
            "Display as:",
            options=list(view_options.keys()),
            format_func=lambda x: view_options[x],
            index=list(view_options.keys()).index(st.session_state.selected_view),
            key="view_selector"
        )
        
        if selected_view != st.session_state.selected_view:
            st.session_state.selected_view = selected_view
            st.rerun()

    with col2:
        # Time range options in a dropdown
        time_options = {
            "week": "Last 7 days",
            "month": "Last 30 days",
            "3months": "Last 3 months",
            "all": "All time"
        }
        
        selected_range = st.selectbox(
            "Time period:",
            options=list(time_options.keys()),
            format_func=lambda x: time_options[x],
            index=list(time_options.keys()).index(st.session_state.selected_time_range),
            key="time_selector"
        )
        
        if selected_range != st.session_state.selected_time_range:
            st.session_state.selected_time_range = selected_range
            st.rerun()
        
    # Convert range to days
    days_lookup = {
        "week": 7,
        "month": 30,
        "3months": 90,
        "all": 9999  # Effectively all records
    }
    days_to_fetch = days_lookup[st.session_state.selected_time_range]
    
    try:
        # Get date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days_to_fetch)
        
        # Fetch mood history for selected range
        response = supabase.table('mood_logs').select('*')\
            .eq('user_id', st.session_state.user.id)\
            .gte('date', start_date.strftime("%Y-%m-%d"))\
            .order('date', desc=False).execute()
        
        if response.data and len(response.data) > 0:
            # Import pandas for data manipulation
            import pandas as pd
            import altair as alt
            
            # Prepare data for visualization
            df = pd.DataFrame(response.data)
            df['date'] = pd.to_datetime(df['date'])
            df['mood_value'] = df['mood'].map(lambda x: moods[x]['value'])
            df['mood_emoji'] = df['mood'].map(lambda x: moods[x]['emoji'])
            df['mood_label'] = df['mood'].map(lambda x: moods[x]['label'])
            df['mood_color'] = df['mood'].map(lambda x: moods[x]['color'])
            df['day'] = df['date'].dt.strftime('%a, %b %d')
            
            # Draw appropriate visualization based on selected view
            if st.session_state.selected_view == "calendar":
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                
                # Group by month if showing more than a week
                if days_to_fetch > 7:
                    df['month'] = df['date'].dt.strftime('%B %Y')
                    months = df['month'].unique()
                    
                    for month in months:
                        st.markdown(f"#### {month}")
                        month_data = df[df['month'] == month]
                        
                        # Create weekly calendar rows
                        for i in range(0, len(month_data), 7):
                            week_data = month_data.iloc[i:min(i+7, len(month_data))]
                            cols = st.columns(7)
                            
                            for j, (_, row) in enumerate(week_data.iterrows()):
                                if j < len(cols):
                                    with cols[j]:
                                        day = row['date'].strftime('%d')
                                        emoji = row['mood_emoji']
                                        note = row.get('note', '')
                                        note_preview = note[:20] + '...' if note and len(note) > 20 else note
                                        
                                        st.markdown(f"""
                                        <div class="mood-calendar-day" style="background-color: {row['mood_color']};">
                                            <div class="calendar-date">{day}</div>
                                            <div class="calendar-emoji">{emoji}</div>
                                            <div class="calendar-note">{note_preview}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Add popup to view full note if present
                                        if note and st.button("View", key=f"view_note_{row['id']}"):
                                            st.session_state.viewing_note = row['id']
                                            st.session_state.note_content = note
                                            st.session_state.note_date = row['date'].strftime('%A, %B %d')
                                            st.session_state.note_mood = row['mood_label']
                                            st.rerun()
                else:
                    # Just show the week view
                    cols = st.columns(min(7, len(df)))
                    
                    for i, (_, row) in enumerate(df.iterrows()):
                        if i < len(cols):
                            with cols[i]:
                                day = row['date'].strftime('%a\n%b %d')
                                emoji = row['mood_emoji']
                                note = row.get('note', '')
                                note_preview = note[:20] + '...' if note and len(note) > 20 else note
                                
                                st.markdown(f"""
                                <div class="mood-calendar-day" style="background-color: {row['mood_color']};">
                                    <div class="calendar-date">{day}</div>
                                    <div class="calendar-emoji">{emoji}</div>
                                    <div class="calendar-note">{note_preview}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Add popup to view full note if present
                                if note and st.button("View", key=f"view_note_{row['id']}"):
                                    st.session_state.viewing_note = row['id']
                                    st.session_state.note_content = note
                                    st.session_state.note_date = row['date'].strftime('%A, %B %d')
                                    st.session_state.note_mood = row['mood_label']
                                    st.rerun()
                
                # Note popup/modal
                if "viewing_note" in st.session_state:
                    with st.expander(f"Journal Entry: {st.session_state.note_date} - {st.session_state.note_mood}", expanded=True):
                        st.markdown(f"**{st.session_state.note_date}**")
                        st.write(st.session_state.note_content)
                        if st.button("Close", key="close_note"):
                            del st.session_state.viewing_note
                            st.rerun()
            
            elif st.session_state.selected_view == "trend":
                # Create a more visually appealing line chart
                df['day_num'] = range(len(df))
                
                # Basic chart with improved styling
                line_chart = alt.Chart(df).mark_line(
                    point=True,
                    strokeWidth=3,
                    interpolate='monotone'
                ).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('mood_value:Q', 
                            title='Mood',
                            scale=alt.Scale(domain=[1, 5]),
                            axis=alt.Axis(
                                values=[1, 2, 3, 4, 5],
                                labelExpr="datum.value == 1 ? 'Very Sad' : datum.value == 2 ? 'Sad' : datum.value == 3 ? 'Neutral' : datum.value == 4 ? 'Happy' : 'Very Happy'"
                            )),
                    color=alt.value('#4e79a7'),
                    tooltip=['day:N', 'mood_label:N', 'note:N']
                ).properties(
                    width='container',
                    height=350
                ).interactive()
                
                # Add points with mood emoji
                points = alt.Chart(df).mark_point(
                    size=100,
                    filled=True
                ).encode(
                    x='date:T',
                    y='mood_value:Q',
                    color=alt.Color('mood_color:N', scale=None),
                    tooltip=['day:N', 'mood_label:N']
                )
                
                # Combine and display
                st.altair_chart(line_chart + points, use_container_width=True)
                
                # Add trend analysis in a card - now with adaptive colors
                if len(df) > 1:
                    recent_avg = df['mood_value'].tail(min(3, len(df))).mean()
                    overall_avg = df['mood_value'].mean()
                    
                    trend = "improving" if recent_avg > overall_avg + 0.3 else \
                            "declining" if recent_avg < overall_avg - 0.3 else "stable"
                    
                    # Calculate most frequent mood in selected period
                    freq_mood = df['mood_label'].value_counts().index[0]
                    freq_emoji = df.loc[df['mood_label'] == freq_mood, 'mood_emoji'].iloc[0]
                    
                    trend_color = '#28a745' if trend == 'improving' else '#dc3545' if trend == 'declining' else '#ffc107'
                    
                    insight_text = f"""
                    <div class="insights-card">
                        <h4 style="color: #31505E;">Mood Insights</h4>
                        <p style="color: #31505E;"><strong>Trend:</strong> Your mood has been <span style="color: {trend_color};">{trend}</span> during this period.</p>
                        <p style="color: #31505E;"><strong>Most common mood:</strong> {freq_emoji} {freq_mood}</p>
                        <p style="color: #31505E;"><strong>Average mood:</strong> {overall_avg:.1f}/5</p>
                    </div>
                    """
                    st.markdown(insight_text, unsafe_allow_html=True)
            
            elif st.session_state.selected_view == "patterns":
                # Create mood distribution visualization
                st.markdown("#### Your Mood Distribution")
                
                # Count moods and create dataframe for visualization
                mood_counts = df['mood'].value_counts().reset_index()
                mood_counts.columns = ['mood', 'count']
                mood_counts['emoji'] = mood_counts['mood'].map(lambda x: moods[x]['emoji'])
                mood_counts['label'] = mood_counts['mood'].map(lambda x: moods[x]['label'])
                mood_counts['color'] = mood_counts['mood'].map(lambda x: moods[x]['color'])
                
                # Sort by mood value for consistent order
                mood_value_map = {k: v['value'] for k, v in moods.items()}
                mood_counts['value'] = mood_counts['mood'].map(mood_value_map)
                mood_counts = mood_counts.sort_values('value', ascending=False)
                
                # Create bar chart with emoji labels and HORIZONTAL text orientation
                bars = alt.Chart(mood_counts).mark_bar().encode(
                    x=alt.X('label:N', title='Mood', sort=None, axis=alt.Axis(labelAngle=0)),  # Horizontal labels
                    y=alt.Y('count:Q', title='Number of Days'),
                    color=alt.Color('color:N', scale=None),
                    tooltip=['label:N', 'count:Q']
                ).properties(
                    width='container',
                    height=300
                )
                
                # Add emoji text above bars
                text = bars.mark_text(
                    align='center',
                    baseline='bottom',
                    dy=-10,
                    fontSize=20
                ).encode(
                    text='emoji:N'
                )
                
                # Display chart
                st.altair_chart(bars + text, use_container_width=True)
                
                # Weekly patterns section
                if len(df) >= 7:
                    st.markdown("#### Weekly Patterns")
                    
                    # Add day of week and create aggregation
                    df['day_of_week'] = df['date'].dt.dayofweek
                    df['day_name'] = df['date'].dt.day_name()
                    
                    # Get average mood by day of week
                    day_avg = df.groupby(['day_of_week', 'day_name'])['mood_value'].mean().reset_index()
                    
                    # Sort by day of week
                    day_avg = day_avg.sort_values('day_of_week')
                    
                    # Create day of week visualization with HORIZONTAL labels
                    day_chart = alt.Chart(day_avg).mark_bar().encode(
                        x=alt.X('day_name:N', title='Day', sort=None, axis=alt.Axis(labelAngle=0)),
                        y=alt.Y('mood_value:Q', title='Average Mood', scale=alt.Scale(domain=[1, 5])),
                        color=alt.Color('mood_value:Q', 
                                        scale=alt.Scale(domain=[1, 5], 
                                                    range=['#dc3545', '#fd7e14', '#ffc107', '#8bc34a', '#28a745']),
                                        legend=None)
                    ).properties(
                        width='container',
                        height=250
                    )
                    
                    st.altair_chart(day_chart, use_container_width=True)
                    
                    # Find best and worst days
                    best_day = day_avg.loc[day_avg['mood_value'].idxmax()]
                    worst_day = day_avg.loc[day_avg['mood_value'].idxmin()]
                    
                    # Display insights about best/worst days with better contrast
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div style="background-color: rgba(40, 167, 69, 0.2); padding: 15px; border-radius: 10px; height: 100%;">
                            <h5 style="margin-top: 0; color: rgba(255, 255, 255, 0.9);">Best Day</h5>
                            <p style="font-size: 1.5rem; margin: 0; color: rgba(255, 255, 255, 0.9);">{best_day['day_name']}</p>
                            <p style="color: rgba(255, 255, 255, 0.9);">Average mood: {best_day['mood_value']:.1f}/5</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col2:
                        st.markdown(f"""
                        <div style="background-color: rgba(220, 53, 69, 0.2); padding: 15px; border-radius: 10px; height: 100%;">
                            <h5 style="margin-top: 0; color: rgba(255, 255, 255, 0.9);">Most Challenging Day</h5>
                            <p style="font-size: 1.5rem; margin: 0; color: rgba(255, 255, 255, 0.9);">{worst_day['day_name']}</p>
                            <p style="color: rgba(255, 255, 255, 0.9);">Average mood: {worst_day['mood_value']:.1f}/5</p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            # No data available
            st.info("Start tracking your mood to see patterns and insights here.")
            
            # Show sample visualization as placeholder
            st.markdown("#### Sample Visualization (Your data will appear here)")
            sample_data = pd.DataFrame({
                'date': pd.date_range(start=datetime.datetime.now() - datetime.timedelta(days=6), periods=7),
                'mood_value': [3, 4, 4, 5, 3, 4, 4],
                'mood_label': ['Neutral', 'Happy', 'Happy', 'Very Happy', 'Neutral', 'Happy', 'Happy'],
                'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            })
            
            sample_chart = alt.Chart(sample_data).mark_line(
                point=True,
                strokeWidth=3,
                strokeDash=[5, 5],  # Make it dashed to indicate sample data
                color='#cccccc'
            ).encode(
                x=alt.X('date:T', title='Date'),
                y=alt.Y('mood_value:Q', title='Mood', scale=alt.Scale(domain=[1, 5])),
                tooltip=['day:N', 'mood_label:N']
            ).properties(
                width='container',
                height=300
            )
            
            st.altair_chart(sample_chart, use_container_width=True)
            st.caption("This is a sample visualization. Your actual mood data will appear here.")
            
    except Exception as e:
        st.warning(f"Could not load mood history: {str(e)}")
        st.error(f"Error details: {str(e)}")

# Function to show feedback form when logging out
def show_logout_feedback_form():
    """Show a clean logout feedback form with normal layout"""
    # Create a container with normal width
    container = st.container()
    
    with container:
        # Center-align content
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:  # Use the middle column for the form to create a normal width layout
            st.subheader("Before you go...")
            st.write("How was your experience with Animoa today?")
            
            # Init rating in session state
            if "logout_rating" not in st.session_state:
                st.session_state.logout_rating = 0
            
            # Simple rating with stars 1-5
            rating_cols = st.columns(5)
            for i in range(5):
                with rating_cols[i]:
                    # Show filled or empty star based on current rating
                    star = "★" if i < st.session_state.logout_rating else "☆"
                    if st.button(star, key=f"star_{i+1}"):
                        st.session_state.logout_rating = i + 1
                        st.rerun()
            
            # Rating text
            rating_texts = ["", "Poor", "Fair", "Good", "Very Good", "Excellent"]
            if st.session_state.logout_rating > 0:
                st.write(f"You selected: {rating_texts[st.session_state.logout_rating]}")
            
            # Comment field
            feedback = st.text_area(
                "Any thoughts before you go? (optional)",
                max_chars=200
            )
            
            # Action buttons
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button("Submit & Logout", key="submit_logout", type="primary", use_container_width=True):
                    # Save feedback
                    if st.session_state.logout_rating > 0:
                        try:
                            feedback_data = {
                                'rating': st.session_state.logout_rating,
                                'feedback_text': feedback,
                                'session_type': 'logout',
                                'user_id': st.session_state.user.id if "user" in st.session_state else None
                            }
                            supabase.table('user_feedback').insert(feedback_data).execute()
                        except:
                            pass
                    
                    st.success("Thank you for your feedback!")
                    time.sleep(1)
                    return True
            
            with btn_col2:
                if st.button("Just Logout", key="skip_logout", use_container_width=True):
                    return True
            
            # Add cancel button below
            if st.button("Cancel", key="cancel_logout", use_container_width=True):
                st.session_state.show_logout_feedback = False
                st.rerun()
    
    return False

def about_section():
    """Display information about the app and its features"""
    # Get current language and translations
    current_lang = st.session_state.language if "language" in st.session_state else 'en'
    translations = TRANSLATIONS.get(current_lang, TRANSLATIONS['en'])
    
    st.header(translations["about_title"])
    st.subheader(translations["about_subtitle"])
    
    # Mission statement
    st.markdown("""
    ### Our Mission
    Animoa was created to provide a private, accessible space for self-reflection and mental wellness support, 
    available whenever you need it. We believe that technology can be harnessed to support mental well-being 
    in a compassionate, user-friendly way that complements traditional mental health care.
    """)
    
    # App description
    st.markdown(translations["about_description"])
    
    # Technical transparency
    st.markdown("""
    ### How Animoa Works
    Animoa is powered by state-of-the-art large language model technology (Llama 3.3) that allows it to understand 
    and respond to your messages with empathy and insight. Your conversations are processed securely, and we 
    continuously improve our system to better support your mental well-being.
    """)
    
    # Data privacy 
    st.info("""
    **Data Privacy**: Your privacy matters to us. Animoa stores your conversations securely to provide personalized 
    support, but never shares your personal information with third parties. You can delete your data at any time 
    from your profile settings.
    """)
    
    # Features section
    st.markdown(f"## {translations['features_heading']}")
    
    # Chat feature
    st.markdown(f"### {translations['chat_heading']}")
    st.markdown(translations["chat_description"])
    
    # Wellness feature
    st.markdown(f"### {translations['wellness_heading']}")
    st.markdown(translations["wellness_description"])
    
    # Mood tracking
    st.markdown("### 📊 Mood Tracker")
    st.markdown("Track your emotional states over time with a simple visual tool. Identifying patterns in your mood can help you better understand your mental health journey.")
    
    # Profile feature
    st.markdown(f"### {translations['profile_heading']}")
    st.markdown(translations["profile_description"])
    
    # Precaution note in a warning box
    st.warning(f"**{translations['precaution_heading']}**: {translations['precaution_text']}")
    
    # Feedback section
    st.markdown(f"## {translations['feedback_heading']}")
    st.markdown(translations["feedback_description"])
    
    # Feedback form in an expander
    with st.expander(translations.get("leave_feedback", "Leave Feedback")):
        with st.form("feedback_form"):
            # Overall rating
            overall_rating = st.slider(
                translations.get("overall_experience", "Overall experience"), 
                min_value=1, 
                max_value=5, 
                value=4
            )
            
            # Feature specific feedback - multi-select
            features = [
                translations.get("chat_feature", "Chat with Animoa"),
                translations.get("wellness_feature", "Mental Health Advisory"),
                translations.get("profile_feature", "Profile Management"),
                "Mood Tracker"
            ]
            selected_features = st.multiselect(
                translations.get("which_features_used", "Which features did you use?"),
                options=features
            )
            
            # Open feedback
            feedback_text = st.text_area(
                translations.get("additional_feedback", "Any additional thoughts or suggestions?"),
                placeholder=translations.get("feedback_placeholder", "Your thoughts help us improve...")
            )
            
            # Anonymous checkbox
            anonymous = st.checkbox(translations.get("submit_anonymously", "Submit anonymously"))
            
            submit_button = st.form_submit_button(translations.get("submit_feedback", "Submit Feedback"))
            
            if submit_button:
                try:
                    # Prepare feedback data
                    feedback_data = {
                        'rating': overall_rating,
                        'features_used': selected_features,
                        'feedback_text': feedback_text,
                        'anonymous': anonymous
                    }
                    
                    # Add user_id if not anonymous
                    if not anonymous and "user" in st.session_state:
                        feedback_data['user_id'] = st.session_state.user.id
                    
                    # Save to database
                    supabase.table('user_feedback').insert(feedback_data).execute()
                    
                    st.success(translations.get("feedback_received", "Thank you for your feedback!"))
                except Exception as e:
                    st.error(f"Error saving feedback: {str(e)}")

def main():
    # Restore Supabase session with retry logic , if tokens exist
    if "access_token" in st.session_state and "refresh_token" in st.session_state:
        max_retries = 3
        retry_delay = 1  # seconds
        for attempt in range(max_retries):
            try:
                supabase.auth.set_session(
                    st.session_state.access_token, st.session_state.refresh_token
                )
                break  # If successful, exit the loop
            except AuthRetryableError as e:
                st.warning(
                    f"Connection to authentication service failed (attempt {attempt + 1}/{max_retries}). Retrying..."
                )
                time.sleep(retry_delay)
        else:  # If the loop completes without breaking (all retries failed)
            st.error(
                "Failed to connect to authentication service. Please check your internet connection and try again."
            )
            st.stop()  # Stop further execution (optional, might want to redirect to login)

    # Set default language if not set
    if "language" not in st.session_state:
        st.session_state.language = 'en'
    
    # Get translations for current language
    current_lang = st.session_state.language
    translations = TRANSLATIONS.get(current_lang, TRANSLATIONS['en'])
    
    # For logout flow
    if "show_logout_feedback" not in st.session_state:
        st.session_state.show_logout_feedback = False
    
    # If showing logout feedback, ONLY show that and nothing else
    if st.session_state.show_logout_feedback:
        should_logout = show_logout_feedback_form()
        
        if should_logout:
            # Clear the session in Supabase
            try:
                supabase.auth.sign_out()
            except:
                pass
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
        # Stop execution here to prevent showing the main UI
        st.stop()
    
    # Check if user is logged in
    is_logged_in = auth_ui(supabase)
    
    if not is_logged_in:
        # Show info for non-logged in users
        st.stop()
    
    # If menu not in session state, default to Chat
    if "menu" not in st.session_state:
        st.session_state.menu = "Chat"
    
    # Create a navigation bar with buttons
    col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
    
    with col1:
        st.write("# Animoa 🧠")
    
    with col2:
        if st.button(translations["chat"], key="nav_chat", use_container_width=True, 
                   type="primary" if st.session_state.menu == "Chat" else "secondary"):
            st.session_state.menu = "Chat"
            st.rerun()
    
    with col3:
        if st.button("📊 Wellness Insights", key="nav_wellness", use_container_width=True,
                   type="primary" if st.session_state.menu == "Advisory" else "secondary"):
            st.session_state.menu = "Advisory"
            st.rerun()
    
    with col4:
        if st.button("😊 Mood", key="nav_mood", use_container_width=True,
                type="primary" if st.session_state.menu == "Mood" else "secondary"):
            st.session_state.menu = "Mood"
            st.rerun()
            
    with col5:
        if st.button(translations["profile"], key="nav_profile", use_container_width=True,
                type="primary" if st.session_state.menu == "Profile" else "secondary"):
            st.session_state.menu = "Profile"
            st.rerun()
        
    with col6:
        if st.button(translations["about"], key="nav_about", use_container_width=True,
                type="primary" if st.session_state.menu == "About" else "secondary"):
            st.session_state.menu = "About"
            st.rerun()
        
    # Display the selected page
    if st.session_state.menu == "Profile":
        profile_manager(supabase)
    elif st.session_state.menu == "Chat":
        chatbot = MentalHealthChatbot()
        chatbot.run()
    elif st.session_state.menu == "Advisory":
        mental_health_advisory()
    elif st.session_state.menu == "About":
        about_section()
    elif st.session_state.menu == "Mood":
        mood_tracker()
    
    # Add the logout button to sidebar with the new feedback form
    # Add this at the end of the main function
    with st.sidebar:
        # Add a spacer to push the logout button to the bottom
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        # Add a visual separator
        st.markdown("---")
        
        # Add the logout button at the bottom of the sidebar
        if st.button("👋 " + translations["logout"], key="sidebar_logout_main", use_container_width=True):
            st.session_state.show_logout_feedback = True
            st.rerun()
            
if __name__ == "__main__":
    main()