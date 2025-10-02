# voice_router.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
import os
import tempfile
import base64
import logging
from typing import Optional
from contextlib import asynccontextmanager
from datetime import datetime
from dotenv import load_dotenv

# load .env (safely)
load_dotenv()

# OpenAI client
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# Chatbot service
try:
    from services.chatbot_services import ChatbotServices
except Exception as e:
    ChatbotServices = None
    logging.warning(f"Could not import ChatbotServices: {e}")

# Logging (no emojis to avoid Windows Unicode errors)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

voice_router = APIRouter()

# Constants
MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB
TTS_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
SUPPORTED_AUDIO_TYPES = {
    "audio/wav",
    "audio/mp3",
    "audio/m4a",
    "audio/webm",
    "audio/ogg",
    "audio/flac",
    "audio/aac",
}

# OpenAI client init
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = None
if OpenAI is not None and OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
else:
    logger.warning("OpenAI client not available or API key missing")


@asynccontextmanager
async def temporary_file(content: bytes, suffix: str = ".webm"):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        yield tmp_path
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")


def validate_audio_file_headers(content_type: Optional[str], audio_bytes: Optional[bytes] = None):
    if not content_type or content_type not in SUPPORTED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format. Supported: {', '.join(SUPPORTED_AUDIO_TYPES)}",
        )
    if audio_bytes and len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file too large. Max size: {MAX_AUDIO_SIZE / (1024*1024):.1f}MB",
        )


async def speech_to_text(audio_bytes: bytes) -> str:
    """Convert speech to text with Whisper"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized")

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    async with temporary_file(audio_bytes, ".webm") as tmp_path:
        def _transcribe(path: str):
            with open(path, "rb") as f:
                return client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="text",
                )

        transcript = await run_in_threadpool(_transcribe, tmp_path)
        if isinstance(transcript, str):
            return transcript.strip()
        return getattr(transcript, "text", str(transcript)).strip()


async def text_to_speech(text: str, voice: str = "alloy") -> bytes:
    """Convert text to speech (MP3)"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized")

    if voice not in TTS_VOICES:
        voice = "alloy"

    def _synthesize(speech_text: str) -> bytes:
        resp = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=speech_text[:4000],
            response_format="mp3",
        )
        if hasattr(resp, "content"):
            return resp.content
        if hasattr(resp, "read"):
            return resp.read()
        return bytes(resp)

    return await run_in_threadpool(_synthesize, text)


# STT endpoint
@voice_router.post("/stt")
async def stt_endpoint(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    validate_audio_file_headers(file.content_type, audio_bytes)
    text = await speech_to_text(audio_bytes)
    return {"text": text}


# TTS endpoint
@voice_router.post("/tts")
async def tts_endpoint(text: str = Query(...), voice: str = Query("alloy")):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    audio_bytes = await text_to_speech(text, voice)
    return {
        "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
        "format": "mp3",
        "voice_used": voice,
        "text_length": len(text),
    }


# Chat (alias: chat/query)
@voice_router.post("/chat")
@voice_router.post("/query")
async def voice_chat(
    file: UploadFile = File(...),
    session_id: str = Query("default"),
    voice: str = Query("alloy"),
):
    audio_bytes = await file.read()
    validate_audio_file_headers(file.content_type, audio_bytes)

    # 1) STT
    user_text = await speech_to_text(audio_bytes)
    logger.info(f"User query: {user_text}")

    # 2) Chatbot
    ai_text, products = "", []
    if ChatbotServices:
        chatbot_service = ChatbotServices()
        try:
            chatbot_response = await run_in_threadpool(
                chatbot_service.get_product_info, user_text, session_id
            )
            if isinstance(chatbot_response, dict):
                ai_text = chatbot_response.get("answer", "")
                products = chatbot_response.get("products", [])
            else:
                ai_text = str(chatbot_response)
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            ai_text = "Error: Chatbot unavailable."
    else:
        ai_text = "Chatbot service not available."

    # 3) TTS
    audio_base64, has_audio = "", False
    if client and ai_text:
        try:
            audio_bytes_out = await text_to_speech(ai_text, voice)
            audio_base64 = base64.b64encode(audio_bytes_out).decode("utf-8")
            has_audio = True
        except Exception as e:
            logger.error(f"TTS error: {e}")

    # 4) Return
    return {
        "user_query": user_text,
        "ai_response": ai_text,
        "audio_base64": audio_base64,
        "format": "mp3" if has_audio else None,
        "has_audio": has_audio,
        "voice_used": voice,
        "session_id": session_id,
        "products": products,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# Voices
@voice_router.get("/voices")
async def get_available_voices():
    return {"voices": TTS_VOICES, "default": "alloy"}


@voice_router.get("/health")
async def health():
    return {
        "service": "voice_integration",
        "status": "healthy",
        "openai_client": "initialized" if client else "not_initialized",
    }
