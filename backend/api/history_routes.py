from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.chat_history_setup import insert_message, fetch_history  # use your working functions

history_router = APIRouter(prefix="/api/history", tags=["History"])


# 🧩 Chat message schema
class ChatMessage(BaseModel):
    id: str
    role: str
    text: str
    timestamp: str
    contentType: str | None = "text"
    imageUrl: str | None = None
    audioUrl: str | None = None


# ✅ GET - Fetch chat history
@history_router.get("/{session_id}")
async def get_chat_history(session_id: str):
    try:
        # Use your helper from chat_history_setup
        history_docs = fetch_history(session_id=session_id)

        # Convert docs into a clean list for frontend
        history = [
            {
                "id": doc.get("id"),
                "role": doc.get("role"),
                "text": doc.get("text"),
                "timestamp": doc.get("timestamp"),
                "contentType": doc.get("contentType", "text"),
                "imageUrl": doc.get("imageUrl"),
                "audioUrl": doc.get("audioUrl"),
            }
            for doc in history_docs
        ]

        return {"history": history}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {e}")


# ✅ POST - Save chat message
@history_router.post("/{session_id}")
async def save_chat_message(session_id: str, msg: ChatMessage):
    try:
        # Convert message to dict and pass to your insert_message helper
        message_data = {
            "session_id": session_id,
            "id": msg.id,
            "role": msg.role,
            "text": msg.text,
            "timestamp": msg.timestamp,
            "contentType": msg.contentType,
            "imageUrl": msg.imageUrl,
            "audioUrl": msg.audioUrl,
        }

        insert_message(message_data)
        return {"status": "success", "message": "Saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save message: {e}")
