"use client";
import React, { useState, useRef } from "react";

const BACKEND_URL = "http://localhost:8000";

const ChatBot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // ✅ generate session ID safely (SSR fix: no window reference before render)
  const [sessionId] = useState(() =>
    typeof window !== "undefined" && window.crypto?.randomUUID
      ? crypto.randomUUID()
      : "session_" + Math.random().toString(36).slice(2, 9)
  );

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // ------------------- TEXT CHAT -------------------
  const sendTextMessage = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${BACKEND_URL}/api/chat/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input, session_id: sessionId }),
      });

      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();

      const userMessage = {
        id: Date.now() + "_u",
        type: "user",
        text: input,
        timestamp: new Date().toLocaleTimeString(),
      };

      const aiMessage = {
        id: Date.now() + "_a",
        type: "ai",
        text: data.answer || "No response",
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, userMessage, aiMessage]);
      setInput("");
    } catch (err) {
      console.error("Text chat error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ------------------- VOICE CHAT -------------------
  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data?.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => sendVoiceMessage();

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setError("Microphone access denied.");
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
      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("file", audioBlob, "voice.webm");
      formData.append("session_id", sessionId);

      const res = await fetch(`${BACKEND_URL}/api/voice/chat`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();

      const userMessage = {
        id: Date.now() + "_u",
        type: "user",
        text: data.user_query || "🎤 (voice input)",
        timestamp: new Date().toLocaleTimeString(),
      };

      const aiMessage = {
        id: Date.now() + "_a",
        type: "ai",
        text: data.ai_response || "No response",
        timestamp: new Date().toLocaleTimeString(),
        audioUrl: data.audio_path ? `${BACKEND_URL}${data.audio_path}` : null,
      };

      setMessages((prev) => [...prev, userMessage, aiMessage]);
    } catch (err) {
      setError(err.message || "Voice processing failed");
    } finally {
      audioChunksRef.current = [];
      setLoading(false);
    }
  };

  // ------------------- UI -------------------
  return (
    <div className="max-w-xl mx-auto p-4">
      <h2 className="text-lg font-bold mb-3">🤖 AI ChatBot (Text + Voice)</h2>

      <div className="border rounded-lg p-3 h-96 overflow-y-auto bg-gray-50">
        {messages.length === 0 && (
          <p className="text-sm text-gray-500">No messages yet. Type or record to start.</p>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`mb-3 p-2 rounded-lg ${
              msg.type === "user" ? "bg-blue-100 text-right" : "bg-green-100 text-left"
            }`}
          >
            <p className="text-sm">{msg.text}</p>
            <p className="text-xs text-gray-500">{msg.timestamp}</p>

            {msg.type === "ai" && msg.audioUrl && (
              <div className="mt-2">
                <audio controls src={msg.audioUrl} />
              </div>
            )}
          </div>
        ))}

        {error && <div className="text-xs text-red-500 mt-2">⚠ {error}</div>}
        {loading && <div className="text-xs text-gray-600 mt-2">⏳ Processing...</div>}
      </div>

      {/* Input Controls */}
      <div className="flex items-center gap-2 mt-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
          className="flex-1 border px-2 py-1 rounded"
        />
        <button
          onClick={sendTextMessage}
          disabled={loading}
          className="bg-blue-500 text-white px-3 py-2 rounded"
        >
          Send
        </button>
      </div>

      {/* Voice Controls */}
      <div className="flex justify-center gap-3 mt-3">
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            🎙 Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="bg-red-600 text-white px-4 py-2 rounded"
          >
            ⏹ Stop
          </button>
        )}

        <button
          onClick={() => {
            setMessages([]);
            setError(null);
          }}
          className="bg-gray-300 px-3 py-2 rounded"
        >
          Clear
        </button>
      </div>
    </div>
  );
};

export default ChatBot;
