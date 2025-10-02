import streamlit as st
import uuid
import requests
import os
import speech_recognition as sr

API_URL = "http://localhost:8000"

def main():
    st.title("🛍️ Multilingual AI Shopping Assistant 🤖")

    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())

    mode = st.radio("Choose input mode:", ["💬 Text", "🎤 Voice"])

    if mode == "💬 Text":
        query = st.text_input("Type your question here:")
        if st.button("Send Text Query") and query:
            process_query(query)

    elif mode == "🎤 Voice":
        if st.button("Start Voice Query"):
            with st.spinner("🎙️ Listening... please speak clearly."):
                query = capture_voice()
                if query:
                    st.success(f"You said: {query}")
                    process_query(query)
                else:
                    st.warning("⚠️ Could not recognize any speech. Try again.")

# -------------------------------
# Voice input function
# -------------------------------
def capture_voice() -> str:
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    try:
        with mic as source:
            st.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            st.info("Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=20)

        # Transcribe speech
        text = recognizer.recognize_google(audio)
        return text

    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        st.error(f"Google Speech Recognition API error: {e}")
        return None
    except Exception as e:
        st.error(f"Error capturing voice: {e}")
        return None

# -------------------------------
# Existing process_query function
# -------------------------------
def process_query(query: str):
    try:
        response = requests.post(
            f"{API_URL}/api/chat/query",
            json={"query": query, "session_id": st.session_state['session_id']},
        )

        if response.status_code != 200:
            st.error(f"❌ API Error: {response.text}")
            return

        result = response.json()
        raw_text = result.get("raw_text", "No response from chatbot.")
        audio_path = result.get("audio_path")

        st.subheader("Chatbot Response:")
        st.text_area(label="", value=raw_text, height=200)

        if audio_path:
            audio_response = requests.get(f"{API_URL}{audio_path}")
            if audio_response.status_code == 200:
                audio_bytes = audio_response.content
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    label="⬇️ Download Speech",
                    data=audio_bytes,
                    file_name=os.path.basename(audio_path),
                    mime="audio/mp3"
                )
            else:
                st.warning("⚠️ Could not fetch audio file.")

    except Exception as e:
        st.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
