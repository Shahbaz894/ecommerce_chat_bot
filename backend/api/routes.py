# backend/api/routes.py

from fastapi import APIRouter, Query

from utils.exceptions import AppException
from services.chatbot_services import ChatbotServices

# Create router
router = APIRouter(prefix="/api", tags=["Chatbot"])

# Instantiate chatbot service
chatbot_service = ChatbotServices()

@router.get("/ask_product")
async def ask_product(query: str = Query(..., description="Customer product-related query")):
    """
    API endpoint to ask EcommerceBot a product-related question.
    
    Args:
        query (str): Customer's question about a product.

    Returns:
        dict: Answer from chatbot with context.
    """
    try:
        return chatbot_service.get_product_info(query)
    except AppException as e:
        return {"error": e.message, "status_code": e.status_code}
    except Exception as e:
        return {"error": str(e), "status_code": 500}
