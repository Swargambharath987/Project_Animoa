
import streamlit as st
from groq import Groq
import os

class MentalHealthChatbot:
    def __init__(self):
        # Initialize Groq client with environment variable
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
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
                    "content": """You are a supportive AI assistant trained to help with mental health concerns. Respond empathetically and concisely, offering practical advice"""
                }
            ]
            
            # Add previous conversation messages
            messages.extend(conversation_history)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})

            # Generate response using Groq
            chat_completion = self.client.chat.completions.create(
                model="qwen-2.5-32b",
                messages=messages,
                temperature=0.7,
                max_tokens=300
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
            page_icon="🧠"
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
    chatbot = MentalHealthChatbot()
    chatbot.run()

if __name__ == "__main__":
    main()