from datetime import datetime
from db.client import connect_to_database
# from client import connect_to_database
from astrapy.constants import VectorMetric
from astrapy.info import (
    CollectionDefinition,
    CollectionVectorOptions,
    VectorServiceOptions,
)

COLLECTION_NAME = "chat_history"


# -------------------------------
# 1️⃣ Create the collection (run once)
# -------------------------------
def create_collection():
    database = connect_to_database()

    # Check if the collection already exists
    existing_collections = [c.name for c in database.list_collections()]
    if COLLECTION_NAME in existing_collections:
        print(f"⚠️ Collection '{COLLECTION_NAME}' already exists.")
        return

    # Create with vector search enabled
    collection = database.create_collection(
        COLLECTION_NAME,
        definition=CollectionDefinition(
            vector=CollectionVectorOptions(
                metric=VectorMetric.COSINE,
                service=VectorServiceOptions(
                    provider="nvidia",
                    model_name="NV-Embed-QA",
                ),
            )
        ),
    )

    print(f"✅ Created collection: {collection.full_name}")


# -------------------------------
# 2️⃣ Insert chat message
# -------------------------------
def insert_message(message_data: dict):
    """
    Insert a chat message into Astra DB.
    Expects a dict with fields: session_id, role, text, timestamp, etc.
    """
    try:
        db = connect_to_database()
        collection = db.get_collection(COLLECTION_NAME)

        # Ensure timestamp exists
        if "timestamp" not in message_data:
            message_data["timestamp"] = datetime.utcnow().isoformat()

        collection.insert_one(message_data)
        print(f"✅ Message inserted for session {message_data.get('session_id')}")
        return True
    except Exception as e:
        print(f"❌ Failed to insert message: {e}")
        raise


# -------------------------------
# 3️⃣ Fetch chat history
# -------------------------------
def fetch_history(session_id: str):
    """
    Fetch all chat messages for a specific session_id.
    """
    try:
        db = connect_to_database()
        collection = db.get_collection(COLLECTION_NAME)

        cursor = collection.find({"session_id": session_id})
        history = list(cursor)
        print(f"💬 Found {len(history)} messages for session {session_id}")
        return history
    except Exception as e:
        print(f"❌ Failed to fetch history: {e}")
        raise


# -------------------------------
# 4️⃣ Manual test (optional)
# -------------------------------
if __name__ == "__main__":
    create_collection()  # Run once to ensure collection exists

    test_msg = {
        "session_id": "test_session_123",
        "role": "user",
        "text": "Hello, I need a blue shirt",
        "timestamp": datetime.utcnow().isoformat(),
    }

    insert_message(test_msg)
    msgs = fetch_history("test_session_123")

    for msg in msgs:
        print(f"- [{msg['role']}] {msg['text']}")



if __name__ == "__main__":
    create_collection()   # <-- This creates 'chat_history'
