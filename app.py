from groq import Groq
import streamlit as st

st.set_page_config(page_title="Sumedh's chatbot", page_icon="🏎️")

# --- REAL BMW M2 STATIC BACKGROUND IMAGE ---
BMW_IMAGE_URL = (
    "https://wikimedia.org"
)

static_bg_css = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: linear-gradient(rgba(8, 12, 22, 0.62), rgba(8, 12, 22, 0.72)), url("{BMW_IMAGE_URL}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: #F8FAFC;
}}

[data-testid="stHeader"] {{
    background: rgba(8, 12, 22, 0.5);
    backdrop-filter: blur(8px);
}}

[data-testid="stBottom"] {{
    background: rgba(8, 12, 22, 0.85);
    backdrop-filter: blur(12px);
}}

[data-testid="stChatMessage"] {{
    background: rgba(15, 23, 42, 0.78);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 16px;
    padding: 12px 16px;
    backdrop-filter: blur(8px);
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5);
}}

h1 {{
    color: #F8FAFC !important;
    text-shadow: 0 2px 12px rgba(0, 0, 0, 0.85);
}}
</style>
"""
st.markdown(static_bg_css, unsafe_allow_html=True)

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
        reply = chat_completion.choices[0].message.content
        st.markdown(reply)
        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )
      except Exception as e:
        st.error(f"Error details: {e}")
