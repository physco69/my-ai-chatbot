import base64, os
from groq import Groq
import streamlit as st

st.set_page_config(page_title="Sumedh's Gemini", page_icon="✨")

# --- TIGER HILL SUNSET + GEMINI LOOK ---
bg = (
    base64.b64encode(open("tigerhill.jpg", "rb").read()).decode()
    if os.path.exists("tigerhill.jpg")
    else ""
)
img_css = (
    f'url("data:image/jpeg;base64,{bg}")'
    if bg
    else "linear-gradient(180deg,#131629,#090A0F)"
)
st.markdown(
    f"""<style>
[data-testid="stAppViewContainer"]::before {{content:"";position:fixed;inset:0;background:linear-gradient(rgba(10,12,20,.25),rgba(10,12,20,.45)),{img_css} center/cover no-repeat;z-index:0;}}
[data-testid="stAppViewContainer"],[data-testid="stHeader"] {{background:transparent!important;}}
.block-container {{position:relative;z-index:1;}}
[data-testid="stChatMessage"] {{background:rgba(18,20,32,.65)!important;border:1px solid rgba(138,180,248,.3)!important;border-radius:18px!important;backdrop-filter:blur(6px);}}
[data-testid="stChatMessage"] * {{color:#FFF!important;}}
[data-testid="stBottom"],[data-testid="stBottom"]>div {{background:rgba(10,12,20,.45)!important;}}
.hi {{font-size:2.3rem;font-weight:700;background:linear-gradient(90deg,#4285F4,#9B72CB,#D96570);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
</style>""",
    unsafe_allow_html=True,
)

# --- GEMINI GEMS & SIDEBAR ---
GEMS = {
    "✨ Gemini": "You are Sumedh's helpful, structured AI like Google Gemini.",
    "💻 Coder": "You are an expert coder. Give clean code and short steps.",
    "🎓 Tutor": "Explain simply with bullet points and examples.",
}
gem = st.sidebar.selectbox("💎 Gem Mode", list(GEMS.keys()))
if st.sidebar.button("➕ New Chat", use_container_width=True):
  st.session_state.messages = []
  st.rerun()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "messages" not in st.session_state:
  st.session_state.messages = []

if not st.session_state.messages:
  st.markdown('<div class="hi">Hello, Sumedh</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
  with st.chat_message(
      m["role"], avatar="👤" if m["role"] == "user" else "✨"
  ):
    st.markdown(m["content"])

# --- VOICE + TEXT INPUT ---
voice = st.audio_input("🎙️ Voice")
prompt = st.chat_input("Ask Sumedh's Gemini...")
if voice and st.session_state.get("last_v") != voice.getvalue():
  st.session_state.last_v = voice.getvalue()
  prompt = client.audio.transcriptions.create(
      file=("v.wav", voice.getvalue()), model="whisper-large-v3-turbo"
  ).text

# --- LIVE WORD-BY-WORD STREAMING REPLY ---
if prompt:
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user", avatar="👤"):
    st.markdown(prompt)
  with st.chat_message("assistant", avatar="✨"):
    msgs = [{"role": "system", "content": GEMS[gem]}] + st.session_state.messages[
        -8:
    ]
    stream = client.chat.completions.create(
        model="openai/gpt-oss-20b", messages=msgs, stream=True
    )
    reply = st.write_stream(
        c.choices[0].delta.content for c in stream if c.choices[0].delta.content
    )
    st.session_state.messages.append({"role": "assistant", "content": reply})
