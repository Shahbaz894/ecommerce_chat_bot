import requests
from langchain_core.documents import Document
from utils.logging import get_logger
from utils.exceptions import AppException

# Initialize logger for this module
logger = get_logger(__name__)


class APILoader:
    """
    APILoader is responsible for fetching product data from an external API
    and converting it into LangChain `Document` objects for use in the
    vector store and retrieval pipeline.

    Attributes:
        api_url (str): The URL of the external API endpoint.

    Methods:
        load() -> list[Document]:
            Fetches product data from the API and transforms it into a list of
            LangChain Document objects, each containing product details in
            page_content and metadata.
    """

    def __init__(self, api_url: str):
        """
        Initialize the APILoader with the provided API URL.

        Args:
            api_url (str): The URL to fetch product data from.
        """
        self.api_url = api_url
        logger.info(f"APILoader initialized with API URL: {self.api_url}")

    def load(self) -> list[Document]:
        """
        Fetch product data from the API and transform it into LangChain Documents.

        Returns:
            list[Document]: A list of Document objects containing product data.

        Raises:
            AppException: If the API request fails or response is invalid.
        """
        try:
            logger.info(f"Fetching data from API: {self.api_url}")
            res = requests.get(self.api_url, timeout=10)

            if res.status_code != 200:
                logger.error(f"API request failed with status code {res.status_code}")
                raise AppException(f"Failed to fetch data from API. Status code: {res.status_code}")

            data = res.json()
            logger.info(f"Successfully fetched {len(data)} products from API")

            docs = []
            for product in data:
                try:
                    # Prepare metadata
                    metadata = {
                        "source": "api",
                        "id": product["id"],
                        "title": product["title"],
                        "price": product["price"],
                        "category": product["category"],
                        "image": product["image"],
                        "rating": product["rating"]["rate"],
                        "rating_count": product["rating"]["count"]
                    }

                    # Prepare textual content for embedding
                    page_content = (
                        f"{product['title']}. "
                        f"Category: {product['category']}. "
                        f"Description: {product['description']}. "
                        f"Price: {product['price']}. "
                        f"Rating: {product['rating']['rate']} based on {product['rating']['count']} reviews."
                    )

                    docs.append(Document(page_content=page_content, metadata=metadata))
                except KeyError as e:
                    logger.warning(f"Skipping product due to missing key: {e}")

            logger.info(f"Transformed {len(docs)} products into Document objects")
            return docs

        except requests.RequestException as e:
            logger.error(f"RequestException while fetching data: {e}")
            raise AppException(f"API request failed: {str(e)}")

        except Exception as e:
            logger.exception(f"Unexpected error in APILoader: {e}")
            raise AppException(f"Unexpected error in APILoader: {str(e)}")
