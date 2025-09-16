from services.retreiver import RetrieverServices
from utils.logging import get_logger
from utils.exceptions import AppException

logger=get_logger(__name__)

class ChatbotServices:
    """
    Chatbot service that uses RetrieverServices to fetch
    product information and answer user queries.
    """

    def __init__(self):
        self.retriever=RetrieverServices()
        
    def get_product_info(self,query:str):
       """
        Generate chatbot response for a given customer query.
        
        Args:
            query (str): Customer's question about a product.

        Returns:
            dict: Contains query and chatbot's answer.
        """
       try:
            response = self.retriever.get_answer(query)
            logger.info(f"Generated response for query: {query}")
            
            response = self.retriever.get_answer(query)
            return {
                "query": query,
                "answer": response
            }
       except AppException as e:
            logger.error(f"AppException occurred: {e.message}")
            raise
       except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            raise AppException("Something went wrong while generating response", 500)