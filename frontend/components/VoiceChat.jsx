"use client";
import React, { useState, useRef } from "react";

const BACKEND_URL = "http://localhost:8000";

export default function VoiceChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [sessionId] = useState(() =>
    crypto.randomUUID ? crypto.randomUUID() : "session_" + Math.random().toString(36).substring(2, 9)
  );

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // ---------------- TEXT CHAT ----------------
  const sendTextMessage = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${BACKEND_URL}/api/ask_product?query=${encodeURIComponent(input)}&session_id=${sessionId}`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { id: Date.now() + "_u", type: "user", text: input, timestamp: new Date().toLocaleTimeString() },
        { id: Date.now() + "_a", type: "ai", text: data.answer, timestamp: new Date().toLocaleTimeString() },
      ]);
      setInput("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ---------------- VOICE CHAT ----------------
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

      setMessages((prev) => [
        ...prev,
        { id: Date.now() + "_u", type: "user", text: data.user_query || "🎤 (voice input)", timestamp: new Date().toLocaleTimeString() },
        { id: Date.now() + "_a", type: "ai", text: data.ai_response, timestamp: new Date().toLocaleTimeString(), audioUrl: `${BACKEND_URL}${data.audio_path}` },
      ]);
    } catch (err) {
      setError(err.message || "Voice processing failed");
    } finally {
      setLoading(false);
      audioChunksRef.current = [];
    }
  };

  // ---------------- UI ----------------
  return (
    <div className="max-w-xl mx-auto p-4 font-sans">
      <h2 className="text-2xl font-bold mb-4 text-center">🤖 Ecomerce ChatBot </h2>

      <div className="border rounded-lg p-3 h-96 overflow-y-auto bg-gray-100 shadow-inner">
        {messages.length === 0 && (
          <p className="text-sm text-gray-500 text-center mt-8">
            No messages yet. Type or record to start.
          </p>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`mb-3 p-2 rounded-lg ${
              msg.type === "user" ? "bg-blue-200 text-right ml-auto max-w-[80%]" : "bg-green-200 text-left mr-auto max-w-[80%]"
            }`}
          >
            <p className="text-sm whitespace-pre-line">{msg.text}</p>
            <p className="text-xs text-gray-600 mt-1">{msg.timestamp}</p>

            {msg.type === "ai" && msg.audioUrl && (
              <div className="mt-2">
                <audio controls src={msg.audioUrl} className="w-full" />
              </div>
            )}
          </div>
        ))}

        {error && <p className="text-red-500 text-xs mt-2">⚠ {error}</p>}
        {loading && <p className="text-gray-600 text-xs mt-2">⏳ Processing...</p>}
      </div>

      <div className="flex gap-2 mt-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
          className="flex-1 border px-3 py-2 rounded shadow-sm"
        />
        <button
          onClick={sendTextMessage}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow"
        >
          Send
        </button>
      </div>

      <div className="flex justify-center gap-3 mt-3">
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={loading}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded shadow"
          >
            🎙 Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="bg-gray-700 text-white px-4 py-2 rounded shadow"
          >
            ⏹ Stop
          </button>
        )}

        <button
          onClick={() => {
            setMessages([]);
            setError(null);
          }}
          className="bg-gray-300 hover:bg-gray-400 text-black px-4 py-2 rounded shadow"
        >
          Clear
        </button>
      </div>
    </div>
  );
}
