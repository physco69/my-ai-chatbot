from groq import Groq
import streamlit as st

st.set_page_config(page_title="BMW M2 Turbo AI", page_icon="🏎️")

# --- ANIMATED RACING TRACK + BMW M2 GRAPHIC ---
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
        /* Glowing BMW M-color outer track curbs */
        linear-gradient(90deg, transparent 35%, rgba(239, 68, 68, 0.8) 35.3%, transparent 35.6%, transparent 64.4%, rgba(56, 189, 248, 0.8) 64.7%, transparent 65%),
        /* Horizontal speed lines rushing forward */
        repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.14) 0px, rgba(255, 255, 255, 0.14) 3px, transparent 3px, transparent 45px);
    background-size: 100% 90px, 100% 100%, 100% 90px;
    transform: perspective(320px) rotateX(68deg);
    transform-origin: top center;
    animation: raceForward 0.45s linear infinite;
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
    background: linear-gradient(90deg, #00A8E8, #1E3A8A, #EF4444);
    box-shadow: 0 0 25px 6px rgba(0, 168, 232, 0.5);
    pointer-events: none;
    z-index: 0;
}

@keyframes raceForward {
    0% { background-position: 0 0, 0 0, 0 0; }
    100% { background-position: 0 90px, 0 0, 0 90px; }
}

/* BMW M2 Floating Container on the Road */
.bmw-m2-container {
    position: fixed;
    bottom: 85px;
    left: 50%;
    transform: translateX(-50%);
    width: 240px;
    pointer-events: none;
    z-index: 0;
    animation: carDrift 2.8s ease-in-out infinite, engineVibe 0.12s linear infinite;
    filter: drop-shadow(0 15px 18px rgba(0, 0, 0, 0.9));
}

/* Subtle lane weaving + high-speed vibration */
@keyframes carDrift {
    0%, 100% { left: 48%; }
    50% { left: 52%; }
}
@keyframes engineVibe {
    0%, 100% { transform: translateX(-50%) translateY(0px); }
    50% { transform: translateX(-50%) translateY(-1.5px); }
}

/* Keep chat content floating cleanly above the car and track */
.block-container {
    position: relative;
    z-index: 1;
}

[data-testid="stHeader"] {
    background: rgba(5, 7, 14, 0.55);
    backdrop-filter: blur(8px);
}
[data-testid="stBottom"] {
    background: rgba(5, 7, 14, 0.85);
    backdrop-filter: blur(12px);
}

/* Frosted dark glass bubbles so text stays readable over the car */
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

<!-- CUSTOM BMW M2 REAR VIEW VECTOR GRAPHIC -->
<div class="bmw-m2-container">
<svg viewBox="0 0 300 140" xmlns="http://w3.org">
  <!-- Underglow -->
  <ellipse cx="150" cy="126" rx="125" ry="10" fill="rgba(0, 168, 232, 0.45)" />
  <!-- Wide Rear Tires -->
  <rect x="28" y="88" width="34" height="36" rx="6" fill="#090D16" />
  <rect x="238" y="88" width="34" height="36" rx="6" fill="#090D16" />
  <!-- Roof & Rear Windshield -->
  <path d="M 75 45 L 225 45 L 245 72 L 55 72 Z" fill="#1E293B" stroke="#38BDF8" stroke-width="1.5"/>
  <path d="M 82 49 L 218 49 L 233 69 L 67 69 Z" fill="#0B1120" />
  <!-- Carbon Fiber Lip Spoiler -->
  <path d="M 52 70 Q 150 64 248 70 L 244 74 Q 150 69 56 74 Z" fill="#020617" />
  <!-- Wide Muscular M2 Rear Body (Zandvoort Blue) -->
  <path d="M 45 72 L 255 72 L 270 95 L 265 115 L 35 115 L 30 95 Z" fill="#38BDF8" />
  <!-- M Performance Tri-Color Racing Stripes -->
  <polygon points="75,72 83,72 78,115 70,115" fill="#00A8E8" />
  <polygon points="83,72 91,72 86,115 78,115" fill="#1E3A8A" />
  <polygon points="91,72 99,72 94,115 86,115" fill="#EF4444" />
  <!-- BMW Roundel Badge -->
  <circle cx="150" cy="84" r="7" fill="#FFFFFF" stroke="#0F172A" stroke-width="1.5"/>
  <path d="M 150 77 A 7 7 0 0 1 157 84 L 150 84 Z" fill="#00A8E8" />
  <path d="M 150 91 A 7 7 0 0 1 143 84 L 150 84 Z" fill="#00A8E8" />
  <!-- M2 Badge -->
  <text x="218" y="85" fill="#0F172A" font-family="Arial, sans-serif" font-weight="bold" font-size="9">M2</text>
  <!-- Aggressive Glowing LED Taillights -->
  <path d="M 42 78 L 88 81 L 85 91 L 38 89 Z" fill="#EF4444" />
  <path d="M 44 82 L 84 84" stroke="#FCA5A5" stroke-width="2" />
  <path d="M 258 78 L 212 81 L 215 91 L 262 89 Z" fill="#EF4444" />
  <path d="M 256 82 L 216 84" stroke="#FCA5A5" stroke-width="2" />
  <!-- Rear Diffuser & Quad Exhaust Pipes -->
  <path d="M 60 103 L 240 103 L 235 118 L 65 118 Z" fill="#0F172A" />
  <circle cx="82" cy="112" r="5" fill="#94A3B8" stroke="#020617" stroke-width="1.5"/>
  <circle cx="96" cy="112" r="5" fill="#94A3B8" stroke="#020617" stroke-width="1.5"/>
  <circle cx="204" cy="112" r="5" fill="#94A3B8" stroke="#020617" stroke-width="1.5"/>
  <circle cx="218" cy="112" r="5" fill="#94A3B8" stroke="#020617" stroke-width="1.5"/>
  <!-- License Plate -->
  <rect x="122" y="92" width="56" height="12" rx="2" fill="#F8FAFC" />
  <text x="150" y="101" text-anchor="middle" fill="#0F172A" font-family="monospace" font-weight="bold" font-size="8">BMW M2</text>
</svg>
</div>
"""
st.markdown(racing_css, unsafe_allow_html=True)

# --- HEADER & CLEAR BUTTON ---
col1, col2 = st.columns([4, 1])
with col1:
  st.title("🏎️ BMW M2 AI Assistant")
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




