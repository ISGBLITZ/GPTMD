import os
from dotenv import load_dotenv
import streamlit as st
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from datetime import datetime

# Load environment variables
load_dotenv()
endpoint = os.getenv("AZURE_FOUNDRY_PROJECT_ENDPOINT")
agent_id = os.getenv("AZURE_FOUNDRY_AGENT_ID")

# Initialize client
credential = DefaultAzureCredential()
client = AgentsClient(endpoint=endpoint, credential=credential)

# Streamlit setup
st.set_page_config(page_title="GPTMD", page_icon="🩺", layout="wide")
st.title("GPTMD - Your AI Health Assistant 🩺")

# --- CSS for bubbles, avatars, timestamps ---
st.markdown("""
<style>
.chat-container {
    display: flex;
    flex-direction: column;
}
.message-row {
    display: flex;
    align-items: flex-end;
    margin: 8px 0;
}
.user-row { justify-content: flex-end; }
.doctor-row { justify-content: flex-start; }
.avatar {
    font-size: 1.5em;
    margin: 0 8px;
}
.user-bubble {
    background-color: #DCF8C6;   /* WhatsApp green */
    color: #000000;              /* Black text */
    padding: 10px 15px;
    border-radius: 15px;
    max-width: 70%;
    word-wrap: break-word;
}
.doctor-bubble {
    background-color: #2F2F2F;   /* Dark gray */
    color: #FFFFFF;              /* White text */
    padding: 10px 15px;
    border-radius: 15px;
    max-width: 70%;
    word-wrap: break-word;
}
.timestamp {
    font-size: 0.75em;
    color: #AAAAAA;
    margin-top: 2px;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# Session state
if "thread_id" not in st.session_state:
    thread = client.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.messages = []
    # System prompt
    client.messages.create(
        thread_id=st.session_state.thread_id,
        role="assistant",
        content="""You are GPTMD, a friendly multilingual health information assistant.
Your purpose: Help users understand their symptoms, medications, and healthy habits clearly and safely.
Language behavior: Detect the user’s language automatically. Reply in the same language. Switch if requested.
Health rules: Provide general, educational information — not medical diagnoses or prescriptions. Encourage consulting professionals.
Style: Simple, clear sentences. Use bullet points or bold for emphasis. Concise and friendly."""
    )

# --- Chat history ---
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        timestamp = msg.get("time", "")
        if msg["role"] == "user":
            st.markdown(
                f'<div class="message-row user-row">'
                f'<div class="user-bubble">👤 {msg["content"]}'
                f'<div class="timestamp">{timestamp}</div></div>'
                f'</div>',
                unsafe_allow_html=True
            )
        elif msg["role"] == "assistant":
            st.markdown(
                f'<div class="message-row doctor-row">'
                f'<div class="doctor-bubble">🩺 {msg["content"]}'
                f'<div class="timestamp">{timestamp}</div></div>'
                f'</div>',
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

scroll_anchor = st.empty()

# --- Input at bottom ---
user_input = st.chat_input("Describe your symptoms...")

if user_input:
    now = datetime.now().strftime("%I:%M %p")
    # Append user message immediately so bubble shows right away
    st.session_state.messages.append({"role": "user", "content": user_input, "time": now})

    # Re-render chat history so user bubble appears instantly
    with chat_container:
        st.markdown(
            f'<div class="message-row user-row">'
            f'<div class="user-bubble">👤 {user_input}'
            f'<div class="timestamp">{now}</div></div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Send user message to backend
    client.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )

    # Placeholder for streaming reply
    with chat_container:
        placeholder = st.empty()
    partial_text = ""

    # Stream reply
    with st.spinner("Doctor is replying..."):
        with client.runs.stream(
            thread_id=st.session_state.thread_id,
            agent_id=agent_id
        ) as stream:
            for event_name, payload, _ in stream:
                if event_name == "thread.message.delta":
                    for item in payload.get("delta", {}).get("content", []):
                        if item.get("type") == "text":
                            text_value = item["text"]["value"]
                            partial_text += text_value
                            placeholder.markdown(
                                f'<div class="message-row doctor-row">'
                                f'<div class="doctor-bubble">🩺 {partial_text}</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                            scroll_anchor.markdown(" ")

                elif event_name == "thread.message.completed":
                    now = datetime.now().strftime("%I:%M %p")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": partial_text, "time": now}
                    )
                    # Replace placeholder with final bubble
                    placeholder.markdown(
                        f'<div class="message-row doctor-row">'
                        f'<div class="doctor-bubble">🩺 {partial_text}'
                        f'<div class="timestamp">{now}</div></div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    scroll_anchor.markdown(" ")
                    break

                elif event_name == "error":
                    st.error(f"⚠️ Error from agent: {payload}")
                    break
