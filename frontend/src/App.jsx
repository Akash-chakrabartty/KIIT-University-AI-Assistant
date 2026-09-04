import React, { useState } from "react";
import AnswerView from "./components/AnswerView";
import FeedbackButtons from "./components/FeedbackButtons";
import "./styles/App.css";

const API_BASE = "http://localhost:8080/api";

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [error, setError] = useState(null);

  async function askQuestion() {
    if (loading || !question.trim()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
          conversation_id: conversationId,
          user_context: {
            role: "student",
            program: "BTech",
          },
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();

      console.log("CHAT RESPONSE:", data);

      setAnswer(data);
      setConversationId(data.conversation_id);
      setQuestion("");
    } catch (e) {
      console.error("Chat error:", e);

      setError(
        "Backend connection failed. Please make sure the backend server is running.",
      );
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  }

  function handleSuggestion(text) {
    setQuestion(text);
  }

  return (
    <div className="app">
      <div className="background-glow glow-one"></div>
      <div className="background-glow glow-two"></div>

      <main className="chat-container">
        <header className="header">
          <div className="logo">K</div>

          <div>
            <h1>KIIT AI Assistant</h1>
            <p>University information, regulations & student help</p>
          </div>

          <div className="status">
            <span></span>
            AI Assistant
          </div>
        </header>

        <section className="welcome">
          <div className="welcome-icon">✦</div>

          <h2>How can I help you?</h2>

          <p>
            Ask questions about KIIT regulations, exams, attendance, hostel
            rules, syllabus and more.
          </p>

          <div className="suggestions">
            <button
              onClick={() =>
                handleSuggestion(
                  "What are the attendance requirements for BTech students?",
                )
              }
            >
              Attendance requirements
            </button>

            <button
              onClick={() =>
                handleSuggestion("What are the hostel rules for students?")
              }
            >
              Hostel rules
            </button>

            <button
              onClick={() =>
                handleSuggestion("Tell me about the BTech examination rules.")
              }
            >
              Examination rules
            </button>
          </div>
        </section>

        {answer && (
          <section className="answer-section">
            <AnswerView answer={answer} />

            {answer.message_id && conversationId && (
              <FeedbackButtons
                conversationId={conversationId}
                messageId={answer.message_id}
                apiBase={API_BASE}
              />
            )}
          </section>
        )}

        {error && <div className="error-box">{error}</div>}

        <div className="input-area">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about KIIT..."
            rows="1"
            disabled={loading}
          />

          <button
            className="ask-button"
            onClick={askQuestion}
            disabled={loading || !question.trim()}
          >
            {loading ? "..." : "Ask"}
          </button>
        </div>

        <p className="footer-text">
          KIIT University AI Assistant • Ask questions based on university
          knowledge
        </p>
      </main>
    </div>
  );
}
