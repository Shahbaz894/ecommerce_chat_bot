"use client";
import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";

const BACKEND_URL = "http://localhost:8000";

export default function VoiceChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [sessionId] = useState(() =>
    crypto.randomUUID
      ? crypto.randomUUID()
      : "session_" + Math.random().toString(36).substring(2, 9)
  );

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const chatBoxRef = useRef(null);

  // --- Scroll to bottom when messages update ---
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTo({
        top: chatBoxRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  // ---------------------- Helper: Detect image URLs or Markdown ----------------------
  const parseBotReply = (reply) => {
    if (!reply) return { contentType: "text", text: "No reply" };

    // Check for Markdown link syntax [text](url)
    const markdownMatch = reply.match(/\[.*?\]\((https?:\/\/[^\s)]+)\)/);
    const markdownUrl = markdownMatch ? markdownMatch[1] : null;

    // Check for plain URL
    const plainUrlMatch = reply.match(/https?:\/\/[^\s]+/);
    const url = markdownUrl || (plainUrlMatch ? plainUrlMatch[0] : null);
    const isImage = url && /\.(jpeg|jpg|gif|png|webp)$/i.test(url);

    if (isImage) {
      const cleanText = reply
        .replace(/\[.*?\]\((https?:\/\/[^\s)]+)\)/, "")
        .replace(url, "")
        .trim();
      return { contentType: "image", text: cleanText, imageUrl: url };
    }

    return { contentType: "text", text: reply };
  };

  // ---------------------- TEXT CHAT ----------------------
  const sendTextMessage = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(
        `${BACKEND_URL}/api/ask_product?query=${encodeURIComponent(
          input
        )}&session_id=${sessionId}`
      );
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();

      const parsed = parseBotReply(data.answer);

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + "_u",
          role: "user",
          text: input,
          timestamp: new Date().toLocaleTimeString(),
        },
        {
          id: Date.now() + "_a",
          role: "ai",
          ...parsed,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
      setInput("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ---------------------- VOICE CHAT ----------------------
  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = () => sendVoiceMessage();
      recorder.start();
      setIsRecording(true);
    } catch (err) {
      setError("🎤 Microphone access denied.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((t) => t.stop());
    }
    setIsRecording(false);
  };

  const sendVoiceMessage = async () => {
    if (!audioChunksRef.current.length) return;
    setLoading(true);
    try {
      const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("file", blob, "voice.webm");
      formData.append("session_id", sessionId);

      const res = await fetch(`${BACKEND_URL}/api/voice/chat`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();

      const parsed = parseBotReply(data.ai_response);

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + "_u",
          role: "user",
          text: data.user_query || "🎤 (voice input)",
          timestamp: new Date().toLocaleTimeString(),
        },
        {
          id: Date.now() + "_a",
          role: "ai",
          ...parsed,
          timestamp: new Date().toLocaleTimeString(),
          audioUrl: `${BACKEND_URL}${data.audio_path}`,
        },
      ]);
    } catch (err) {
      setError(err.message || "Voice processing failed");
    } finally {
      setLoading(false);
      audioChunksRef.current = [];
    }
  };

  // ---------------------- UI ----------------------
  return (
    <div className="min-h-screen w-full bg-[#050b25] flex justify-center items-center p-4 sm:p-6">
      <motion.div
        className="w-full max-w-lg bg-[#0d1645]/90 backdrop-blur-lg border border-blue-400/20 shadow-[0_0_40px_rgba(0,150,255,0.25)] rounded-3xl p-6 text-white"
        initial={{ opacity: 0, scale: 0.9, y: 30 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <h2 className="text-2xl sm:text-3xl font-bold mb-4 text-center text-blue-300">
          🤖 Smart AI E-Commerce ChatBot
        </h2>

        {/* Chat Box */}
        <div
          ref={chatBoxRef}
          className="border border-blue-500/30 rounded-2xl p-4 h-96 overflow-y-auto bg-[#111b3c]/70 shadow-inner scroll-smooth"
        >
          {messages.length === 0 && (
            <p className="text-sm text-gray-400 text-center mt-20">
              No messages yet. Type or record to start ✨
            </p>
          )}

          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`mb-3 p-3 rounded-2xl border ${
                msg.role === "user"
                  ? "bg-blue-800/60 border-blue-400/30 text-right ml-auto max-w-[80%]"
                  : "bg-blue-900/40 border-blue-300/20 text-left mr-auto max-w-[80%]"
              }`}
            >
              {/* Display text or image */}
              {msg.contentType === "image" && msg.imageUrl ? (
                <>
                  {msg.text && (
                    <p className="text-sm whitespace-pre-line mb-2">{msg.text}</p>
                  )}
                  <img
                    src={msg.imageUrl}
                    alt="AI content"
                    className="rounded-xl mt-1 w-full max-h-64 object-contain border border-blue-300/30"
                  />
                </>
              ) : (
                <p className="text-sm whitespace-pre-line break-words">
                  {msg.text}
                </p>
              )}

              <p className="text-xs text-gray-400 mt-1">{msg.timestamp}</p>

              {msg.role === "ai" && msg.audioUrl && (
                <div className="mt-2">
                  <audio controls src={msg.audioUrl} className="w-full" />
                </div>
              )}
            </motion.div>
          ))}

          {error && (
            <p className="text-red-400 text-xs mt-2 text-center">⚠ {error}</p>
          )}
          {loading && (
            <p className="text-blue-300 text-xs mt-2 text-center">
              ⏳ Processing...
            </p>
          )}
        </div>

        {/* Input Bar */}
        <div className="flex gap-2 mt-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="💬 Ask about a product..."
            className="flex-1 bg-[#0e1536] border border-blue-400/30 text-white px-3 py-2 rounded-2xl shadow-inner focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={sendTextMessage}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-2xl shadow-md transition-transform"
          >
            Send 🚀
          </motion.button>
        </div>

        {/* Voice Buttons */}
        <div className="flex justify-center gap-3 mt-4 flex-wrap">
          {!isRecording ? (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.9 }}
              onClick={startRecording}
              disabled={loading}
              className="bg-red-600 hover:bg-red-700 text-white px-5 py-2 rounded-2xl shadow-md"
            >
              🎙 Start Recording
            </motion.button>
          ) : (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.9 }}
              onClick={stopRecording}
              className="bg-gray-700 hover:bg-gray-800 text-white px-5 py-2 rounded-2xl shadow-md"
            >
              ⏹ Stop
            </motion.button>
          )}

          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={() => {
              setMessages([]);
              setError(null);
            }}
            className="bg-gray-300 hover:bg-gray-400 text-black px-5 py-2 rounded-2xl shadow-md"
          >
            Clear 🧹
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
}
