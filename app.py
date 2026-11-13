import base64
import os
from groq import Groq
from pypdf import PdfReader
import streamlit as st

st.set_page_config(
    page_title="Sumedh's chatbot", page_icon="🌄", layout="centered"
)


# --- LOAD TIGER HILL SUNSET BACKGROUND ---
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

# --- FULL VISIBILITY SUNSET THEME & GLASS UI ---
mobile_css = f"""
<style>
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-image: linear-gradient(rgba(10, 8, 20, 0.18), rgba(10, 8, 20, 0.35)), {bg_layer};
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

[data-testid="stSidebar"] {{
    background: rgba(12, 10, 24, 0.88) !important;
    backdrop-filter: blur(12px) !important;
}}
[data-testid="stSidebar"] * {{
    color: #F8FAFC !important;
}}

[data-testid="stButton"] button {{
    background-color: rgba(220, 38, 38, 0.9) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: bold !important;
}}

[data-testid="stChatMessage"] {{
    background: rgba(15, 12, 28, 0.58) !important;
    border: 1px solid rgba(251, 146, 60, 0.5) !important;
    border-radius: 16px !important;
    padding: 12px 16px !important;
    backdrop-filter: blur(6px) !important;
    -webkit-backdrop-filter: blur(6px) !important;
}}
[data-testid="stChatMessage"] p, 
[data-testid="stChatMessage"] span, 
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] li {{
    color: #FFFFFF !important;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.85);
}}

[data-testid="stBottom"], [data-testid="stBottom"] > div {{
    background: rgba(10, 8, 20, 0.4) !important;
    backdrop-filter: blur(6px) !important;
}}

h1 {{
    color: #FFFFFF !important;
    text-shadow: 0 2px 14px rgba(0, 0, 0, 0.95);
}}
</style>
"""
st.markdown(mobile_css, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- AI PERSONALITIES ---
PERSONAS = {
    "🤖 Smart Assistant": (
        "You are Sumedh's intelligent, concise, and helpful AI assistant."
    ),
    "💻 Pro Coder": (
        "You are an expert software engineer. Write clean, well-explained code"
        " and debug issues step-by-step."
    ),
    "🎓 Study Tutor": (
        "You are a patient teacher. Explain complex topics simply using"
        " examples, bullet points, and analogies."
    ),
    "😂 Savage Roaster": (
        "You are a witty, sarcastic comedian. Answer the user's question"
        " accurately, but roast them playfully along the way."
    ),
}

# --- SIDEBAR CONTROL CENTER ---
with st.sidebar:
  st.header("⚙️ Control Center")

  selected_persona = st.selectbox("Choose AI Mode", list(PERSONAS.keys()))
  selected_model = st.selectbox(
      "AI Brain Speed/Power",
      [
          "openai/gpt-oss-20b",
          "openai/gpt-oss-120b",
          "meta-llama/llama-4-scout-17b-16e-instruct",
      ],
  )

  st.divider()
  st.subheader("📎 Attach Photo or PDF")
  uploaded_file = st.file_uploader(
      "Upload image or document", type=["png", "jpg", "jpeg", "pdf", "txt"]
  )

  st.divider()
  if st.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

  if "messages" in st.session_state and len(st.session_state.messages) > 0:
    chat_export = "\n\n".join(
        [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages]
    )
    st.download_button(
        label="💾 Download Chat (.txt)",
        data=chat_export,
        file_name="sumedh_ai_chat.txt",
        mime="text/plain",
        use_container_width=True,
    )

# --- MAIN HEADER ---
st.title("Sumedh's chatbot")

if "messages" not in st.session_state:
  st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])

# --- VOICE INPUT & TEXT INPUT ---
audio_value = st.audio_input("🎙️ Speak to Sumedh's AI (Optional)")
text_prompt = st.chat_input("Ask anything or describe your uploaded file...")

final_prompt = None

# Transcribe voice input using Groq Whisper if user recorded audio
if audio_value is not None:
  if (
      "last_audio" not in st.session_state
      or st.session_state.last_audio != audio_value.getvalue()
  ):
    st.session_state.last_audio = audio_value.getvalue()
    with st.spinner("Transcribing voice..."):
      try:
        transcription = client.audio.transcriptions.create(
            file=("voice.wav", audio_value.getvalue()),
            model="whisper-large-v3-turbo",
        )
        final_prompt = transcription.text
      except Exception as e:
        st.error(f"Voice Error: {e}")

if text_prompt:
  final_prompt = text_prompt

# --- PROCESS USER REQUEST ---
if final_prompt:
  st.session_state.messages.append({"role": "user", "content": final_prompt})
  with st.chat_message("user"):
    st.markdown(final_prompt)

  with st.chat_message("assistant"):
    with st.spinner("Thinking..."):
      try:
        api_messages = [
            {"role": "system", "content": PERSONAS[selected_persona]}
        ]

        # Add conversation memory (last 10 turns)
        for m in st.session_state.messages[-10:-1]:
          api_messages.append({"role": m["role"], "content": m["content"]})

        # Handle Image Vision or PDF Document Context if attached
        if uploaded_file is not None:
          file_type = uploaded_file.type

          if "image" in file_type:
            img_b64 = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
            api_messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": final_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{file_type};base64,{img_b64}"
                        },
                    },
                ],
            })
            active_model = "meta-llama/llama-4-scout-17b-16e-instruct"

          elif "pdf" in file_type:
            reader = PdfReader(uploaded_file)
            pdf_text = "\n".join(
                [page.extract_text() or "" for page in reader.pages]
            )[:12000]
            api_messages.append({
                "role": "user",
                "content": (
                    f"Document Content:\n{pdf_text}\n\nUser Question:"
                    f" {final_prompt}"
                ),
            })
            active_model = selected_model

          else:
            txt_content = uploaded_file.getvalue().decode("utf-8")[:12000]
            api_messages.append({
                "role": "user",
                "content": (
                    f"File Content:\n{txt_content}\n\nUser Question:"
                    f" {final_prompt}"
                ),
            })
            active_model = selected_model
        else:
          api_messages.append({"role": "user", "content": final_prompt})
          active_model = selected_model

        chat_completion = client.chat.completions.create(
            messages=api_messages, model=active_model, max_tokens=1024
        )
        reply = chat_completion.choices.message.content
        st.markdown(reply)
        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )

      except Exception as e:
        st.error(f"Error details: {e}")



