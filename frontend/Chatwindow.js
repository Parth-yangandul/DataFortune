export default function ChatWindow({ messages }) {
    return (
      <div className="h-96 overflow-y-auto border p-2 rounded bg-white">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`my-1 flex ${msg.from === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`inline-block p-2 rounded max-w-xs ${
                msg.from === "user" ? "bg-blue-200" : "bg-gray-200"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>
    );
  }