# backend/services/retreiver.py

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

# Global in-memory session storage
chat_histories = {}


class RetrieverServices:
    """
    Chatbot Retriever Service for Ecommerce queries.

    Responsibilities:
    -----------------
    - Load vector database (AstraDB) as retriever.
    - Initialize Groq/OpenAI LLM for response generation.
    - Build a LangChain pipeline with prompt templates.
    - Maintain per-session chat history with RunnableWithMessageHistory.

    Attributes:
    -----------
    llm : ChatGroq | ChatOpenAI
        Large language model instance.
    retriever : BaseRetriever
        Vector store retriever for semantic search.
    prompt : ChatPromptTemplate
        Prompt template with system + human instructions.
    chain_with_history : RunnableWithMessageHistory
        Runnable chain supporting conversational memory.
    """

    def __init__(self, provider: str = "groq"):
        """
        Initialize the retriever service with an LLM provider.

        Parameters
        ----------
        provider : str, optional
            LLM provider name ("groq" or "openai"), default is "groq".

        Raises
        ------
        ValueError
            If the provider is not supported.
        """
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

        # Vector retriever
        vstore = DataIngestion().run()
        self.retriever = vstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        # Prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", PRODUCT_BOT_PROMPT),
            ("human", "{question}")
        ])

        # Core chain:
        # - Pass question directly to retriever as query
        # - Collect context + question for LLM prompt
        base_chain = (
            {
                "context": (lambda x: self.retriever.invoke(x["question"])),
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        # Wrap with chat history
        self.chain_with_history = RunnableWithMessageHistory(
            base_chain,
            self._get_session_history,
            input_messages_key="question",
            history_messages_key="history"
        )

    def _get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """
        Retrieve or create chat history for a session.

        Parameters
        ----------
        session_id : str
            Unique identifier for the chat session.

        Returns
        -------
        InMemoryChatMessageHistory
            In-memory history object for the session.
        """
        if session_id not in chat_histories:
            chat_histories[session_id] = InMemoryChatMessageHistory()
        return chat_histories[session_id]

    def get_answer(self, query: str, session_id: str = "default") -> str:
        """
        Generate an AI-powered answer for a user query.

        Parameters
        ----------
        query : str
            Customer query or product-related question.
        session_id : str, optional
            Session identifier for maintaining chat history.

        Returns
        -------
        str
            Chatbot's generated response.
        """
        return self.chain_with_history.invoke(
            {"question": query},
            config={"configurable": {"session_id": session_id}}
        )
