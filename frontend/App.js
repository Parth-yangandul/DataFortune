import { useState } from "react";
import VoiceInput from "./VoiceInput";
import ChatWindow from "./ChatWindow";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(localStorage.getItem("session_id") || null);
  const [mode, setMode] = useState("patient"); // "patient" or "admin"

  const addMessage = (from, text) => {
    setMessages((prev) => [...prev, { from, text }]);
  };

  const handleSend = async (text) => {
    addMessage("user", text);

    if (mode === "patient" && !sessionId) {
      const phone = prompt("Enter your phone for login:");
      const loginRes = await fetch(`http://127.0.0.1:8000/auth/patient-login?phone=${phone}`, { method: "POST" });
      const loginData = await loginRes.json();
      localStorage.setItem("session_id", loginData.session_id);
      setSessionId(loginData.session_id);
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/voice/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "session-id": sessionId || localStorage.getItem("session_id") || "",
        },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      addMessage("bot", data.answer);
    } catch (err) {
      addMessage("bot", "Error: Could not get response from server.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("session_id");
    setSessionId(null);
    setMessages([]);
    alert("Logged out!");
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-4">
      <h1 className="text-2xl font-bold mb-4">AI Voice Patient Portal</h1>

      {/* Mode Toggle */}
      <div className="mb-4">
        <button
          className={`px-4 py-2 rounded mr-2 ${mode === "patient" ? "bg-blue-500 text-white" : "bg-gray-300"}`}
          onClick={() => setMode("patient")}
        >
          Patient Mode
        </button>
        <button
          className={`px-4 py-2 rounded ${mode === "admin" ? "bg-green-500 text-white" : "bg-gray-300"}`}
          onClick={() => setMode("admin")}
        >
          Admin Mode
        </button>
      </div>

      <div className="w-full max-w-md flex flex-col space-y-2">
        <ChatWindow messages={messages} />
        <VoiceInput onSend={handleSend} />
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>
    </div>
  );
}