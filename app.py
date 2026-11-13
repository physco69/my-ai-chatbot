import base64
import io
import os
import urllib.parse
from duckduckgo_search import DDGS
from groq import Groq
from gtts import gTTS
from pypdf import PdfReader
import streamlit as st

st.set_page_config(
    page_title="Sumedh's AI Studio", page_icon="🌄", layout="centered"
)


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

mobile_css = f"""
<style>
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-image: linear-gradient(rgba(10, 8, 20, 0.16), rgba(10, 8, 20, 0.34)), {bg_layer};
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
    background: rgba(12, 10, 24, 0.90) !important;
    backdrop-filter: blur(14px) !important;
}}
[data-testid="stSidebar"] * {{
    color: #F8FAFC !important;
}}
[data-testid="stButton"] button {{
    background: rgba(251, 146, 60, 0.25) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(251, 146, 60, 0.6) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    backdrop-filter: blur(6px) !important;
}}
[data-testid="stChatMessage"] {{
    background: rgba(15, 12, 28, 0.56) !important;
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
    background: rgba(10, 8, 20, 0.42) !important;
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


def generate_ai_reply(
    prompt_text, history, persona_prompt, model_choice, use_web, attachment
):
  system_content = persona_prompt

  if use_web and attachment is None:
    try:
      with DDGS() as ddgs:
        results = list(ddgs.text(prompt_text, max_results=3))
      if results:
        web_context = "\n".join(
            [f"- {r['title']}: {r['body']}" for r in results]
        )
        system_content += (
            "\n\nUse these live web search results if helpful:\n"
            f" {web_context}"
        )
    except Exception:
      pass

  api_messages = [{"role": "system", "content": system_content}]
  for m in history[-10:-1]:
    api_messages.append({"role": m["role"], "content": m["content"]})

  active_model = model_choice

  if attachment is not None:
    file_type = attachment.type
    if "image" in file_type:
      img_b64 = base64.b64encode(attachment.getvalue()).decode("utf-8")
      api_messages.append({
          "role": "user",
          "content": [
              {"type": "text", "text": prompt_text},
              {
                  "type": "image_url",
                  "image_url": {"url": f"data:{file_type};base64,{img_b64}"},
              },
          ],
      })
      active_model = "meta-llama/llama-4-scout-17b-16e-instruct"
    elif "pdf" in file_type:
      reader = PdfReader(attachment)
      pdf_text = "\n".join(
          [page.extract_text() or "" for page in reader.pages]
      )[:12000]
      api_messages.append({
          "role": "user",
          "content": f"Document:\n{pdf_text}\n\nQuestion: {prompt_text}",
      })
    else:
      txt_content = attachment.getvalue().decode("utf-8")[:12000]
      api_messages.append({
          "role": "user",
          "content": f"File:\n{txt_content}\n\nQuestion: {prompt_text}",
      })
  else:
    api_messages.append({"role": "user", "content": prompt_text})

  completion = client.chat.completions.create(
      messages=api_messages, model=active_model, max_tokens=1024
  )
  return completion.choices.message.content


# --- SIDEBAR CONTROL CENTER ---
with st.sidebar:
  st.header("⚙️ Hi-Fi Control Center")
  selected_persona = st.selectbox("🎭 AI Personality", list(PERSONAS.keys()))
  selected_model = st.selectbox(
      "🧠 AI Brain Model",
      [
          "openai/gpt-oss-20b",
          "openai/gpt-oss-120b",
          "meta-llama/llama-4-scout-17b-16e-instruct",
      ],
  )
  st.divider()
  st.subheader("🚀 Superpowers")
  web_search_enabled = st.toggle("🌐 Live Web Search", value=True)
  voice_reply_enabled = st.toggle("🔊 AI Voice Reply (Speak)", value=False)
  st.divider()
  st.subheader("📎 Vision & PDF Reader")
  uploaded_file = st.file_uploader(
      "Upload photo or PDF", type=["png", "jpg", "jpeg", "pdf", "txt"]
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

# --- MAIN HEADER & QUICK ACTION CHIPS ---
st.title("Sumedh's chatbot")

if "messages" not in st.session_state:
  st.session_state.messages = []

quick_prompt = None
if len(st.session_state.messages) == 0:
  c1, c2, c3 = st.columns(3)
  with c1:
    if st.button("📰 Today's News", use_container_width=True):
      quick_prompt = "Give me the top 5 world and tech news headlines today."
  with c2:
    if st.button("🎨 Draw BMW M2", use_container_width=True):
      quick_prompt = (
          "/imagine futuristic blue BMW M2 drifting on a mountain road at"
          " sunset, 8k photorealistic"
      )
  with c3:
    if st.button("💡 Python Idea", use_container_width=True):
      quick_prompt = (
          "Give me 3 cool Python project ideas I can build this weekend."
      )

for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])
    if "image" in msg:
      st.image(msg["image"], use_container_width=True)
    if "audio" in msg:
      st.audio(msg["audio"], format="audio/mp3")

audio_value = st.audio_input("🎙️ Speak to Sumedh's AI")
text_prompt = st.chat_input(
    "Ask anything, search the web, or type /imagine <prompt>..."
)

final_prompt = quick_prompt

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

if final_prompt:
  st.session_state.messages.append({"role": "user", "content": final_prompt})
  with st.chat_message("user"):
    st.markdown(final_prompt)

  with st.chat_message("assistant"):
    if final_prompt.lower().startswith("/imagine"):
      img_prompt = final_prompt[8:].strip() or "sunset over Tiger Hill"
      with st.spinner("Generating AI artwork..."):
        encoded = urllib.parse.quote(img_prompt)
        img_url = f"https://pollinations.ai{encoded}?width=1024&height=768&nologo=true"
        reply_text = f"🎨 Generated image for: **{img_prompt}**"
        st.markdown(reply_text)
        st.image(img_url, use_container_width=True)
        st.session_state.messages.append(
            {"role": "assistant", "content": reply_text, "image": img_url}
        )
    else:
      with st.spinner("Thinking..."):
        try:
          reply = generate_ai_reply(
              final_prompt,
              st.session_state.messages,
              PERSONAS[selected_persona],
              selected_model,
              web_search_enabled,
              uploaded_file,
          )
          st.markdown(reply)
          msg_data = {"role": "assistant", "content": reply}

          if voice_reply_enabled:
            tts = gTTS(text=reply[:600], lang="en")
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_bytes = audio_fp.getvalue()
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            msg_data["audio"] = audio_bytes

          st.session_state.messages.append(msg_data)
        except Exception as e:
st.error(f"Error details: {e}")
