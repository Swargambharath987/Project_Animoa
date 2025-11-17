import streamlit as st
from groq import Groq
from supabase import create_client, Client
from dotenv import load_dotenv
import pandas as pd
import datetime
import os

# Dictionary for UI translations - English, Spanish, and Mandarin Chinese
TRANSLATIONS = {
    "en": {
        "welcome": "Welcome to Animoa🧠💬",
        "login": "Login",
        "signup": "Sign Up",
        "email": "Email",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "logout": "Logout",
        "chat": "💬 Chat",
        "wellness": "📊 Wellness",
        "profile": "👤 Profile",
        "new_chat": "➕ New Chat",
        "chat_placeholder": "Share what's on your mind...",
        "welcome_message": "Welcome to your safe space",
        "welcome_subtitle": "How are you feeling today? I'm here to listen and chat whenever you're ready.",
        "translate_history": "Translate conversation history",
        "language": "Language"
    },
    "es": {
        "welcome": "Bienvenido a Animoa🧠💬",
        "login": "Iniciar sesión",
        "signup": "Registrarse",
        "email": "Correo electrónico",
        "password": "Contraseña",
        "confirm_password": "Confirmar Contraseña",
        "logout": "Cerrar sesión",
        "chat": "💬 Chat",
        "wellness": "📊 Bienestar",
        "profile": "👤 Perfil",
        "new_chat": "➕ Nuevo Chat",
        "chat_placeholder": "Comparte lo que piensas...",
        "welcome_message": "Bienvenido a tu espacio seguro",
        "welcome_subtitle": "¿Cómo te sientes hoy? Estoy aquí para escucharte y charlar cuando estés listo.",
        "translate_history": "Traducir historial de conversación",
        "language": "Idioma"
    },
    "zh": {
        "welcome": "欢迎来到 Animoa🧠💬",
        "login": "登录",
        "signup": "注册",
        "email": "电子邮件",
        "password": "密码",
        "confirm_password": "确认密码",
        "logout": "登出",
        "chat": "💬 聊天",
        "wellness": "📊 健康",
        "profile": "👤 个人资料",
        "new_chat": "➕ 新对话",
        "chat_placeholder": "分享您的想法...",
        "welcome_message": "欢迎来到您的安全空间",
        "welcome_subtitle": "今天感觉如何？我随时准备倾听和交流。",
        "translate_history": "翻译对话历史",
        "language": "语言"
    }
}

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
        
        if st.sidebar.button(translations["logout"], key="sidebar_logout_button"):
            # Clear the session in Supabase first
            try:
                supabase.auth.sign_out()
            except:
                pass
            # Then clear session state
            for key in ['user', 'logged_in', 'messages', 'access_token', 'refresh_token']:
                if key in st.session_state:
                    del st.session_state[key]
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
    
    # Create columns for a cleaner layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🧠")
        
    with col2:
        st.markdown("### Your Mental Health Companion")
        st.write("Sign in to access personalized mental health support")
    
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
    st.header("Your Profile")
    
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
    translations = TRANSLATIONS.get(current_lang, TRANSLATIONS['en'])
    
    # Profile form with enhanced UI
    st.markdown("### Personal Details")
    st.write("This information helps us personalize your experience.")
    
    col1, col2 = st.columns(2)
    
    with st.form("profile_form"):
        with col1:
            full_name = st.text_input("Name", value=existing_data.get('full_name', ''))
            age = st.number_input("Age", min_value=13, max_value=120, value=existing_data.get('age', 30))
        
        with col2:
            stress_level = st.selectbox(
                "Current Stress Level", 
                ["Low", "Moderate", "High", "Very High"],
                index=["Low", "Moderate", "High", "Very High"].index(existing_data.get('stress_level', 'Moderate')) if existing_data.get('stress_level') else 1
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
        
        st.markdown("### Mental Wellness Goals")
        goals = st.text_area(
            "What are you hoping to achieve with Animoa?", 
            value=existing_data.get('goals', ''),
            placeholder="e.g., Manage anxiety, improve sleep, develop coping skills..."
        )
        
        interests = st.text_area(
            "Activities that bring you joy or peace", 
            value=existing_data.get('interests', ''),
            placeholder="e.g., Reading, meditation, walking in nature..."
        )
        
        submit_button = st.form_submit_button("Save Profile")
        
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
                
                st.success("Profile updated successfully!")
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
                for msg in response.data:
                    if msg['sender'] == 'user':
                        st.session_state.messages.append({"role": "user", "content": msg['message']})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": msg['message']})
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
                    'sender': 'user' if role == 'user' else 'bot'
                }
                
                if role == "feedback" and message_index is not None:
                    message_data['feedback_for_message_index'] = message_index
                    message_data['sender'] = 'feedback' #overwrite the sender
                
                supabase.table('chat_history').insert(message_data).execute()
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
            
            with chat_interface:
                # Option to translate conversation history
                if st.session_state.messages:
                    if st.button(translations['translate_history']):
                        # This would be where you'd call a translation API to translate messages
                        with st.spinner("Translating..."):
                            st.session_state.messages = self.translate_messages(st.session_state.messages, current_lang)
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
                            if message["role"] == "assistant":
                                # Add feedback buttons
                                cols = st.columns(2)  # Create two columns for the buttons
                                with cols[0]:
                                    if st.button("👍", key=f"thumb_up_{i}", use_container_width=True):
                                        self.save_message("feedback", "👍", i)  # Save positive feedback
                                        st.success("Thank you for your feedback!")
                                        st.rerun()  # Refresh to prevent duplicate feedback
                                with cols[1]:
                                    if st.button("👎", key=f"thumb_down_{i}", use_container_width=True):
                                        self.save_message("feedback", "👎", i)  # Save negative feedback
                                        st.warning("Thank you for your feedback.")
                                        st.rerun()  # Refresh to prevent duplicate feedback
                                        
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
                if msg["role"] == "user":
                    # Simply mark user messages as translated (in production would actually translate)
                    translated_messages.append({
                        "role": "user", 
                        "content": f"[Translated to {target_lang_name}] {msg['content']}"
                    })
                else:
                    # For assistant messages, we can use Groq to generate a proper translation
                    system_prompt = f"You are a precise translator. Translate the following message to {target_lang_name}. Keep the same tone and meaning."
                    
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
                        "role": "assistant",
                        "content": translated_content
                    })
                    
            return translated_messages
        except Exception as e:
            st.warning(f"Translation error: {str(e)}")
            return messages  # Return original messages if translation fails
    
def mental_health_advisory():
    """Mental Health Advisory questionnaire and recommendations"""
    st.header("Mental Health Advisory")
    st.write("Answer a few questions to receive personalized mental health recommendations.")
    
    if "questionnaire_submitted" not in st.session_state:
        st.session_state.questionnaire_submitted = False
    
    # Define the questions based on validated mental health assessments
    # PHQ-2 (depression screening), GAD-2 (anxiety screening), and additional well-being questions
    questions = {
        "mood": "Over the past 2 weeks, how often have you felt down, depressed, or hopeless?",
        "interest": "Over the past 2 weeks, how often have you felt little interest or pleasure in doing things?",
        "anxiety": "Over the past 2 weeks, how often have you felt nervous, anxious, or on edge?",
        "worry": "Over the past 2 weeks, how often have you not been able to stop or control worrying?",
        "sleep": "How would you rate your sleep quality over the past week?",
        "support": "Do you feel you have adequate social support in your life?",
        "coping": "What coping strategies do you currently use when feeling stressed or overwhelmed?"
    }
    
    # Options for the rating questions
    rating_options = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
    sleep_options = ["Very poor", "Poor", "Fair", "Good", "Very good"]
    support_options = ["No support", "Limited support", "Moderate support", "Strong support"]
    
    # Create the questionnaire form
    if not st.session_state.questionnaire_submitted:
        with st.form("mental_health_questionnaire"):
            st.write("Please answer these questions honestly to receive the most helpful recommendations:")
            
            responses = {}
            # No default selections - user must make an active choice
            responses["mood"] = st.radio(questions["mood"], rating_options, index=None)
            responses["interest"] = st.radio(questions["interest"], rating_options, index=None)
            responses["anxiety"] = st.radio(questions["anxiety"], rating_options, index=None)
            responses["worry"] = st.radio(questions["worry"], rating_options, index=None)
            responses["sleep"] = st.radio(questions["sleep"], sleep_options, index=None)
            responses["support"] = st.radio(questions["support"], support_options, index=None)
            responses["coping"] = st.text_area(questions["coping"], height=100)
            
            # Add option to include chat history for personalization
            include_chat_history = False
            if "user" in st.session_state and "messages" in st.session_state and st.session_state.messages:
                st.markdown("---")
                include_chat_history = st.checkbox("Include my chat history for more personalized recommendations", 
                                               help="This will analyze your recent conversations to provide more tailored suggestions")
            
            submit_button = st.form_submit_button("Get Recommendations")
            
            if submit_button:
                # Validate form
                if None in [responses["mood"], responses["interest"], responses["anxiety"], 
                           responses["worry"], responses["sleep"], responses["support"]] or not responses["coping"]:
                    st.error("Please answer all questions to receive accurate recommendations.")
                else:
                    # Save responses to database if user is logged in
                    if "user" in st.session_state:
                        try:
                            # Ensure user exists in profiles first
                            ensure_profile_exists(st.session_state.user.id, st.session_state.user.email)
                            
                            # Convert responses to a format suitable for storage
                            response_data = {
                                'user_id': st.session_state.user.id,
                                'responses': responses,
                                'used_chat_history': include_chat_history
                            }
                            
                            # Store in questionnaire_responses table
                            supabase.table('questionnaire_responses').insert(response_data).execute()
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
        with st.spinner("Analyzing your responses..."):
            # Pass the chat history if requested
            chat_history = None
            if st.session_state.get("include_chat_history", False) and "messages" in st.session_state:
                chat_history = st.session_state.messages
                
            recommendations = generate_recommendations(st.session_state.responses, chat_history)
            
        # Display recommendations
        st.success("Based on your responses, here are some personalized recommendations:")
        st.markdown(recommendations)
        
        # Provide option to download recommendations
        csv_data = pd.DataFrame([
            {"Recommendation": recommendations}
        ])
        csv = csv_data.to_csv(index=False)
        st.download_button(
            label="Download Recommendations",
            data=csv,
            file_name="mental_health_recommendations.csv",
            mime="text/csv"
        )
        
        # Option to reset and take questionnaire again
        if st.button("Take Questionnaire Again", key="retake_questionnaire_button"):
            st.session_state.questionnaire_submitted = False
            st.rerun()
   
def generate_recommendations(responses, chat_history=None):
    """Generate personalized mental health recommendations with optional chat history"""
    try:
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
        
        system_prompt += """
        ## YOUR TASK
        Analyze these responses using clinical frameworks (like CBT principles, ACT, positive psychology) to provide personalized recommendations. Use a stepped-care approach where appropriate, focusing on self-help strategies while acknowledging when professional support may be beneficial.
        
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
def main():
    # Set page configuration
    st.set_page_config(
        page_title="Animoa | Mental Health Companion", 
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Restore Supabase session if tokens exist
    if "access_token" in st.session_state and "refresh_token" in st.session_state:
        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
    
    # Set default language if not set
    if "language" not in st.session_state:
        st.session_state.language = 'en'
    
    # Get translations for current language
    current_lang = st.session_state.language
    translations = TRANSLATIONS.get(current_lang, TRANSLATIONS['en'])
    
    # Check if user is logged in
    is_logged_in = auth_ui(supabase)
    
    if not is_logged_in:
        # Show info for non-logged in users
        st.stop()
    
    # If menu not in session state, default to Chat
    if "menu" not in st.session_state:
        st.session_state.menu = "Chat"
    
    # Create a simple navigation bar with buttons
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        st.write("# Animoa 🧠")
    
    with col2:
        if st.button(translations["chat"], key="nav_chat", use_container_width=True, 
                   type="primary" if st.session_state.menu == "Chat" else "secondary"):
            st.session_state.menu = "Chat"
            st.rerun()
    
    with col3:
        if st.button(translations["wellness"], key="nav_wellness", use_container_width=True,
                   type="primary" if st.session_state.menu == "Advisory" else "secondary"):
            st.session_state.menu = "Advisory"
            st.rerun()
    
    with col4:
        if st.button(translations["profile"], key="nav_profile", use_container_width=True,
                   type="primary" if st.session_state.menu == "Profile" else "secondary"):
            st.session_state.menu = "Profile"
            st.rerun()
    
    # Add the logout button to sidebar only
    with st.sidebar:
        st.write(f"Logged in as: {st.session_state.user.email}")
        if st.button(translations["logout"], key="sidebar_logout_button_main"):
            # Clear the session in Supabase
            try:
                supabase.auth.sign_out()
            except:
                pass
            # Clear session state
            for key in ['user', 'logged_in', 'messages', 'access_token', 'refresh_token', 'menu']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Display the selected page
    if st.session_state.menu == "Profile":
        profile_manager(supabase)
    elif st.session_state.menu == "Chat":
        chatbot = MentalHealthChatbot()
        chatbot.run()
    elif st.session_state.menu == "Advisory":
        mental_health_advisory()
       
if __name__ == "__main__":
    main()