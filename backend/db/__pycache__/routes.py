from fastapi import APIRouter, Query
from utils.exceptions import AppException
from services.chatbot_services import ChatbotServices
from db.client import get_collection  # import from your db folder

routes_router = APIRouter(tags=["Chatbot"])
chatbot_service = ChatbotServices()

def get_history(session_id: str):
    collection = get_collection("chat_history")
    # Fetch messages for the session
    rows = collection.find({"session_id": session_id})
    return [{"sender": row["sender"], "text": row["message"]} for row in rows]

@routes_router.get("/history")
async def get_chat_history(session_id: str):
    try:
        return get_history(session_id)
    except Exception as e:
        return {"error": str(e), "status_code": 500}

@routes_router.get("/ask_product")
async def ask_product(
    query: str = Query(..., description="Customer product-related query"),
    session_id: str = Query("default", description="Unique session ID to maintain chat history")
):
    try:
        return chatbot_service.get_product_info(query, session_id=session_id)
    except AppException as e:
        return {"error": e.message, "status_code": e.status_code}
    except Exception as e:
        return {"error": str(e), "status_code": 500}
