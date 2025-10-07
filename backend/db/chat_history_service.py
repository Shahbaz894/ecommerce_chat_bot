from datetime import datetime
from client import connect_to_database


class ChatHistoryService:
    def __init__(self):
        """Initialize connection to Astra DB and target collection."""
        db = connect_to_database()
        self.collection = db.get_collection("chat_history")

    def insert_message(self, session_id: str, role: str, text: str):
        """Insert a new chat message (user or bot)."""
        message = {
            "session_id": session_id,
            "role": role,
            "text": text,
            "timestamp": datetime.utcnow().isoformat(),
        }
        inserted = self.collection.insert_one(message)
        return str(inserted.inserted_id)

    def fetch_history(self, session_id: str):
        """Fetch all messages for a given session."""
        cursor = self.collection.find({"session_id": session_id})
        return list(cursor)
