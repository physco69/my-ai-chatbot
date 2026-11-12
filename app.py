import base64
import os
from groq import Groq
import streamlit as st

st.set_page_config(page_title="Sumedh's chatbot", page_icon="🌄")


# --- LOAD TIGER HILL SUNSET IMAGE SAFELY ---
def get_base64_bg(image_path):
  if os.path.exists(image_path):
    with open(image_path, "rb") as f:
      return base64.b64encode(f.read()).decode()
  return None


bg_base64 = get_base64_bg("tigerhill.jpg")
bg_layer = (
    f'url("data:image/jpeg;base64,{bg_base64}")'
    if bg_base64
    else "linear-gradient(180deg, #1E1B4B 0%, #7C2D12 55%, #090D16 100%)"
)

# --- FULL VISIBILITY SUNSET THEME & TRANSLUCENT GLASS BUBBLES ---
mobile_css = f"""
<style>
/* Pin the Tiger Hill sunset image so it stays visible even as new messages scroll */
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-image: linear-gradient(rgba(10, 8, 20, 0.18), rgba(10, 8, 20, 0.32)), {bg_layer};
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    z-index: 0;
    pointer-events: none;
}}

[data-testid="stAppViewContainer"] {{
    background: transparent !important;
}}

.block-container {{
    position: relative;
    z-index: 1;
}}

[data-testid="stHeader"] {{
    background: transparent !important;
}}

/* Red Clear Button with crisp white text */
[data-testid="stButton"] button {{
    background-color: rgba(220, 38, 38, 0.9) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: bold !important;
}}

/* Translucent frosted-glass bubbles so the sunset shines right through new messages */
[data-testid="stChatMessage"] {{
    background: rgba(15, 12, 28, 0.55) !important;
    border: 1px solid rgba(251, 146, 60, 0.5) !important;
    border-radius: 16px !important;
    padding: 12px 16px !important;
    backdrop-filter: blur(6px) !important;
    -webkit-backdrop-filter: blur(6px) !important;
}}
[data-testid="stChatMessage"] p, 
[data-testid="stChatMessage"] span, 
[data-testid="stChatMessage"] div {{
    color: #FFFFFF !important;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.85);
}}

/* See-through bottom input area so the sunset stays visible at the bottom too */
[data-testid="stBottom"], [data-testid="stBottom"] > div {{
    background: rgba(10, 8, 20, 0.35) !important;
    backdrop-filter: blur(6px) !important;
}}

h1 {{
    color: #FFFFFF !important;
    text-shadow: 0 2px 14px rgba(0, 0, 0, 0.95);
}}
</style>
"""
st.markdown(mobile_css, unsafe_allow_html=True)

# --- HEADER & CLEAR BUTTON ---
col1, col2 = st.columns([4, 1])
with col1:
  st.title("Sumedh's chatbot")
with col2:
  st.write("")
  if st.button("Clear", use_container_width=True):
    st.session_state.messages = [{
        "role": "system",
        "content": "You are a helpful, concise, and intelligent AI assistant.",
    }]
    st.rerun()

# --- GROQ AI CONNECTION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "system",
      "content": "You are a helpful, concise, and intelligent AI assistant.",
  }]

for msg in st.session_state.messages:
  if msg["role"] != "system":
    with st.chat_message(msg["role"]):
      st.markdown(msg["content"])

if prompt := st.chat_input("Ask anything..."):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    with st.spinner("Thinking..."):
      try:
        chat_completion = client.chat.completions.create(
            messages=st.session_state.messages,
            model="openai/gpt-oss-20b",
        )
        reply = chat_completion.choices.message.content
        st.markdown(reply)
        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )
      except Exception as e:
        st.error(f"Error details: {e}")

