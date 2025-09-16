import pandas as pd
from langchain_core.documents import Document
from utils.logging import get_logger
from utils.exceptions import AppException

# Initialize logger
logger = get_logger(__name__)


class CSVLoader:
    """
    CSVLoader is responsible for loading product review data from a CSV file
    and converting it into LangChain `Document` objects for use in the
    vector store and retrieval pipeline.

    Attributes:
        file_path (str): Path to the CSV file.

    Methods:
        load() -> list[Document]:
            Reads the CSV file and transforms product reviews into a list of
            Document objects with metadata.
    """

    def __init__(self, file_path: str):
        """
        Initialize the CSVLoader with the provided file path.

        Args:
            file_path (str): Path to the CSV file containing product data.
        """
        self.file_path = file_path
        logger.info(f"CSVLoader initialized with file: {self.file_path}")

    def load(self) -> list[Document]:
        """
        Load product data from CSV and transform it into LangChain Documents.

        Returns:
            list[Document]: A list of Document objects containing product reviews.

        Raises:
            AppException: If the CSV file cannot be read or data is invalid.
        """
        try:
            logger.info(f"Loading data from CSV: {self.file_path}")
            data = pd.read_csv(self.file_path)

            # Validate required columns
            required_columns = {"product_title", "review", "rating"}
            if not required_columns.issubset(data.columns):
                missing = required_columns - set(data.columns)
                logger.error(f"CSV missing required columns: {missing}")
                raise AppException(f"CSV file missing required columns: {missing}")

            docs = []
            for _, row in data[["product_title", "review", "rating"]].iterrows():
                try:
                    metadata = {
                        "source": "csv",
                        "product_name": row["product_title"],
                        "rating": row["rating"]
                    }
                    doc = Document(page_content=row["review"], metadata=metadata)
                    docs.append(doc)
                except Exception as e:
                    logger.warning(f"Skipping row due to error: {e}")

            logger.info(f"Transformed {len(docs)} rows into Document objects")
            return docs

        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.file_path}")
            raise AppException(f"CSV file not found: {self.file_path}")

        except pd.errors.EmptyDataError:
            logger.error("CSV file is empty")
            raise AppException("CSV file is empty")

        except Exception as e:
            logger.exception(f"Unexpected error in CSVLoader: {e}")
            raise AppException(f"Unexpected error in CSVLoader: {str(e)}")
