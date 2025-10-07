from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from db.client import get_collection

class AstraChatMessageHistory(BaseChatMessageHistory):
    """Chat history persisted in Astra DB (Mongo API)."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.collection = get_collection("chat_history")

    @property
    def messages(self):
        rows = self.collection.find({"session_id": self.session_id}).sort("timestamp", 1)
        return [
            HumanMessage(content=r["message"]) if r["sender"] == "user" else AIMessage(content=r["message"])
            for r in rows
        ]

    def add_message(self, message):
        role = "user" if isinstance(message, HumanMessage) else "assistant"
        self.collection.insert_one({
            "session_id": self.session_id,
            "sender": role,
            "message": message.content,
            "timestamp": message.additional_kwargs.get("timestamp", None)
        })

    def clear(self):
        self.collection.delete_many({"session_id": self.session_id})
