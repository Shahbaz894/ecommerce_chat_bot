from fastapi import APIRouter, Query
from utils.exceptions import AppException
from services.chatbot_services import ChatbotServices


routes_router = APIRouter(tags=["Chatbot"])
chatbot_service = ChatbotServices()


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
