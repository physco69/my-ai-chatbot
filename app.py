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
    page_title="Sumedh's Gemini AI", page_icon="✨", layout="centered"
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
    else "radial-gradient(circle at top, #131629 0%, #090A0F 100%)"
)

# --- GOOGLE GEMINI INSPIRED UI + TIGER HILL SUNSET ---
gemini_css = f"""
<style>
/* Fixed Tiger Hill Sunset Backdrop */
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-image: linear-gradient(rgba(11, 13, 22, 0.22), rgba(11, 13, 22, 0.42)), {bg_layer};
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    z-index: 0;
    pointer-events: none;
}}

[data-testid="stAppViewContainer"] {{
    background: transparent !important;
    font-family: 'Google Sans', 'Segoe UI', Roboto, sans-serif;
}}

.block-container {{
    position: relative;
    z-index: 1;
    max-width: 780px;
}}

[data-testid="stHeader"] {{
    background: transparent !important;
}}

/* Gemini Dark Translucent Sidebar */
[data-testid="stSidebar"] {{
    background: rgba(16, 18, 28, 0.92) !important;
    backdrop-filter: blur(16px) !important;
    border-right: 1px solid rgba(138, 180, 248, 0.15);
}}
[data-testid="stSidebar"] * {{
    color: #E8EAED !important;
}}

/* Gemini Signature Blue-Purple-Pink Gradient Greeting */
.gemini-greeting {{
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #4285F4 0%, #9B72CB 50%, #D96570 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
    filter: drop-shadow(0 2px 10px rgba(0, 0, 0, 0.6));
}}
.gemini-sub {{
    font-size: 1.25rem;
    color: rgba(232, 234, 237, 0.92);
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.85);
    margin-bottom: 1.5rem;
}}

/* Gemini Suggestion Cards */
[data-testid="stButton"] button {{
    background: rgba(24, 27, 40, 0.65) !important;
    color: #E8EAED !important;
    border: 1px solid rgba(138, 180, 248, 0.35) !important;
    border-radius: 16px !important;
    padding: 12px 14px !important;
    font-weight: 500 !important;
    backdrop-filter: blur(8px) !important;
    transition: all 0.2s ease;
}}
[data-testid="stButton"] button:hover {{
    border-color: #8AB4F8 !important;
    background: rgba(36, 41, 60, 0.82) !important;
}}

/* Gemini Clean Frosted Chat Bubbles */
[data-testid="stChatMessage"] {{
    background: rgba(18, 20, 32, 0.62) !important;
    border: 1px solid rgba(138, 180, 248, 0.25) !important;
    border-radius: 20px !important;
    padding: 14px 18px !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
}}
[data-testid="stChatMessage"] p, 
[data-testid="stChatMessage"] span, 
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] li {{
    color: #F1F3F4 !important;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.85);
    line-height: 1.6;
}}

/* Pill-Shaped Bottom Bar */
[data-testid="stBottom"], [data-testid="stBottom"] > div {{
    background: rgba(11, 13, 22, 0.45) !important;
    backdrop-filter: blur(8px) !important;
}}
[data-testid="stChatInput"] textarea {{
    border-radius: 24px !important;
}}
</style>
"""
st.markdown(gemini_css, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- GEMINI GEMS (SPECIALIZED AI MODES) ---
GEMS = {
    "✨ Gemini General": (
        "You are Sumedh's helpful, structured, and intelligent AI assistant"
        " modeled after Google Gemini. Use clear headings, bullet points, and"
        " concise explanations."
    ),
    "💻 Coding Partner": (
        "You are a senior software engineer. Write clean, production-ready"
        " code with clear explanations and edge-case checks."
    ),
    "🎓 Learning Coach": (
        "You are a supportive tutor. Break complex concepts into simple"
        " step-by-step lessons with real-world analogies."
    ),
    "✍️ Writing Editor": (
        "You are a creative writer and editor. Help draft polished emails,"
        " essays, stories, and social media posts."
    ),
    "🧠 Deep Brainstormer": (
        "You are a strategic thinker. Generate innovative ideas, pros and"
        " cons, and actionable roadmaps."
    ),
}


def stream_gemini_response(
    prompt_text, history, gem_prompt, model_choice, use_web, attachment
):
  system_content = gem_prompt

  if use_web and attachment is None:
    try:
      with DDGS() as ddgs:
        results = list(ddgs.text(prompt_text, max_results=3))
      if results:
        web_context = "\n".join(
            [f"- {r['title']}: {r['body']}" for r in results]
        )
        system_content += (
            "\n\nUse these live web search results for up-to-date facts:\n"
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

  stream = client.chat.completions.create(
      messages=api_messages, model=active_model, max_tokens=1500, stream=True
  )
  for chunk in stream:
    delta = chunk.choices.delta.content
    if delta:
      yield delta


def run_chat_turn(
    prompt_text, gem_prompt, model_choice, use_web, use_voice, attachment
):
  st.session_state.messages.append({"role": "user", "content": prompt_text})
  with st.chat_message("user", avatar="👤"):
    st.markdown(prompt_text)

  with st.chat_message("assistant", avatar="✨"):
    if prompt_text.lower().startswith("/imagine"):
      img_prompt = prompt_text[8:].strip() or "sunset over Tiger Hill"
      with st.spinner("Creating image..."):
        encoded = urllib.parse.quote(img_prompt)
        img_url = f"https://pollinations.ai{encoded}?width=1024&height=768&nologo=true"
        reply_text = f"✨ Created image for: **{img_prompt}**"
        st.markdown(reply_text)
        st.image(img_url, use_container_width=True)
        st.session_state.messages.append(
            {"role": "assistant", "content": reply_text, "image": img_url}
        )
      return

    full_reply = st.write_stream(
        stream_gemini_response(
            prompt_text,
            st.session_state.messages,
            gem_prompt,
            model_choice,
            use_web,
            attachment,
        )
    )
    msg_data = {"role": "assistant", "content": full_reply}

    if use_voice and full_reply:
      tts = gTTS(text=full_reply[:600], lang="en")
      audio_fp = io.BytesIO()
      tts.write_to_fp(audio_fp)
      audio_bytes = audio_fp.getvalue()
      st.audio(audio_bytes, format="audio/mp3", autoplay=True)
      msg_data["audio"] = audio_bytes

    st.session_state.messages.append(msg_data)


# --- GEMINI SIDEBAR (GEMS & TOOLS) ---
with st.sidebar:
  st.markdown("### ✨ Sumedh's Gemini")
  if st.button("➕ New Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

  st.divider()
  selected_gem = st.selectbox("💎 Gems (AI Modes)", list(GEMS.keys()))
  selected_model = st.selectbox(
      "⚡ Model",
      [
          "openai/gpt-oss-20b",
          "openai/gpt-oss-120b",
          "meta-llama/llama-4-scout-17b-16e-instruct",
      ],
      format_func=lambda x: "Gemini Flash (Fast)"
      if "20b" in x
      else (
          "Gemini Pro (Deep)" if "120b" in x else "Gemini Vision (Multimodal)"
      ),
  )

  st.divider()
  web_search_enabled = st.toggle("🌐 Google/Web Grounding", value=True)
  voice_reply_enabled = st.toggle("🔊 Read Aloud (Voice)", value=False)

  st.divider()
  uploaded_file = st.file_uploader(
      "📎 Upload Image or PDF", type=["png", "jpg", "jpeg", "pdf", "txt"]
  )

  if "messages" in st.session_state and len(st.session_state.messages) > 0:
    st.divider()
    chat_export = "\n\n".join(
        [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages]
    )
    st.download_button(
        label="💾 Export Chat",
        data=chat_export,
        file_name="sumedh_gemini_chat.txt",
        mime="text/plain",
        use_container_width=True,
    )

if "messages" not in st.session_state:
  st.session_state.messages = []

# --- GEMINI HERO GREETING & SUGGESTION CARDS ---
quick_prompt = None
if len(st.session_state.messages) == 0:
  st.markdown(
      '<div class="gemini-greeting">Hello, Sumedh</div>', unsafe_allow_html=True
  )
st.markdown(
'How can I help you today?',
unsafe_allow_html=True,
)
c1, c2 = st.columns(2)
with c1:
if st.button("🌐 Latest tech & world news", use_container_width=True):
quick_prompt = (
"Summarize the top 5 technology and world news stories today."
)
if st.button("💻 Write a Python script", use_container_width=True):
quick_prompt = (
"Write a clean Python script to organize files in a folder by file"
" type."
)
with c2:
if st.button("🎨 Create BMW M2 art", use_container_width=True):
quick_prompt = (
"/imagine sleek blue BMW M2 parked at Tiger Hill viewpoint during"
" golden sunrise, photorealistic 8k"
)
if st.button("🧠 Explain quantum computing", use_container_width=True):
quick_prompt = (
"Explain quantum computing simply in 4 short bullet points."
)

Display existing messages with Gemini sparkle avatar

for msg in st.session_state.messages:
avatar_icon = "👤" if msg["role"] == "user" else "✨"
with st.chat_message(msg["role"], avatar=avatar_icon):
st.markdown(msg["content"])
if "image" in msg:
st.image(msg["image"], use_container_width=True)
if "audio" in msg:
st.audio(msg["audio"], format="audio/mp3")
audio_value = st.audio_input("🎙️ Voice prompt")
text_prompt = st.chat_input("Ask Sumedh's Gemini (or type /imagine )...")
final_prompt = quick_prompt
if audio_value is not None:
if (
"last_audio" not in st.session_state
or st.session_state.last_audio != audio_value.getvalue()
):
st.session_state.last_audio = audio_value.getvalue()
with st.spinner("Listening..."):
transcription = client.audio.transcriptions.create(
file=("voice.wav", audio_value.getvalue()),
model="whisper-large-v3-turbo",
)
final_prompt = transcription.text
if text_prompt:
final_prompt = text_prompt
if final_prompt:
run_chat_turn(
final_prompt,
GEMS[selected_gem],
selected_model,
web_search_enabled,
voice_reply_enabled,
uploaded_file,
)
