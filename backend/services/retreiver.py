from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import os
from ingestion.data_ingestion import DataIngestion
from config.setting import get_llm_config
from prompt_library.system_prompt import PRODUCT_BOT_PROMPT
from datetime import datetime


class RetrieverServices:
    """
    Chatbot Retriever Service for Ecommerce queries with AstraDB chat history persistence.
    """

    def __init__(self, provider: str = "groq"):
        llm_config = get_llm_config(provider)

        # Initialize LLM
        if provider == "groq":
            self.llm = ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model=llm_config.get("model", "llama-3.1-70b"),
                temperature=llm_config.get("temperature", 0.2),
            )
        elif provider == "openai":
            self.llm = ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                model=llm_config.get("model", "gpt-4"),
                temperature=llm_config.get("temperature", 0.2),
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Vector retriever (for product data)
        vstore = DataIngestion().run()
        self.retriever = vstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

        # Astra DB connection for chat history
        self.db = DataIngestion().get_astra_db()

        # Prompt template for conversation
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", PRODUCT_BOT_PROMPT),
            ("human", "{question}")
        ])

        # Core chain logic
        base_chain = (
            {
                "context": lambda x: self.retriever.invoke(x["question"]),
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        # Wrap with message history
        self.chain_with_history = RunnableWithMessageHistory(
            base_chain,
            self._get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )

    # ========== CHAT MEMORY HANDLING ========== #
    def _get_session_history(self, session_id: str):
        """Retrieve chat history for a given session."""
        messages = self._load_history_from_db(session_id)
        memory = InMemoryChatMessageHistory()

        for msg in messages:
            # Flexible parsing — handles both formats
            if "user" in msg and "bot" in msg:
                memory.add_user_message(msg["user"])
                memory.add_ai_message(msg["bot"])
            elif "role" in msg and msg["role"] == "user":
                memory.add_user_message(msg.get("text", ""))
            elif "role" in msg and msg["role"] == "assistant":
                memory.add_ai_message(msg.get("text", ""))
            else:
                print(f"⚠️ Skipping malformed message: {msg}")

        return memory

    def _load_history_from_db(self, session_id: str):
        """Fetch chat history from Astra DB for session_id."""
        try:
            collection = self.db.get_collection("chat_history")
            docs = collection.find({"session_id": session_id})
            return sorted(docs, key=lambda x: x.get("timestamp", ""))
        except Exception as e:
            print(f"[WARN] Could not load chat history: {e}")
            return []

    def _save_message_to_db(self, session_id: str, user_msg: str, bot_msg: str):
        """Save chat messages to Astra DB."""
        try:
            collection = self.db.get_collection("chat_history")
            doc = {
                "session_id": session_id,
                "user": user_msg,
                "bot": bot_msg,
                "timestamp": datetime.utcnow().isoformat(),
            }
            collection.insert_one(doc)
            print(f"✅ Message inserted for session {session_id}")
        except Exception as e:
            print(f"[ERROR] Failed to save chat message: {e}")

    # ========== MAIN CHAT FUNCTION ========== #
    def get_answer(self, query: str, session_id: str = "default") -> str:
        """Generate answer + persist conversation to Astra DB."""
        try:
            response = self.chain_with_history.invoke(
                {"question": query},
                config={"configurable": {"session_id": session_id}},
            )

            # Save user + AI message
            self._save_message_to_db(session_id, query, response)

            return response

        except Exception as e:
            print(f"[ERROR] Unexpected error in get_answer: {e}")
            return "⚠️ Sorry, something went wrong while processing your request."
