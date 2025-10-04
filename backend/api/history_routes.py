# history_routes.py
from fastapi import APIRouter, Query
from db.client import get_collection

history_router = APIRouter(tags=["History"])
def get_history(session_id: str):
    collection = get_collection("chat_history")
    # Fetch messages for the session
    rows = collection.find({"session_id": session_id})
    return [{"sender": row["sender"], "text": row["message"]} for row in rows]



@history_router.get("/history")
async def get_chat_history(session_id: str = Query(...)):
    collection = get_collection("chat_history")
    rows = collection.find({"session_id": session_id})
    return [{"sender": row["sender"], "text": row["message"]} for row in rows]
