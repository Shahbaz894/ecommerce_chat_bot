# backend/services/chatbot_services.py

from services.retreiver import RetrieverServices
from utils.logging import get_logger
from utils.exceptions import AppException

logger = get_logger(__name__)

class ChatbotServices:
    """
    Chatbot service that integrates RetrieverServices for fetching
    product-related information and managing user sessions.
    """

    def __init__(self):
        # Initialize retriever with history support
        self.retriever = RetrieverServices()

    def get_product_info(self, query: str, session_id: str = "default") -> dict:
        """
        Generate chatbot response for a given customer query while
        maintaining session-based chat history.

        Args:
            query (str): Customer's product-related question.
            session_id (str): Unique ID to maintain chat history.

        Returns:
            dict: Contains query and chatbot's answer.
        """
        try:
            response = self.retriever.get_answer(query, session_id=session_id)
            logger.info(f"Generated response for query='{query}' in session='{session_id}'")

            return {
                "query": query,
                "answer": response,
                "session_id": session_id
            }
        except AppException as e:
            logger.error(f"AppException in ChatbotServices: {e.message}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            raise AppException("Something went wrong while generating response", 500)
