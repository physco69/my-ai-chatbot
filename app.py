import requests
import streamlit as st

st.set_page_config(page_title="Advanced AI Assistant", page_icon="✦")
st.title("✦ Advanced AI Assistant")

API_URL = "https://huggingface.co"
HEADERS = {
    "Authorization": f"Bearer {st.secrets['HF_TOKEN']}",
    "Content-Type": "application/json",
}

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
        payload = {
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "messages": st.session_state.messages,
            "max_tokens": 500,
        }
        res = requests.post(
            API_URL, headers=HEADERS, json=payload, timeout=30
        )

        if res.status_code != 200:
          st.error(f"API Status {res.status_code}: {res.text}")
        else:
          data = res.json()
          reply = data["choices"]["message"]["content"]
          st.markdown(reply)
          st.session_state.messages.append(
              {"role": "assistant", "content": reply}
          )
      except Exception as e:
        st.error(f"Error details: {e}")

