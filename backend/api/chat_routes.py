from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from services.chatbot_services import ChatbotServices
import speech_recognition as sr
from gtts import gTTS
import uuid, os, logging
from pydub import AudioSegment

logger = logging.getLogger(__name__)
voice_router = APIRouter()

OUTPUT_DIR = "responses"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@voice_router.post("/chat")
async def voice_chat(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    try:
        # Save uploaded file
        temp_input = f"temp_{uuid.uuid4().hex}.webm"
        with open(temp_input, "wb") as f:
            f.write(await file.read())

        # Convert to WAV using pydub
        temp_wav = f"temp_{uuid.uuid4().hex}.wav"
        audio = AudioSegment.from_file(temp_input, format="webm")
        audio.export(temp_wav, format="wav")
        os.remove(temp_input)

        # Speech Recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        os.remove(temp_wav)

        logger.info(f"Transcribed: {text}")

        # Get chatbot response
        response = ChatbotServices().get_product_info(text, session_id)
        raw_text = response.get("answer", "No response")

        # Generate TTS
        tts_filename = f"speech_{uuid.uuid4().hex}.mp3"
        tts_path = os.path.join(OUTPUT_DIR, tts_filename)
        gTTS(raw_text).save(tts_path)

        return JSONResponse({
            "user_query": text,
            "ai_response": raw_text,
            "audio_path": f"/static/{tts_filename}"
        })

    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
