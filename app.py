from groq import Groq
import streamlit as st

st.set_page_config(page_title="Advanced AI Assistant", page_icon="🏎️")

# --- ANIMATED MOVING RACING TRACK BACKGROUND ---
racing_css = """
<style>
/* Deep night sky base */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #05070E 0%, #0D1326 48%, #070A12 100%);
    color: #F8FAFC;
    overflow: hidden;
}

/* 3D Perspective Moving Racing Highway */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 45%;
    left: -50%;
    width: 200%;
    height: 100%;
    background-image: 
        /* Center dashed racing lane divider */
        linear-gradient(90deg, transparent 49.4%, rgba(250, 204, 21, 0.85) 49.6%, rgba(250, 204, 21, 0.85) 50.4%, transparent 50.6%),
        /* Glowing red & cyan outer track curbs */
        linear-gradient(90deg, transparent 35%, rgba(239, 68, 68, 0.7) 35.3%, transparent 35.6%, transparent 64.4%, rgba(56, 189, 248, 0.7) 64.7%, transparent 65%),
        /* Horizontal speed lines rushing forward */
        repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.14) 0px, rgba(255, 255, 255, 0.14) 3px, transparent 3px, transparent 45px);
    background-size: 100% 90px, 100% 100%, 100% 90px;
    transform: perspective(320px) rotateX(68deg);
    transform-origin: top center;
    animation: raceForward 0.55s linear infinite;
    pointer-events: none;
    z-index: 0;
}

/* Horizon neon glow */
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    top: 43%;
    left: 0;
    width: 100%;
    height: 6px;
    background: linear-gradient(90deg, #EF4444, #FACC15, #38BDF8);
    box-shadow: 0 0 25px 6px rgba(56, 189, 248, 0.45);
    pointer-events: none;
    z-index: 0;
}

@keyframes raceForward {
    0% { background-position: 0 0, 0 0, 0 0; }
    100% { background-position: 0 90px, 0 0, 0 90px; }
}

/* Keep chat content floating cleanly above the moving track */
.block-container {
    position: relative;
    z-index: 1;
}

/* Transparent top header & bottom bar */
[data-testid="stHeader"] {
    background: rgba(5, 7, 14, 0.55);
    backdrop-filter: blur(8px);
}
[data-testid="stBottom"] {
    background: rgba(5, 7, 14, 0.85);
    backdrop-filter: blur(12px);
}

/* Frosted dark glass bubbles so text stays readable over the moving road */
[data-testid="stChatMessage"] {
    background: rgba(15, 23, 42, 0.82);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 16px;
    padding: 12px 16px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.55);
}

h1 {
    color: #38BDF8 !important;
    text-shadow: 0 0 18px rgba(56, 189, 248, 0.5);
}
</style>
"""
st.markdown(racing_css, unsafe_allow_html=True)

# --- HEADER & CLEAR BUTTON ---
col1, col2 = st.columns([4, 1])
with col1:
  st.title("🏎️ Turbo AI Assistant")
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


