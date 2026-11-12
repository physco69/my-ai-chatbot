from openai import OpenAI
import streamlit as st

st.set_page_config(page_title="Advanced AI Assistant", page_icon="✦")
st.title("✦ Advanced AI Assistant")

# Connects to Hugging Face's AI server safely from the backend
client = OpenAI(
    base_url="https://huggingface.co",
    api_key=st.secrets["HF_TOKEN"],
)

if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "system",
      "content": "You are a helpful, concise, and intelligent AI assistant.",
  }]

# Display chat history
for msg in st.session_state.messages:
  if msg["role"] != "system":
    with st.chat_message(msg["role"]):
      st.markdown(msg["content"])

# User input box at bottom
if prompt := st.chat_input("Ask anything..."):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    stream = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct",
        messages=st.session_state.messages,
        stream=True,
    )
    response = st.write_stream(stream)

  st.session_state.messages.append(
      {"role": "assistant", "content": response}
  )
