
import streamlit as st
from groq import Groq
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load environment variables from .env 
load_dotenv()
# Initialize Supabase

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(supabase_url, supabase_key)

import streamlit as st

# Function to log in or sign up
def auth_ui(supabase):
    st.title("Welcome to Animoa🧠💬")

    option = st.radio("Select option:", ("Login", "Sign Up"))

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button(option):
        if option == "Sign Up":
            result = supabase.auth.sign_up({"email": email, "password": password})
            if result.error is not None:
                st.error(f"Signup failed: {result.error.message}")
            else:
                st.success("Signup successful! Please check your email to verify.")
        else:
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if result.error is not None:
                st.error(f"Login failed: {result.error.message}")
            else:
                st.success("Login successful!")
                st.session_state.user = result.session.user

    # Show user info if logged in
    if "user" in st.session_state:
        st.write("Logged in as:", st.session_state.user.email)
        return True
    else:
        return False


class MentalHealthChatbot:
    def __init__(self):
        # Initialize Groq client with environment variable
        self.client = Groq(api_key=st.secrets('GROQ_API_KEY'))
        
        # Initialize session state for chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def generate_response(self, user_input, conversation_history):
        """Generate response using Groq API with conversation context"""
        try:
            # Prepare messages with conversation history
            messages = [
                {
                    "role": "system", 
                    "content": """You are an empathetic mental health chatbot, designed to provide a safe, non-judgmental space for users to express their 
                    feelings and thoughts. Your primary role is to listen actively, reflect the user’s emotions, and gently encourage deeper self-exploration. 
                    Your responses should be calm, warm, and human-like, encouraging users to share more without pushing. Respond with kindness, understanding, 
                    and patience. Do not give unsolicited advice; instead, ask open-ended questions that help users explore their emotions and experiences.
                    
                    Focus on the following principles:
                    Empathy: Acknowledge the user’s emotions and experiences with compassion.
                    Non-Judgmental: Avoid any judgmental language and offer a safe space for the user.
                    Active Listening: Reflect the user’s words back to them and ask clarifying questions to show you are engaged.
                    Encouragement: Gently prompt the user to explore their feelings or thoughts deeper, without pressure.
                    Conciseness: Keep responses clear and concise. Avoid long or complex explanations. Your goal is to make the conversation feel natural and flowing."""
                }
            ]
            
            # Add previous conversation messages
            messages.extend(conversation_history)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})

            # Generate response using Groq
            chat_completion = self.client.chat.completions.create(
                model="qwen-2.5-32b",   #qwen-2.5-32b  #llama-3.3-70b-versatile  #deepseek-r1-distill-qwen-32b
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
        """Main Streamlit application"""
        # Page configuration
        st.set_page_config(
            page_title="Mental Health Companion", 
            page_icon="🧠",
            layout="wide"
        )

        # Title and introduction
        st.title("🌱 Mental Health Companion")
        st.write("A supportive AI assistant here to listen and help.")
        

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User input
        if prompt := st.chat_input("How are you feeling today?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
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

def main():
    is_logged_in = auth_ui(supabase)
    if not is_logged_in:
        st.stop()  # Stop the rest of the app until logged in
    chatbot = MentalHealthChatbot()
    chatbot.run()

if __name__ == "__main__":
    main()