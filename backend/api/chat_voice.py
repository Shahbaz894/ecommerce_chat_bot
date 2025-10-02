import speech_recognition as sr
from services.chatbot_services import ChatbotServices
from gtts import gTTS
import os
import uuid
import logging

# =========================
# Setup Logging
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = "responses"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def voice_input() -> str:
    """Capture voice from microphone and convert to text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        logger.info("Listening... speak now!")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source, timeout=10, phrase_time_limit=30)

    try:
        text = r.recognize_google(audio)
        logger.info(f"Recognized voice input: {text}")
        return text
    except sr.UnknownValueError:
        logger.warning("Could not understand the audio")
        return None
    except sr.RequestError as e:
        logger.error(f"Google Speech Recognition service error: {e}")
        return None


def text_to_speech(text: str) -> str:
    """Convert text to speech, save as mp3, return file path."""
    try:
        clean_text = str(text)
        file_name = f"speech_{uuid.uuid4().hex}.mp3"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        tts = gTTS(text=clean_text, lang="en")
        tts.save(file_path)
        logger.info(f"TTS saved to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        return None


def llm_response(user_text: str, session_id: str = "default"):
    """
    Fetch raw chatbot response and generate TTS audio.
    Returns:
        response_text (str): raw text from chatbot
        audio_path (str): path to generated mp3
    """
    try:
        chatbot = ChatbotServices()
        response = chatbot.get_product_info(query=user_text, session_id=session_id)

        # Get raw text (assuming 'answer' key from ChatbotServices)
        raw_text = response.get("answer") if isinstance(response, dict) else str(response)
        logger.info(f"Chatbot raw response: {raw_text}")

        # Generate audio
        audio_path = text_to_speech(raw_text)
        logger.info(f"TTS generated: {audio_path}")

        return raw_text, audio_path

    except Exception as e:
        logger.exception("Error in llm_response")
        return f"Error: {e}", None
