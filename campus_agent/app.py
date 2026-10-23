"""
app.py - Final version for Lab 3

Complete Streamlit chat interface with ADK agent integration.
This file connects to the Campus Resource Assistant agent from Lab 2.

Author: Rebecca Russo
Course: CSC 2560 Introduction to AI Development
"""

import streamlit as st
import asyncio
import os

from streamlit.errors import StreamlitSecretNotFoundError

# ADK imports
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types

# Import our agent from Lab 2
from agent import root_agent, RESOURCE_FILE

# --- Environment and API Key Handling ---

# Handle API key for both local development and Streamlit Cloud deployment
if "GOOGLE_API_KEY" not in os.environ:
    # Try Streamlit secrets first (for deployment)
    try:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
    except (KeyError, AttributeError, FileNotFoundError, StreamlitSecretNotFoundError):
        # No secrets file (normal on a local machine): fall back to .env
        from dotenv import load_dotenv
        load_dotenv()

# Verify API key is available before proceeding
if "GOOGLE_API_KEY" not in os.environ or not os.environ["GOOGLE_API_KEY"]:
    st.error("""
    **API Key Not Found**
    For local development, create a `.env` file in the campus_agent folder with:
    ```
    GOOGLE_API_KEY=your-key-here
    ```
    For Streamlit Cloud, add the secret in your app's settings:
    - Key: `GOOGLE_API_KEY`
    - Value: your actual API key
    """)
    st.stop()

# --- Constants for ADK Session Management ---

APP_NAME = "campus_resource_app"
USER_ID = "student_user"

# --- Session and Runner Setup ---

def get_runner():
    """Create or retrieve the ADK runner from session state.
    The Runner orchestrates the agent execution loop:
    - Sends messages to the LLM
    - Handles tool calls
    - Returns responses
    
    We store it in session_state so it persists across Streamlit reruns.
    """
    if "runner" not in st.session_state:
        session_service = InMemorySessionService()
        artifact_service = InMemoryArtifactService()
        
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
            artifact_service=artifact_service
        )
        st.session_state.runner = runner
        st.session_state.session_service = session_service
    
    return st.session_state.runner


async def get_or_create_session():
    """Create a new ADK session or retrieve existing one.
    A Session represents one conversation thread. In a production app,
    each logged-in user would have their own session(s).
    
    We store the session_id so we can reuse the same session for
    the entire conversation.
    """
    session_service = st.session_state.session_service
    
    if "session_id" not in st.session_state:
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID
        )
        st.session_state.session_id = session.id
    
    return st.session_state.session_id


async def call_agent(prompt: str) -> str:
    """Send a message to the agent and get the response.
    This async function:
    1. Gets the runner and session
    2. Formats the message for Gemini
    3. Streams events from the agent
    4. Extracts the final response text
    
    Args:
        prompt: The user's question about campus resources
        
    Returns:
        The agent's response as a string
    """
    runner = get_runner()
    session_id = await get_or_create_session()
    
    # Create the message in ADK/Gemini format
    message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)]
    )
    
    # Run the agent and collect the response
    response_text = ""
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=message
    ):
        # Only process final responses (not streaming chunks or tool events)
        if event.is_final_response():
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
    
    # Graceful fallback if something goes wrong
    return response_text or "I couldn't process that request."

# --- Streamlit UI ---

st.set_page_config(
    page_title="Campus Resource Assistant",
    page_icon="🏛️",
    layout="centered"
)

st.title("🏛️ Campus Resource Assistant")

st.markdown("""
Ask me about campus resources like the library, tutoring center, 
advising office, or financial aid. I can help you find hours, 
locations, and contact information.
""")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome message on first load
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("""
        👋 Hello! I'm your Campus Resource Assistant.
        
        I can help you find information about campus resources like:
        - **Library** - hours, locations, services
        - **Learning Center (Tutoring)** - academic support
        - **Success Center** - advising and counseling
        - **Financial Aid and Billing** - aid, scholarships, billing
        - **Campus Bookstore**, **Campus Safety** and **Career Services**
        
        What would you like to know?
        """)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask about campus resources..."):
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response with loading indicator
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = asyncio.run(call_agent(prompt))
            st.markdown(response)
    
    # Store assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with information and controls
with st.sidebar:
    st.header("About")
    st.markdown(f"""
    This assistant helps you find information about campus resources.
    
    **Data source:** `{RESOURCE_FILE.name}`
    **Tip:** Try asking:
    - "Where is the library?"
    - "When is tutoring open?"
    - "What resources are available?"
    """)
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        # Also reset the ADK session for a true fresh start
        if "session_id" in st.session_state:
            del st.session_state.session_id
        st.rerun()
