# backend/utils/exceptions.py

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from utils.logging import get_logger

logger = get_logger(__name__)

# ---- Custom Exceptions ----
class AppException(Exception):
    """Base class for all custom exceptions."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class DataIngestionError(AppException):
    """Error raised during data ingestion."""


class VectorStoreError(AppException):
    """Error raised during vector store operations."""


# ---- Exception Handlers ----
async def app_exception_handler(request: Request, exc: AppException):
    """Handles custom AppException errors."""
    logger.error(f"[AppException] {exc.message} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handles standard FastAPI HTTP errors."""
    logger.warning(f"[HTTPException] {exc.detail} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handles all unexpected errors."""
    logger.exception(f"[Unexpected] {str(exc)} | Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"error": "Something went wrong, please try again later."}
    )



# 📌 Example usage inside your code:
    
# from utils.exceptions import DataIngestionError

# def load_csv(path):
#     try:
#         # your code here...
#         raise ValueError("File not found!")  # example error
#     except Exception as e:
#         raise DataIngestionError(f"CSV loading failed: {str(e)}", status_code=500)
