import streamlit as st
import requests

st.set_page_config(page_title="Ecommerce Chatbot", page_icon="🤖", layout="centered")

# Session ID (can be generated per user/session)
SESSION_ID = "test-session"

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

st.title("💬 Ecommerce Chatbot")

st.markdown("Ask product-related questions. The chat will appear below like a conversation.")

# Chat styles (left = bot, right = user)
chat_container_style = """
<style>
.chat-box {
    border: 1px solid #ccc;
    border-radius: 10px;
    padding: 15px;
    height: 450px;
    overflow-y: auto;
    background-color: #f9f9f9;
}
.user-msg {
    background-color: #007bff;
    color: white;
    padding: 10px;
    border-radius: 12px;
    margin: 5px 0;
    max-width: 70%;
    float: right;
    clear: both;
}
.bot-msg {
    background-color: #e0e0e0;
    color: black;
    padding: 10px;
    border-radius: 12px;
    margin: 5px 0;
    max-width: 70%;
    float: left;
    clear: both;
}
</style>
"""
st.markdown(chat_container_style, unsafe_allow_html=True)

# Input box
message = st.text_input("Type your message here:")

if st.button("Send") and message:
    try:
        # Call FastAPI backend
        url = f"http://127.0.0.1:8000/api/ask_product?query={message}&session_id={SESSION_ID}"
        response = requests.get(url)
        data = response.json()
        answer = data.get("answer", "No answer returned")

        # Save both user and bot messages
        st.session_state.history.append({"role": "user", "content": message})
        st.session_state.history.append({"role": "bot", "content": answer})

    except Exception as e:
        st.error(f"Error: {e}")

# Render chat history
chat_html = '<div class="chat-box">'
for chat in st.session_state.history:
    if chat["role"] == "user":
        chat_html += f'<div class="user-msg">{chat["content"]}</div>'
    else:
        chat_html += f'<div class="bot-msg">{chat["content"]}</div>'
chat_html += "</div>"

st.markdown(chat_html, unsafe_allow_html=True)

# Auto-scroll to bottom
st.markdown("""
<script>
const chatBox = window.parent.document.querySelector('.chat-box');
if(chatBox) { chatBox.scrollTop = chatBox.scrollHeight; }
</script>
""", unsafe_allow_html=True)
