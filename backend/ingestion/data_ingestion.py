from ingestion.csv_loader import CSVLoader
from ingestion.api_loader import APILoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from astrapy import DataAPIClient  # ✅ NEW: For direct Astra DB access
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

logger = get_logger(__name__)


class DataIngestion:
    """
    DataIngestion pipeline:
    - Load data (CSV + API)
    - Create embeddings
    - Store in AstraDB vector store
    - Provide direct Astra DB access for chat history persistence
    """

    def __init__(self):
        self.csv_loader = CSVLoader(CSV_FILE_PATH)
        self.api_loader = APILoader(API_URL)

        # ✅ Initialize Astra DB connection for chat history
        try:
            self.client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
            self.db = self.client.get_database_by_api_endpoint(ASTRA_DB_API_ENDPOINT)
            logger.info("✅ Connected to Astra DB successfully for chat storage.")
        except Exception as e:
            logger.warning(f"⚠️ Astra DB chat connection failed: {e}")
            self.db = None

    def run(self):
        """
        Load data, create embeddings, and store in vector DB.
        """
        try:
            logger.info("🚀 Starting data ingestion pipeline...")

            # 1. Load product data
            logger.info("📥 Loading data from CSV and API...")
            csv_docs = self.csv_loader.load()
            api_docs = self.api_loader.load()
            all_docs = csv_docs + api_docs
            logger.info(f"✅ Loaded {len(all_docs)} documents (CSV + API)")

            # 2. Create embeddings
            provider = EMBEDDINGS_CONFIG.get("provider", "huggingface")
            logger.info(f"🔍 Initializing embeddings provider: {provider}")

            if provider == "huggingface":
                embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_CONFIG["model"])
            elif provider == "openai":
                embeddings = OpenAIEmbeddings(model=EMBEDDINGS_CONFIG["model"])
            else:
                raise AppException(f"Unsupported embeddings provider: {provider}")

            # 3. Create vector store
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
                raise AppException(f"Unsupported vectorstore provider: {vstore_provider}")

            # 4. Add documents
            logger.info("📤 Adding documents to vector store...")
            vstore.add_documents(all_docs)
            logger.info(f"✅ {len(all_docs)} documents successfully added to {vstore_provider}")

            return vstore

        except Exception as e:
            logger.exception(f"❌ Error in DataIngestion pipeline: {e}")
            raise AppException(f"DataIngestion failed: {str(e)}")

    def get_astra_db(self):
        """
        ✅ Direct Astra DB client for other services (chat history storage).
        Returns:
            Database object if connected, otherwise raises exception.
        """
        if not self.db:
            raise AppException("Astra DB connection not initialized.")
        return self.db
