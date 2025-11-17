import streamlit as st
from groq import Groq
from supabase import create_client, Client
from dotenv import load_dotenv
import pandas as pd
import datetime
import os

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
    if "logged_in" in st.session_state and st.session_state.logged_in:
        # If already logged in, show user info in sidebar
        st.sidebar.success(f"Logged in as: {st.session_state.user.email}")
        if st.sidebar.button("Logout"):
            # Clear the session in Supabase first
            try:
                supabase.auth.sign_out()
            except:
                pass
            # Then clear session state
            for key in ['user', 'logged_in', 'messages', 'access_token', 'refresh_token']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()  # Use st.rerun() instead of experimental_rerun
        return True
    
    # If not logged in, show login/signup form
    st.title("Welcome to Animoa🧠💬")
    
    # Create columns for a cleaner layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🧠")
        
    with col2:
        st.markdown("### Your Mental Health Companion")
        st.write("Sign in to access personalized mental health support")
    
    # Authentication tabs
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:  # Login tab
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
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
                        st.success("Login successful!")
                        # Enable RLS for this user
                        supabase.auth.set_session(result.session.access_token, result.session.refresh_token)
                        st.rerun() # Use st.rerun() instead of experimental_rerun
                except Exception as e:
                    st.error(f"Authentication error: {str(e)}")
    
    with tab2:  # Sign Up tab
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Sign Up", use_container_width=True):
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
            existing_data = {'full_name': '', 'dob': None}
            
    except Exception as e:
        st.error(f"Error retrieving profile: {str(e)}")
        return
    
    # Profile form
    with st.form("profile_form"):
        full_name = st.text_input("Full Name", value=existing_data.get('full_name', ''))
        
        # Parse the date if it exists
        default_date = None
        if existing_data.get('dob'):
            try:
                if isinstance(existing_data['dob'], str):
                    default_date = datetime.datetime.strptime(existing_data['dob'], '%Y-%m-%d').date()
                else:
                    default_date = existing_data['dob']
            except:
                default_date = None
                
        dob = st.date_input("Date of Birth", value=default_date)
        
        submit_button = st.form_submit_button("Save Profile")
        
        if submit_button:
            try:
                supabase.table('profiles').update({
                    'full_name': full_name,
                    'dob': str(dob)
                }).eq('id', user_id).execute()
                st.success("Profile updated successfully!")
            except Exception as e:
                st.error(f"Error updating profile: {str(e)}")

class MentalHealthChatbot:
    def __init__(self):
        # Initialize Groq client with environment variable
        self.client = Groq(api_key=groq_api_key)
        
        # Initialize session state for chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        # Load previous chat history from database if user is logged in
        if "user" in st.session_state:
            self.load_chat_history()
    
    def load_chat_history(self):
        """Load chat history from Supabase"""
        if len(st.session_state.messages) == 0:  # Only load if no messages in current session
            try:
                response = supabase.table('chat_history').select('*').eq('user_id', st.session_state.user.id).order('timestamp', desc=False).execute()
                
                if response and response.data:
                    for msg in response.data:
                        if msg['sender'] == 'user':
                            st.session_state.messages.append({"role": "user", "content": msg['message']})
                        else:
                            st.session_state.messages.append({"role": "assistant", "content": msg['message']})
            except Exception as e:
                st.warning(f"Could not load chat history: {str(e)}")
    
    def save_message(self, role, content):
        """Save a message to the database"""
        if "user" in st.session_state:
            try:
                # Ensure user exists in profiles first
                ensure_profile_exists(st.session_state.user.id, st.session_state.user.email)
                
                # Then save message
                supabase.table('chat_history').insert({
                    'user_id': st.session_state.user.id,
                    'message': content,
                    'sender': 'user' if role == 'user' else 'bot'
                }).execute()
            except Exception as e:
                st.warning(f"Could not save message to database: {str(e)}")
    
    def generate_response(self, user_input, conversation_history):
        """Generate response using Groq API with conversation context"""
        try:
            # Prepare messages with conversation history
            messages = [
                {
                    "role": "system", 
                    "content": """You are an empathetic mental health chatbot, designed to provide a safe, non-judgmental space for users to express their 
                    feelings and thoughts. Your primary role is to listen actively, reflect the user's emotions, and gently encourage deeper self-exploration. 
                    Your responses should be calm, warm, and human-like, encouraging users to share more without pushing. Respond with kindness, understanding, 
                    and patience. Do not give unsolicited advice; instead, ask open-ended questions that help users explore their emotions and experiences.
                    
                    Focus on the following principles:
                    Empathy: Acknowledge the user's emotions and experiences with compassion.
                    Non-Judgmental: Avoid any judgmental language and offer a safe space for the user.
                    Active Listening: Reflect the user's words back to them and ask clarifying questions to show you are engaged.
                    Encouragement: Gently prompt the user to explore their feelings or thoughts deeper, without pressure.
                    Conciseness: Keep responses clear and concise. Avoid long or complex explanations. Your goal is to make the conversation feel natural and flowing."""
                }
            ]
            
            # Add previous conversation messages
            messages.extend(conversation_history)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Generate response using Groq - using llama-3.1 model instead of qwen
            chat_completion = self.client.chat.completions.create(
                model="llama3-70b-8192",  # Using llama3 model instead of qwen
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
        st.header("Chat with Animoa")
        st.write("Share your thoughts, feelings, or concerns, and I'll listen.")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # User input
        if prompt := st.chat_input("How are you feeling today?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            self.save_message("user", prompt)
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Prepare conversation history
            conversation_history = self.prepare_conversation_history()
            
            # Generate and display bot response
            with st.chat_message("assistant"):
                with st.spinner("Listening carefully..."):
                    response = self.generate_response(prompt, conversation_history)
                    st.markdown(response)
            
            # Add bot response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            self.save_message("assistant", response)

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
                                'responses': responses
                            }
                            
                            # Store in questionnaire_responses table
                            supabase.table('questionnaire_responses').insert(response_data).execute()
                            st.session_state.questionnaire_submitted = True
                            st.session_state.responses = responses
                            st.rerun()
                        except Exception as e:
                            st.warning(f"Could not save responses: {str(e)}")
                            
                    # If not logged in or error saving, still show recommendations
                    st.session_state.questionnaire_submitted = True
                    st.session_state.responses = responses
                    st.rerun()
    
    # Show recommendations if questionnaire is submitted
    if st.session_state.questionnaire_submitted:
        # Generate personalized advice based on responses
        with st.spinner("Analyzing your responses..."):
            recommendations = generate_recommendations(st.session_state.responses)
            
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
        if st.button("Take Questionnaire Again"):
            st.session_state.questionnaire_submitted = False
            st.rerun()

def generate_recommendations(responses):
    """Generate personalized mental health recommendations based on questionnaire responses"""
    try:
        # Create a prompt for the LLM based on responses
        system_prompt = f"""You are a mental health advisory AI trained to provide evidence-based recommendations.
        A user has completed a mental health questionnaire with the following responses:
        
        - Feeling down or depressed: {responses['mood']}
        - Little interest or pleasure: {responses['interest']}
        - Feeling anxious: {responses['anxiety']}
        - Uncontrollable worry: {responses['worry']}
        - Sleep quality: {responses['sleep']}
        - Social support: {responses['support']}
        - Current coping strategies: {responses['coping']}
        
        Based on these responses, provide personalized, evidence-based recommendations for improving mental wellbeing.
        Focus on actionable suggestions in these areas:
        1. Daily practices for mental wellness
        2. Specific techniques to address their reported challenges
        3. Resources they might find helpful
        
        Format your response using markdown with clear headings and bullet points.
        Keep your response compassionate, encouraging, and concise.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Please provide my personalized mental health recommendations."}
        ]
        
        # Generate response using Groq
        client = Groq(api_key=groq_api_key)
        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # Using llama3 model instead of qwen
            messages=messages,
            temperature=0.7
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        return f"""
        # Mental Health Recommendations
        
        We apologize, but we encountered an issue generating your personalized recommendations. Here are some general evidence-based mental health practices:
        
        ## Daily Practices
        * Practice mindfulness meditation for 5-10 minutes daily
        * Engage in physical activity for at least 30 minutes
        * Maintain a consistent sleep schedule
        
        ## Resources
        * If you're experiencing persistent mental health challenges, consider reaching out to a professional therapist or counselor
        * Crisis Text Line: Text HOME to 741741
        * National Suicide Prevention Lifeline: 988 or 1-800-273-8255
        
        Error details: {str(e)}
        """

def main():
    # Set page configuration - this must be the first Streamlit command
    st.set_page_config(
        page_title="Mental Health Companion", 
        page_icon="🧠",
        layout="wide"
    )
    
    # Restore Supabase session if tokens exist in session state
    if "access_token" in st.session_state and "refresh_token" in st.session_state:
        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
    
    # Check if user is logged in
    is_logged_in = auth_ui(supabase)
    
    if not is_logged_in:
        # Show some information about the app for non-logged in users
        st.markdown("""
        ## About Animoa - Your Mental Health Companion
        
        Animoa is an AI-powered mental health companion designed to support your emotional wellbeing through:
        
        - **Supportive Conversations**: Chat with our empathetic AI that listens and responds with compassion
        - **Personalized Recommendations**: Receive evidence-based mental health suggestions tailored to your needs
        - **Private & Secure**: Your conversations and data are kept private and secure
        
        Sign up or log in above to get started on your mental health journey.
        """)
        st.stop()  # Stop the rest of the app until logged in
    
    # Create sidebar menu
    menu = st.sidebar.radio(
        "Navigation",
        ["Profile", "Chat", "Mental Health Advisory"]
    )
    
    # Display the selected page
    if menu == "Profile":
        profile_manager(supabase)
    elif menu == "Chat":
        chatbot = MentalHealthChatbot()
        chatbot.run()
    elif menu == "Mental Health Advisory":
        mental_health_advisory()

if __name__ == "__main__":
    main()