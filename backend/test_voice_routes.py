# from fastapi import FastAPI, UploadFile, File

# app = FastAPI()

# @app.post("/api/voice/query-json")
# async def test_endpoint(file: UploadFile = File(...)):
#     return {"message": "Working!", "filename": file.filename}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("test_voice_routes:app", host="127.0.0.1", port=8000, reload=True)
    
    
#     ///////////////////////////
#     from fastapi import APIRouter
# from pydantic import BaseModel
# from fastapi.responses import JSONResponse
# from services.chatbot_services import ChatbotServices
# from gtts import gTTS
# import os, uuid, logging

# logger = logging.getLogger(__name__)

# chat_router = APIRouter()

# OUTPUT_DIR = "responses"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# class ChatRequest(BaseModel):
#     query: str
#     session_id: str

# @chat_router.post("/query")
# async def chat_query(payload: ChatRequest):
#     """
#     Accepts a text query, gets raw chatbot response, 
#     generates TTS, and returns both.
#     """
#     try:
#         # Get chatbot response
#         chatbot_service = ChatbotServices()
#         response = chatbot_service.get_product_info(payload.query, payload.session_id)
#         raw_text = response.get("answer") or str(response) or "No response from chatbot."
#         logger.info(f"Chatbot response: {raw_text}")

#         # Generate TTS audio if response exists
#         tts_file_path = None
#         if raw_text.strip():
#             tts = gTTS(text=raw_text, lang="en")
#             filename = f"speech_{uuid.uuid4().hex}.mp3"
#             tts_file_path = os.path.join(OUTPUT_DIR, filename)
#             tts.save(tts_file_path)
#             logger.info(f"TTS saved: {tts_file_path}")

#         return JSONResponse(
#             content={
#                 "raw_text": raw_text,
#                 "audio_path": f"/static/{os.path.basename(tts_file_path)}" if tts_file_path else None
#             }
#         )

#     except Exception as e:
#         logger.exception("Error in chat_query")
#         return JSONResponse(
#             content={"error": "Failed to process query", "details": str(e)},
#             status_code=500
#         )







# # backend/services/retreiver.py

#test  code of retriever . this tested code which work fine
# # backend/services/retreiver.py

# from langchain_core.chat_history import InMemoryChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain.schema.runnable import RunnablePassthrough
# from langchain.schema.output_parser import StrOutputParser
# from langchain.prompts import ChatPromptTemplate
# from langchain_groq import ChatGroq
# from langchain_openai import ChatOpenAI
# import os

# from ingestion.data_ingestion import DataIngestion
# from config.setting import get_llm_config
# from prompt_library.system_prompt import PRODUCT_BOT_PROMPT

# # Global in-memory session storage
# chat_histories = {}


# class RetrieverServices:
#     """
#     Chatbot Retriever Service for Ecommerce queries.

#     Responsibilities:
#     -----------------
#     - Load vector database (AstraDB) as retriever.
#     - Initialize Groq/OpenAI LLM for response generation.
#     - Build a LangChain pipeline with prompt templates.
#     - Maintain per-session chat history with RunnableWithMessageHistory.

#     Attributes:
#     -----------
#     llm : ChatGroq | ChatOpenAI
#         Large language model instance.
#     retriever : BaseRetriever
#         Vector store retriever for semantic search.
#     prompt : ChatPromptTemplate
#         Prompt template with system + human instructions.
#     chain_with_history : RunnableWithMessageHistory
#         Runnable chain supporting conversational memory.
#     """

#     def __init__(self, provider: str = "groq"):
#         """
#         Initialize the retriever service with an LLM provider.

#         Parameters
#         ----------
#         provider : str, optional
#             LLM provider name ("groq" or "openai"), default is "groq".

#         Raises
#         ------
#         ValueError
#             If the provider is not supported.
#         """
#         llm_config = get_llm_config(provider)

#         # Initialize LLM
#         if provider == "groq":
#             self.llm = ChatGroq(
#                 api_key=os.getenv("GROQ_API_KEY"),
#                 model=llm_config.get("model", "llama-3.1-70b"),
#                 temperature=llm_config.get("temperature", 0.2),
#             )
#         elif provider == "openai":
#             self.llm = ChatOpenAI(
#                 api_key=os.getenv("OPENAI_API_KEY"),
#                 model=llm_config.get("model", "gpt-4"),
#                 temperature=llm_config.get("temperature", 0.2),
#             )
#         else:
#             raise ValueError(f"Unsupported provider: {provider}")

#         # Vector retriever
#         vstore = DataIngestion().run()
#         self.retriever = vstore.as_retriever(
#             search_type="similarity",
#             search_kwargs={"k": 3}
#         )

#         # Prompt template
#         self.prompt = ChatPromptTemplate.from_messages([
#             ("system", PRODUCT_BOT_PROMPT),
#             ("human", "{question}")
#         ])

#         # Core chain:
#         # - Pass question directly to retriever as query
#         # - Collect context + question for LLM prompt
#         base_chain = (
#             {
#                 "context": (lambda x: self.retriever.invoke(x["question"])),
#                 "question": RunnablePassthrough()
#             }
#             | self.prompt
#             | self.llm
#             | StrOutputParser()
#         )

#         # Wrap with chat history
#         self.chain_with_history = RunnableWithMessageHistory(
#             base_chain,
#             self._get_session_history,
#             input_messages_key="question",
#             history_messages_key="history"
#         )

#     def _get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
#         """
#         Retrieve or create chat history for a session.

#         Parameters
#         ----------
#         session_id : str
#             Unique identifier for the chat session.

#         Returns
#         -------
#         InMemoryChatMessageHistory
#             In-memory history object for the session.
#         """
#         if session_id not in chat_histories:
#             chat_histories[session_id] = InMemoryChatMessageHistory()
#         return chat_histories[session_id]

#     def get_answer(self, query: str, session_id: str = "default") -> str:
#         """
#         Generate an AI-powered answer for a user query.

#         Parameters
#         ----------
#         query : str
#             Customer query or product-related question.
#         session_id : str, optional
#             Session identifier for maintaining chat history.

#         Returns
#         -------
#         str
#             Chatbot's generated response.
#         """
#         return self.chain_with_history.invoke(
#             {"question": query},
#             config={"configurable": {"session_id": session_id}}
#         )












#this code of data ingesyion which also working fine
# from ingestion.csv_loader import CSVLoader
# from ingestion.api_loader import APILoader
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_openai import OpenAIEmbeddings
# from langchain_astradb import AstraDBVectorStore

# from config.setting import (
#     CSV_FILE_PATH,
#     API_URL,
#     ASTRA_DB_API_ENDPOINT,
#     ASTRA_DB_APPLICATION_TOKEN,
#     ASTRA_DB_KEYSPACE,
#     EMBEDDINGS_CONFIG,
#     VECTORSTORE_CONFIG,
# )

# from utils.logging import get_logger
# from utils.exceptions import AppException

# # Initialize logger
# logger = get_logger(__name__)


# class DataIngestion:
#     """
#     DataIngestion pipeline responsible for:
#     1. Loading product data from CSV and API sources.
#     2. Initializing embeddings dynamically (HuggingFace or OpenAI).
#     3. Initializing vector store dynamically (AstraDB).
#     4. Adding all documents to the vector store.

#     Returns:
#         vstore: Configured vector store instance with ingested documents.
#     """

#     def __init__(self):
#         """Initialize loaders for CSV and API sources."""
#         self.csv_loader = CSVLoader(CSV_FILE_PATH)
#         self.api_loader = APILoader(API_URL)

#     def run(self):
#         """
#         Execute the ingestion pipeline:
#         - Load documents from CSV and API.
#         - Setup embeddings (HuggingFace/OpenAI).
#         - Setup vector store (AstraDB).
#         - Store all documents in vector store.

#         Returns:
#             vstore: Vector store populated with ingested documents.

#         Raises:
#             AppException: If any step in the ingestion pipeline fails.
#         """
#         try:
#             logger.info("🚀 Starting data ingestion pipeline...")

#             # 1. Load data
#             logger.info("📥 Loading data from CSV and API...")
#             csv_docs = self.csv_loader.load()
#             api_docs = self.api_loader.load()
#             all_docs = csv_docs + api_docs
#             logger.info(f"✅ Loaded {len(all_docs)} documents (CSV + API)")

#             # 2. Setup embeddings dynamically
#             provider = EMBEDDINGS_CONFIG.get("provider", "huggingface")
#             logger.info(f"🔍 Initializing embeddings provider: {provider}")

#             if provider == "huggingface":
#                 embeddings = HuggingFaceEmbeddings(
#                     model_name=EMBEDDINGS_CONFIG["model"]
#                 )
#             elif provider == "openai":
#                 embeddings = OpenAIEmbeddings(
#                     model=EMBEDDINGS_CONFIG["model"]
#                 )
#             else:
#                 logger.error(f"❌ Unsupported embeddings provider: {provider}")
#                 raise AppException(f"Unsupported embeddings provider: {provider}")

#             # 3. Setup vector store dynamically
#             vstore_provider = VECTORSTORE_CONFIG.get("provider", "astradb")
#             logger.info(f"🗄️ Initializing vector store provider: {vstore_provider}")

#             if vstore_provider == "astradb":
#                 vstore = AstraDBVectorStore(
#                     embedding=embeddings,
#                     collection_name="chatbotecomm",
#                     api_endpoint=ASTRA_DB_API_ENDPOINT,
#                     token=ASTRA_DB_APPLICATION_TOKEN,
#                     namespace=ASTRA_DB_KEYSPACE,
#                 )
#             else:
#                 logger.error(f"❌ Unsupported vectorstore provider: {vstore_provider}")
#                 raise AppException(f"Unsupported vectorstore provider: {vstore_provider}")

#             # 4. Add docs to vector store
#             logger.info("📤 Adding documents to vector store...")
#             vstore.add_documents(all_docs)

#             logger.info(f"✅ {len(all_docs)} documents successfully added to {vstore_provider}")
#             return vstore

#         except Exception as e:
#             logger.exception(f"❌ Error in DataIngestion pipeline: {e}")
#             raise AppException(f"DataIngestion failed: {str(e)}")






# #routes.p
# from fastapi import APIRouter, Query
# from utils.exceptions import AppException
# from services.chatbot_services import ChatbotServices
# from db.client import get_collection  # import from your db folder

# routes_router = APIRouter(tags=["Chatbot"])
# chatbot_service = ChatbotServices()

# def get_history(session_id: str):
#     collection = get_collection("chat_history")
#     # Fetch messages for the session
#     rows = collection.find({"session_id": session_id})
#     return [{"sender": row["sender"], "text": row["message"]} for row in rows]

# @routes_router.get("/history")
# async def get_chat_history(session_id: str):
#     try:
#         return get_history(session_id)
#     except Exception as e:
#         return {"error": str(e), "status_code": 500}

# @routes_router.get("/ask_product")
# async def ask_product(
#     query: str = Query(..., description="Customer product-related query"),
#     session_id: str = Query("default", description="Unique session ID to maintain chat history")
# ):
#     try:
#         return chatbot_service.get_product_info(query, session_id=session_id)
#     except AppException as e:
#         return {"error": e.message, "status_code": e.status_code}
#     except Exception as e:
#         return {"error": str(e), "status_code": 500}




# from astrapy import DataAPIClient
# import os, time

# ASTRA_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
# ASTRA_DB_URL = "https://39077156-05eb-46f5-80c3-55be2964c72b-us-east-2.apps.astra.datastax.com"

# client = DataAPIClient(ASTRA_TOKEN)
# db = client.get_database_by_api_endpoint(ASTRA_DB_URL)


# def get_collection(name: str):
#     """Create or return a collection safely."""
#     try:
#         # ✅ List existing collections
#         existing = db.list_collections()
#         existing_names = [c["name"] for c in existing.get("data", {}).get("collections", [])]

#         # ✅ Create if missing
#         if name not in existing_names:
#             print(f"[INFO] Creating collection '{name}' ...")
#             db.create_collection(name)
#             # Wait until ready
#             for i in range(10):
#                 time.sleep(0.5)
#                 existing = db.list_collections()
#                 existing_names = [c["name"] for c in existing.get("data", {}).get("collections", [])]
#                 if name in existing_names:
#                     print(f"[INFO] Collection '{name}' is ready.")
#                     break
#             else:
#                 raise RuntimeError(f"Collection '{name}' not ready after 5s.")

#         # ✅ Return collection handle
#         return db.get_collection(name)

#     except Exception as e:
#         print(f"[ERROR] get_collection failed: {e}")
#         raise



# # routes.py

# from fastapi import APIRouter, Query, HTTPException
# from utils.exceptions import AppException
# from services.chatbot_services import ChatbotServices
# from db.chat_history_setup import get_collection  # Astra DB connection

# routes_router = APIRouter(tags=["Chatbot"])
# chatbot_service = ChatbotServices()


# @routes_router.get("/ask_product")
# async def ask_product(
#     query: str = Query(..., description="Customer product-related query"),
#     session_id: str = Query("default", description="Unique session ID to maintain chat history")
# ):
#     """
#     Ask product-related question and auto-save chat messages to history.
#     """
#     try:
#         # Get DB collection
#         collection = get_collection("chat_history")

#         # ✅ Save user's message first
#         collection.insert_one({
#             "session_id": session_id,
#             "sender": "user",
#             "message": query
#         })

#         # ✅ Generate chatbot response
#         response = chatbot_service.get_product_info(query, session_id=session_id)

#         # ✅ Save bot response
#         collection.insert_one({
#             "session_id": session_id,
#             "sender": "bot",
#             "message": response.get("response", str(response))  # handle dict or string
#         })

#         # ✅ Return chatbot reply
#         return {
#             "session_id": session_id,
#             "query": query,
#             "response": response.get("response", str(response))
#         }

#     except AppException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.message)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))







#voice_routes.jsx
# "use client";
# import React, { useState, useRef, useEffect } from "react";
# import { motion } from "framer-motion";

# const BACKEND_URL = "http://localhost:8000";

# export default function VoiceChat() {
#   const [messages, setMessages] = useState([]);
#   const [input, setInput] = useState("");
#   const [isRecording, setIsRecording] = useState(false);
#   const [loading, setLoading] = useState(false);
#   const [error, setError] = useState(null);

#   const [sessionId] = useState(() =>
#     crypto.randomUUID
#       ? crypto.randomUUID()
#       : "session_" + Math.random().toString(36).substring(2, 9)
#   );

#   const mediaRecorderRef = useRef(null);
#   const audioChunksRef = useRef([]);
#   const chatBoxRef = useRef(null);

#   // Auto scroll down
#   useEffect(() => {
#     if (chatBoxRef.current) {
#       chatBoxRef.current.scrollTo({
#         top: chatBoxRef.current.scrollHeight,
#         behavior: "smooth",
#       });
#     }
#   }, [messages]);

#   // 🧠 Load history on start
#   useEffect(() => {
#     const loadHistory = async () => {
#       try {
#         const res = await fetch(`${BACKEND_URL}/api/history/${sessionId}`);
#         const data = await res.json();
#         if (data.history) setMessages(data.history);
#       } catch (err) {
#         console.error("Failed to load history", err);
#       }
#     };
#     loadHistory();
#   }, [sessionId]);

#   // Save message to backend
#   const saveToHistory = async (message) => {
#     try {
#       await fetch(`${BACKEND_URL}/api/history/${sessionId}`, {
#         method: "POST",
#         headers: { "Content-Type": "application/json" },
#         body: JSON.stringify(message),
#       });
#     } catch (err) {
#       console.error("Failed to save history", err);
#     }
#   };

#   // ---------------------- Helper: Detect image URLs or Markdown ----------------------
#   const parseBotReply = (reply) => {
#     if (!reply) return { contentType: "text", text: "No reply" };
#     const markdownMatch = reply.match(/\[.*?\]\((https?:\/\/[^\s)]+)\)/);
#     const markdownUrl = markdownMatch ? markdownMatch[1] : null;
#     const plainUrlMatch = reply.match(/https?:\/\/[^\s]+/);
#     const url = markdownUrl || (plainUrlMatch ? plainUrlMatch[0] : null);
#     const isImage = url && /\.(jpeg|jpg|gif|png|webp)$/i.test(url);
#     if (isImage) {
#       const cleanText = reply
#         .replace(/\[.*?\]\((https?:\/\/[^\s)]+)\)/, "")
#         .replace(url, "")
#         .trim();
#       return { contentType: "image", text: cleanText, imageUrl: url };
#     }
#     return { contentType: "text", text: reply };
#   };

#   // ---------------------- TEXT CHAT ----------------------
#   const sendTextMessage = async () => {
#     if (!input.trim()) return;
#     setLoading(true);
#     setError(null);

#     const userMsg = {
#       id: Date.now() + "_u",
#       role: "user",
#       text: input,
#       timestamp: new Date().toLocaleTimeString(),
#     };
#     setMessages((prev) => [...prev, userMsg]);
#     saveToHistory(userMsg);
 

#     try {
#       const res = await fetch(
#         `${BACKEND_URL}/api/chat/ask_product?query=${encodeURIComponent(input)}&session_id=${sessionId}`
#         );

#       if (!res.ok) throw new Error(await res.text());
#       const data = await res.json();
#       const parsed = parseBotReply(data.answer);

#       const aiMsg = {
#         id: Date.now() + "_a",
#         role: "ai",
#         ...parsed,
#         timestamp: new Date().toLocaleTimeString(),
#       };
#       setMessages((prev) => [...prev, aiMsg]);
#       saveToHistory(aiMsg);
#       setInput("");
#     } catch (err) {
#       setError(err.message);
#     } finally {
#       setLoading(false);
#     }
#   };

#   // ---------------------- VOICE CHAT ----------------------
#   const startRecording = async () => {
#     try {
#       setError(null);
#       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
#       const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
#       mediaRecorderRef.current = recorder;
#       audioChunksRef.current = [];
#       recorder.ondataavailable = (e) => {
#         if (e.data.size > 0) audioChunksRef.current.push(e.data);
#       };
#       recorder.onstop = () => sendVoiceMessage();
#       recorder.start();
#       setIsRecording(true);
#     } catch (err) {
#       setError("🎤 Microphone access denied.");
#     }
#   };

#   const stopRecording = () => {
#     if (mediaRecorderRef.current?.state === "recording") {
#       mediaRecorderRef.current.stop();
#       mediaRecorderRef.current.stream.getTracks().forEach((t) => t.stop());
#     }
#     setIsRecording(false);
#   };

#   const sendVoiceMessage = async () => {
#     if (!audioChunksRef.current.length) return;
#     setLoading(true);
#     try {
#       const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
#       const formData = new FormData();
#       formData.append("file", blob, "voice.webm");
#       formData.append("session_id", sessionId);

#       const res = await fetch(`${BACKEND_URL}/api/voice/chat`, {
#         method: "POST",
#         body: formData,
#       });

#       if (!res.ok) throw new Error(await res.text());
#       const data = await res.json();
#       const parsed = parseBotReply(data.ai_response);

#       const userMsg = {
#         id: Date.now() + "_u",
#         role: "user",
#         text: data.user_query || "🎤 (voice input)",
#         timestamp: new Date().toLocaleTimeString(),
#       };
#       const aiMsg = {
#         id: Date.now() + "_a",
#         role: "ai",
#         ...parsed,
#         timestamp: new Date().toLocaleTimeString(),
#         audioUrl: `${BACKEND_URL}${data.audio_path}`,
#       };

#       setMessages((prev) => [...prev, userMsg, aiMsg]);
#       saveToHistory(userMsg);
#       saveToHistory(aiMsg);
#     } catch (err) {
#       setError(err.message || "Voice processing failed");
#     } finally {
#       setLoading(false);
#       audioChunksRef.current = [];
#     }
#   };

#   // ---------------------- UI ----------------------
#   return (
#     <div className="min-h-screen w-full bg-[#050b25] flex justify-center items-center p-4 sm:p-6">
#       <motion.div
#         className="w-full max-w-lg bg-[#0d1645]/90 backdrop-blur-lg border border-blue-400/20 shadow-[0_0_40px_rgba(0,150,255,0.25)] rounded-3xl p-6 text-white"
#         initial={{ opacity: 0, scale: 0.9, y: 30 }}
#         animate={{ opacity: 1, scale: 1, y: 0 }}
#         transition={{ duration: 0.6, ease: "easeOut" }}
#       >
#         <h2 className="text-2xl sm:text-3xl font-bold mb-4 text-center text-blue-300">
#           🤖 Smart AI ChatBot
#         </h2>

#         {/* Chat Box */}
#         <div
#           ref={chatBoxRef}
#           className="border border-blue-500/30 rounded-2xl p-4 h-96 overflow-y-auto bg-[#111b3c]/70 shadow-inner scroll-smooth"
#         >
#           {messages.length === 0 && (
#             <p className="text-sm text-gray-400 text-center mt-20">
#               No messages yet. Start chatting ✨
#             </p>
#           )}

#           {messages.map((msg) => (
#             <motion.div
#               key={msg.id}
#               initial={{ opacity: 0, y: 20 }}
#               animate={{ opacity: 1, y: 0 }}
#               transition={{ duration: 0.3 }}
#               className={`mb-3 p-3 rounded-2xl border ${
#                 msg.role === "user"
#                   ? "bg-blue-800/60 border-blue-400/30 text-right ml-auto max-w-[80%]"
#                   : "bg-blue-900/40 border-blue-300/20 text-left mr-auto max-w-[80%]"
#               }`}
#             >
#               {msg.contentType === "image" && msg.imageUrl ? (
#                 <>
#                   {msg.text && (
#                     <p className="text-sm whitespace-pre-line mb-2">{msg.text}</p>
#                   )}
#                   <img
#                     src={msg.imageUrl}
#                     alt="AI"
#                     className="rounded-xl mt-1 w-full max-h-64 object-contain border border-blue-300/30"
#                   />
#                 </>
#               ) : (
#                 <p className="text-sm whitespace-pre-line break-words">
#                   {msg.text}
#                 </p>
#               )}

#               <p className="text-xs text-gray-400 mt-1">{msg.timestamp}</p>

#               {msg.role === "ai" && msg.audioUrl && (
#                 <div className="mt-2">
#                   <audio controls src={msg.audioUrl} className="w-full" />
#                 </div>
#               )}
#             </motion.div>
#           ))}

#           {error && (
#             <p className="text-red-400 text-xs mt-2 text-center">⚠ {error}</p>
#           )}
#         </div>

#         {/* Input and buttons */}
#         <div className="flex gap-2 mt-4">
#           <input
#             type="text"
#             value={input}
#             onChange={(e) => setInput(e.target.value)}
#             placeholder="💬 Type here..."
#             className="flex-1 bg-[#0e1536] border border-blue-400/30 text-white px-3 py-2 rounded-2xl focus:ring-2 focus:ring-blue-400"
#           />
#           <motion.button
#             whileTap={{ scale: 0.9 }}
#             onClick={sendTextMessage}
#             disabled={loading}
#             className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-2xl shadow-md"
#           >
#             Send 🚀
#           </motion.button>
#         </div>

#         {/* Voice Buttons */}
#         <div className="flex justify-center gap-3 mt-4 flex-wrap">
#           {!isRecording ? (
#             <motion.button
#               whileHover={{ scale: 1.05 }}
#               whileTap={{ scale: 0.9 }}
#               onClick={startRecording}
#               disabled={loading}
#               className="bg-red-600 hover:bg-red-700 text-white px-5 py-2 rounded-2xl shadow-md"
#             >
#               🎙 Start
#             </motion.button>
#           ) : (
#             <motion.button
#               whileTap={{ scale: 0.9 }}
#               onClick={stopRecording}
#               className="bg-gray-700 hover:bg-gray-800 text-white px-5 py-2 rounded-2xl shadow-md"
#             >
#               ⏹ Stop
#             </motion.button>
#           )}

#           <motion.button
#             whileTap={{ scale: 0.9 }}
#             onClick={() => setMessages([])}
#             className="bg-gray-300 hover:bg-gray-400 text-black px-5 py-2 rounded-2xl shadow-md"
#           >
#             Clear 🧹
#           </motion.button>
#         </div>
#       </motion.div>
#     </div>
#   );
# }
