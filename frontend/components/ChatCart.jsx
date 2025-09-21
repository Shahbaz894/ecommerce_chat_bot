"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { v4 as uuidv4 } from "uuid";

const BACKEND_BASE = "http://127.0.0.1:8000";

export default function ChatCard({ title = "AI Assistant", subtitle = "Online", avatarUrl }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const bottomRef = useRef(null);

  // Generate or get session ID
  useEffect(() => {
    let id = localStorage.getItem("session_id");
    if (!id) {
      id = uuidv4();
      localStorage.setItem("session_id", id);
    }
    setSessionId(id);
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load chat history
  useEffect(() => {
    if (!sessionId) return;

    async function loadHistory() {
      try {
        const res = await fetch(`${BACKEND_BASE}/api/history?session_id=${sessionId}`);
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data)) setMessages(data);
        }
      } catch (err) {
        console.warn("History load failed:", err);
      }
    }
    loadHistory();
  }, [sessionId]);

  // 🔥 Robust URL/image detection
  const parseBotReply = (reply) => {
    if (!reply) return { type: "text", text: "No reply" };

    // Try to extract first URL if present
    const urlMatch = reply.match(/https?:\/\/[^\s]+/);
    const url = urlMatch ? urlMatch[0] : null;

    // Check if the URL is an image
    const isImage = url && /\.(jpeg|jpg|gif|png|webp)$/i.test(url);

    if (isImage) {
      return { type: "image", text: url };
    }
    return { type: "text", text: reply };
  };

  // Send message
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input, type: "text" };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(
        `${BACKEND_BASE}/api/ask_product?query=${encodeURIComponent(input)}&session_id=${sessionId}`,
        { method: "GET", headers: { "Content-Type": "application/json" } }
      );
      if (!res.ok) throw new Error("Request failed");

      const data = await res.json();
      const botReply = data.answer ?? "No reply";

      const parsed = parseBotReply(botReply);

      setMessages((prev) => [...prev, { sender: "ai", ...parsed }]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: "⚠️ Server error", type: "text" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center relative overflow-hidden">
      {/* Animated background */}
      <motion.div
        className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-indigo-900 via-black to-black"
        animate={{ backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] }}
        transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
        style={{ backgroundSize: "200% 200%" }}
      />

      {/* Chat card */}
      <div className="relative w-full max-w-md h-[650px] bg-gradient-to-br from-gray-800 via-gray-900 to-black rounded-2xl shadow-2xl border border-gray-700 flex flex-col z-10">
        {/* Header */}
        <div className="flex items-center gap-3 p-4 border-b border-gray-700 flex-shrink-0">
          <div className="relative">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-600 to-teal-400 flex items-center justify-center shadow-md overflow-hidden">
              {avatarUrl ? (
                <img src={avatarUrl} alt="avatar" className="w-full h-full object-cover" />
              ) : (
                <span className="text-white font-bold">AI</span>
              )}
            </div>
            <span className="absolute -bottom-1 -right-1 w-3 h-3 rounded-full bg-green-400 ring-2 ring-gray-900" />
          </div>
          <div className="flex-1">
            <div className="text-white font-semibold leading-tight">{title}</div>
            <div className="text-sm text-gray-400">{subtitle}</div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 px-4 py-4 overflow-y-auto space-y-3">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`p-3 rounded-lg max-w-[80%] shadow text-sm ${
                  msg.sender === "user"
                    ? "bg-gradient-to-r from-indigo-600 to-teal-400 text-black rounded-br-none"
                    : "bg-gray-800 text-gray-200 rounded-bl-none"
                }`}
              >
                {msg.type === "image" ? (
                  <img
                    src={msg.text}
                    alt="AI Response"
                    className="w-40 h-40 object-contain rounded-lg"
                  />
                ) : (
                  msg.text
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex">
              <div className="bg-gray-800 text-gray-400 p-3 rounded-lg rounded-bl-none max-w-[80%] shadow text-sm animate-pulse">
                Typing...
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Composer */}
        <div className="bg-gradient-to-t from-black/40 to-transparent p-4 border-t border-gray-700 flex-shrink-0">
          <form onSubmit={sendMessage} className="flex items-center gap-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 bg-gray-900 border border-gray-700 text-gray-100 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-600"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-indigo-600 hover:bg-indigo-500 text-black font-semibold py-2 px-4 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              {loading ? "..." : "Send"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
