from fastapi import APIRouter, Query, HTTPException
from services.chatbot_services import ChatbotServices
from db.chat_history_service import ChatHistoryService
from utils.exceptions import AppException

routes_router = APIRouter(tags=["Chatbot"])
chatbot_service = ChatbotServices()
chat_history_service = ChatHistoryService()


@routes_router.get("/ask_product")
async def ask_product(
    query: str = Query(..., description="User’s product-related question"),
    session_id: str = Query("default", description="Unique session ID")
):
    """
    Handles user queries, stores both user and bot messages in Astra DB.
    """
    try:
        # ✅ Save user's query
        chat_history_service.insert_message(session_id, "user", query)

        # ✅ Get AI response
        response = chatbot_service.get_product_info(query, session_id=session_id)
        bot_reply = response.get("response") if isinstance(response, dict) else str(response)

        # ✅ Save bot response
        chat_history_service.insert_message(session_id, "bot", bot_reply)

        return {
            "session_id": session_id,
            "query": query,
            "response": bot_reply
        }

    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
