from ingestion.csv_loader import CSVLoader
from ingestion.api_loader import APILoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore

from config.setting import (
    CSV_FILE_PATH,
    API_URL,
    ASTRA_DB_API_ENDPOINT,
    ASTRA_DB_APPLICATION_TOKEN,
    ASTRA_DB_KEYSPACE,
    EMBEDDINGS_CONFIG,
    VECTORSTORE_CONFIG,
)

from utils.logging import get_logger
from utils.exceptions import AppException

# Initialize logger
logger = get_logger(__name__)


class DataIngestion:
    """
    DataIngestion pipeline responsible for:
    1. Loading product data from CSV and API sources.
    2. Initializing embeddings dynamically (HuggingFace or OpenAI).
    3. Initializing vector store dynamically (AstraDB).
    4. Adding all documents to the vector store.

    Returns:
        vstore: Configured vector store instance with ingested documents.
    """

    def __init__(self):
        """Initialize loaders for CSV and API sources."""
        self.csv_loader = CSVLoader(CSV_FILE_PATH)
        self.api_loader = APILoader(API_URL)

    def run(self):
        """
        Execute the ingestion pipeline:
        - Load documents from CSV and API.
        - Setup embeddings (HuggingFace/OpenAI).
        - Setup vector store (AstraDB).
        - Store all documents in vector store.

        Returns:
            vstore: Vector store populated with ingested documents.

        Raises:
            AppException: If any step in the ingestion pipeline fails.
        """
        try:
            logger.info("🚀 Starting data ingestion pipeline...")

            # 1. Load data
            logger.info("📥 Loading data from CSV and API...")
            csv_docs = self.csv_loader.load()
            api_docs = self.api_loader.load()
            all_docs = csv_docs + api_docs
            logger.info(f"✅ Loaded {len(all_docs)} documents (CSV + API)")

            # 2. Setup embeddings dynamically
            provider = EMBEDDINGS_CONFIG.get("provider", "huggingface")
            logger.info(f"🔍 Initializing embeddings provider: {provider}")

            if provider == "huggingface":
                embeddings = HuggingFaceEmbeddings(
                    model_name=EMBEDDINGS_CONFIG["model"]
                )
            elif provider == "openai":
                embeddings = OpenAIEmbeddings(
                    model=EMBEDDINGS_CONFIG["model"]
                )
            else:
                logger.error(f"❌ Unsupported embeddings provider: {provider}")
                raise AppException(f"Unsupported embeddings provider: {provider}")

            # 3. Setup vector store dynamically
            vstore_provider = VECTORSTORE_CONFIG.get("provider", "astradb")
            logger.info(f"🗄️ Initializing vector store provider: {vstore_provider}")

            if vstore_provider == "astradb":
                vstore = AstraDBVectorStore(
                    embedding=embeddings,
                    collection_name="chatbotecomm",
                    api_endpoint=ASTRA_DB_API_ENDPOINT,
                    token=ASTRA_DB_APPLICATION_TOKEN,
                    namespace=ASTRA_DB_KEYSPACE,
                )
            else:
                logger.error(f"❌ Unsupported vectorstore provider: {vstore_provider}")
                raise AppException(f"Unsupported vectorstore provider: {vstore_provider}")

            # 4. Add docs to vector store
            logger.info("📤 Adding documents to vector store...")
            vstore.add_documents(all_docs)

            logger.info(f"✅ {len(all_docs)} documents successfully added to {vstore_provider}")
            return vstore

        except Exception as e:
            logger.exception(f"❌ Error in DataIngestion pipeline: {e}")
            raise AppException(f"DataIngestion failed: {str(e)}")
