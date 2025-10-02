from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from services.chatbot_services import ChatbotServices
from gtts import gTTS
import os, uuid, logging

logger = logging.getLogger(__name__)

chat_router = APIRouter()

OUTPUT_DIR = "responses"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    query: str
    session_id: str

@chat_router.post("/query")
async def chat_query(payload: ChatRequest):
    """
    Accepts a text query, gets raw chatbot response, 
    generates TTS, and returns both.
    """
    try:
        # Get chatbot response
        chatbot_service = ChatbotServices()
        response = chatbot_service.get_product_info(payload.query, payload.session_id)
        raw_text = response.get("answer") or str(response) or "No response from chatbot."
        logger.info(f"Chatbot response: {raw_text}")

        # Generate TTS audio if response exists
        tts_file_path = None
        if raw_text.strip():
            tts = gTTS(text=raw_text, lang="en")
            filename = f"speech_{uuid.uuid4().hex}.mp3"
            tts_file_path = os.path.join(OUTPUT_DIR, filename)
            tts.save(tts_file_path)
            logger.info(f"TTS saved: {tts_file_path}")

        return JSONResponse(
            content={
                "raw_text": raw_text,
                "audio_path": f"/static/{os.path.basename(tts_file_path)}" if tts_file_path else None
            }
        )

    except Exception as e:
        logger.exception("Error in chat_query")
        return JSONResponse(
            content={"error": "Failed to process query", "details": str(e)},
            status_code=500
        )
