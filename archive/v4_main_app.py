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
        "language": "Language",
        
        # Mental Health Advisory translations
        "mental_health_advisory": "Mental Health Advisory",
        "answer_questions": "Answer a few questions to receive personalized mental health recommendations.",
        "submit_questionnaire": "Get Recommendations",
        "include_chat_history": "Include my chat history for more personalized recommendations",
        "retake_questionnaire": "Take Questionnaire Again",
        "download_recommendations": "Download Recommendations",
        "analyzing_responses": "Analyzing your responses...",
        "based_on_responses": "Based on your responses, here are some personalized recommendations:",
        "questionnaire_error": "Please answer all questions to receive accurate recommendations.",
        
        # Profile translations
        "profile_title": "Your Profile",
        "profile_subtitle": "This information helps us personalize your experience.",
        "personal_details": "Personal Details",
        "name": "Name",
        "age": "Age",
        "stress_level": "Current Stress Level",
        "mental_wellness_goals": "Mental Wellness Goals",
        "goals_placeholder": "What are you hoping to achieve with Animoa?",
        "interests": "Activities that bring you joy or peace",
        "interests_placeholder": "e.g., Reading, meditation, walking in nature...",
        "save_profile": "Save Profile",
        "profile_updated": "Profile updated successfully!"
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
        "language": "Idioma",
        
        # Mental Health Advisory translations
        "mental_health_advisory": "Asesoramiento de Salud Mental",
        "answer_questions": "Responda algunas preguntas para recibir recomendaciones personalizadas de salud mental.",
        "submit_questionnaire": "Obtener Recomendaciones",
        "include_chat_history": "Incluir mi historial de chat para recomendaciones más personalizadas",
        "retake_questionnaire": "Responder Cuestionario Nuevamente",
        "download_recommendations": "Descargar Recomendaciones",
        "analyzing_responses": "Analizando sus respuestas...",
        "based_on_responses": "Basado en sus respuestas, aquí hay algunas recomendaciones personalizadas:",
        "questionnaire_error": "Por favor responda todas las preguntas para recibir recomendaciones precisas.",
        
        # Profile translations
        "profile_title": "Tu Perfil",
        "profile_subtitle": "Esta información nos ayuda a personalizar tu experiencia.",
        "personal_details": "Datos Personales",
        "name": "Nombre",
        "age": "Edad",
        "stress_level": "Nivel de Estrés Actual",
        "mental_wellness_goals": "Objetivos de Bienestar Mental",
        "goals_placeholder": "¿Qué esperas lograr con Animoa?",
        "interests": "Actividades que te brindan alegría o paz",
        "interests_placeholder": "p.ej., Leer, meditación, caminar en la naturaleza...",
        "save_profile": "Guardar Perfil",
        "profile_updated": "¡Perfil actualizado con éxito!"
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
        "language": "语言",
        
        # Mental Health Advisory translations
        "mental_health_advisory": "心理健康咨询",
        "answer_questions": "回答几个问题，获取个性化的心理健康建议。",
        "submit_questionnaire": "获取建议",
        "include_chat_history": "包含我的聊天记录以获得更个性化的建议",
        "retake_questionnaire": "再次参与问卷",
        "download_recommendations": "下载建议",
        "analyzing_responses": "正在分析您的回答...",
        "based_on_responses": "根据您的回答，以下是一些个性化建议：",
        "questionnaire_error": "请回答所有问题以获得准确的建议。",
        
        # Profile translations
        "profile_title": "您的个人资料",
        "profile_subtitle": "这些信息有助于我们为您提供个性化体验。",
        "personal_details": "个人详情",
        "name": "姓名",
        "age": "年龄",
        "stress_level": "当前压力水平",
        "mental_wellness_goals": "心理健康目标",
        "goals_placeholder": "您希望通过Animoa实现什么？",
        "interests": "为您带来快乐或平静的活动",
        "interests_placeholder": "例如：阅读、冥想、在自然中散步...",
        "save_profile": "保存个人资料",
        "profile_updated": "个人资料更新成功！"
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
    
def mental_health_advisory():
    """Mental Health Advisory questionnaire and recommendations"""
    # Get current language and translations
    current_lang = st.session_state.language if "language" in st.session_state else 'en'
    translations = TRANSLATIONS.get(current_lang, TRANSLATIONS['en'])
    
    st.header(translations["mental_health_advisory"])
    st.write(translations["answer_questions"])
    
    if "questionnaire_submitted" not in st.session_state:
        st.session_state.questionnaire_submitted = False
    
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
        with st.spinner(translations["analyzing_responses"]):
            # Pass the chat history if requested
            chat_history = None
            if st.session_state.get("include_chat_history", False) and "messages" in st.session_state:
                chat_history = st.session_state.messages
                
            recommendations = generate_recommendations(st.session_state.responses, chat_history)
            
        # Display recommendations
        st.success(translations["based_on_responses"])
        st.markdown(recommendations)
        
        # Provide option to download recommendations
        csv_data = pd.DataFrame([
            {"Recommendation": recommendations}
        ])
        csv = csv_data.to_csv(index=False)
        st.download_button(
            label=translations["download_recommendations"],
            data=csv,
            file_name="mental_health_recommendations.csv",
            mime="text/csv"
        )
        
        # Option to reset and take questionnaire again
        if st.button(translations["retake_questionnaire"], key="retake_questionnaire_button"):
            st.session_state.questionnaire_submitted = False
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