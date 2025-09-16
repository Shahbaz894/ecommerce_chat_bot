from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from utils.exceptions import (
    app_exception_handler,
    http_exception_handler,
    generic_exception_handler,
    AppException,
)
from fastapi import HTTPException

# Initialize FastAPI app
app = FastAPI(title="Ecommerce Chatbot API")

# ✅ Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register API routes
app.include_router(router, prefix="/api")

# ✅ Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/")
def root():
    return {"message": "Ecommerce Chatbot API is running 🚀"}
