import { useState, useEffect } from "react";

export default function VoiceInput({ onSend }) {
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState("");

  useEffect(() => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Speech Recognition not supported in this browser.");
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          setTranscript(result);
          onSend(result); // send to backend
        } else {
          interim += result;
        }
      }
    };

    recognition.onend = () => setListening(false);

    if (listening) recognition.start();
    else recognition.stop();

    return () => recognition.abort();
  }, [listening]);

  return (
    <div className="flex flex-col items-center p-2">
      <button
        className={`px-4 py-2 rounded ${listening ? "bg-red-500" : "bg-green-500"} text-white`}
        onClick={() => setListening(!listening)}
      >
        {listening ? "Stop Listening" : "Start Talking"}
      </button>
      <p className="mt-2 text-gray-700">{transcript}</p>
    </div>
  );
}