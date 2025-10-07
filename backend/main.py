from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Routers
from api.routes import routes_router
from api.history_routes import history_router

from api.chat_routes import voice_router
# from api.voice_routes import voice_router

# Exception handlers
from utils.exceptions import (
    app_exception_handler,
    http_exception_handler,
    generic_exception_handler,
    AppException,
)

load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Ecommerce Chatbot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

 # ✅ only once (clean)

app.include_router(routes_router, prefix="/api/chat", tags=["chat"])
app.include_router(voice_router, prefix="/api/voice", tags=["voice"])
# app.include_router(history_router, prefix="/api", tags=["history"])
app.include_router(history_router)


from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="responses"), name="static")

# Static files (for TTS responses etc.)
app.mount("/static", StaticFiles(directory="responses"), name="static")

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/")
def root():
    return {"message": "Ecommerce Chatbot API is running 🚀"}
#uvicorn main:app --reload --host 0.0.0.0 --port 8000