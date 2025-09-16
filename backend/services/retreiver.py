from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

from ingestion.data_ingestion import DataIngestion
from config.setting import GROQ_API_KEY, get_llm_config
from prompt_library.system_prompt import PRODUCT_BOT_PROMPT

# Initialize vector store (run ingestion pipeline)
vstore = DataIngestion().run()

load_dotenv()


class RetrieverServices:
    """
    RetrieverServices integrates:
    - A vector store retriever (AstraDB in this case).
    - A Groq/OpenAI LLM.
    - A prompt that injects context + user query.

    The chain:
        user_query → retriever fetches relevant docs → LLM with system prompt → response.
    """

    def __init__(self, provider: str = "groq"):
        """
        Initialize the retriever service.
        Args:
            provider (str): Which LLM to use ("groq" or "openai").
        """
        llm_config = get_llm_config(provider)

        # ✅ Initialize LLM
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

        # ✅ Create retriever (search top 3 docs)
        self.retriever = vstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3},
        )

        # ✅ Prompt template (system + user)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", PRODUCT_BOT_PROMPT),
            ("human", "{question}")
        ])

        # ✅ Build chain
        self.chain = (
            {
                "context": self.retriever,        # retriever works with string input
                "question": RunnablePassthrough() # passthrough user query
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def get_answer(self, query: str) -> str:
        """
        Query the retriever + LLM chain.

        Args:
            query (str): User's natural language question.
        Returns:
            str: AI-generated response.
        """
        # ✅ Only pass plain string
        response = self.chain.invoke(query)
        return response
