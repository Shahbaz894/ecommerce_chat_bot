// components/VoiceChat.jsx
"use client";

import React, { useState, useRef } from "react";

const VoiceChat = () => {
  const [messages, setMessages] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Generate session ID
  const [sessionId] = useState(() => {
    if (window.crypto?.randomUUID) return crypto.randomUUID();
    return "session_" + Math.random().toString(36).slice(2, 9);
  });

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

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

      mediaRecorder.onstop = () => {
        handleSendAudio();
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Mic error:", err);
      setError("Microphone access failed. Please allow mic permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((t) => t.stop());
    }
    setIsRecording(false);
  };

  const handleSendAudio = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!audioChunksRef.current.length) {
        setError("No audio recorded.");
        setLoading(false);
        return;
      }

      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("file", audioBlob, "voice.webm");

      const endpoint = `http://localhost:8000/api/voice/chat?session_id=${sessionId}`;
      const res = await fetch(endpoint, { method: "POST", body: formData });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      const data = await res.json();

      // Add user message
      const userMessage = {
        id: Date.now() + "_u",
        type: "user",
        text: data.user_query || "You (voice)",
        timestamp: new Date().toLocaleTimeString(),
      };

      // Add AI message
      const aiMessage = {
        id: Date.now() + "_a",
        type: "ai",
        text: data.ai_response || "No response",
        timestamp: new Date().toLocaleTimeString(),
        audioUrl: data.audio_path ? `http://localhost:8000${data.audio_path}` : null,
      };

      setMessages((prev) => [...prev, userMessage, aiMessage]);
    } catch (err) {
      console.error("Voice chat error:", err);
      setError(err.message || "Voice processing failed");
    } finally {
      setLoading(false);
      audioChunksRef.current = [];
    }
  };

  return (
    <div className="max-w-xl mx-auto p-4">
      <h2 className="text-lg font-bold mb-3">🎤 Voice ChatBot</h2>

      <div className="border rounded-lg p-3 h-96 overflow-y-auto bg-gray-50">
        {messages.length === 0 && (
          <p className="text-sm text-gray-500">No messages yet. Click the mic to start.</p>
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
        {loading && <div className="text-xs text-gray-600 mt-2">Processing voice...</div>}
      </div>

      <div className="flex justify-center mt-4 gap-3">
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={loading}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg"
          >
            🎙 Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="bg-red-500 text-white px-4 py-2 rounded-lg"
          >
            ⏹ Stop Recording
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

export default VoiceChat;
