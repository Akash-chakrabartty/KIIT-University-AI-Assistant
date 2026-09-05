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
    if (loading || !question.trim()) return;

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
      {/* Background decoration */}
      <div className="background-glow glow-one"></div>
      <div className="background-glow glow-two"></div>
      <div className="background-grid"></div>

      <main className="chat-container">
        {/* ================= HEADER ================= */}
        <header className="top-header">
          <div className="brand">
            <div className="kiit-logo">
              <span>KIIT</span>
              <small>ESTD. 1992</small>
            </div>

            <div className="brand-text">
              <h1>Kalinga Institute of Industrial Technology</h1>
              <p>Deemed to be University | Bhubaneswar, India</p>
            </div>
          </div>

          <nav className="nav-menu">
            <button className="nav-item active">
              <span>⌂</span>
              Home
            </button>

            <button className="nav-item">
              <span>ⓘ</span>
              About
            </button>

            <button className="nav-item">
              <span>♙</span>
              Student Info
            </button>

            <button className="nav-item">
              <span>✦</span>
              AI Assistant
            </button>

            <button className="nav-item">
              <span>▤</span>
              Resources
            </button>

            <button className="icon-button">☼</button>
            <button className="profile-button">●</button>
          </nav>
        </header>

        {/* ================= HERO ================= */}
        <section className="hero">
          <div className="companion-badge">
            <span></span>
            Your Campus Companion
          </div>

          <div className="quote">
            “Learn Today, Lead Tomorrow”
            <small>— KIIT</small>
          </div>

          <h2>
            <span>KIIT</span> AI Assistant
          </h2>

          <p className="hero-description">
            Get instant answers about university information, regulations,
            exams, attendance, hostel rules, syllabus and more — all in one
            place.
          </p>

          {/* ================= INFO CARDS ================= */}
          <div className="info-cards">
            <div className="info-card">
              <div className="card-icon green">🎓</div>
              <h3>Academic Info</h3>
              <p>Syllabus, exams, regulations</p>
            </div>

            <div className="info-card">
              <div className="card-icon purple">▦</div>
              <h3>Campus Life</h3>
              <p>Hostel rules, facilities, clubs</p>
            </div>

            <div className="info-card">
              <div className="card-icon blue">▤</div>
              <h3>Quick Guidance</h3>
              <p>Get instant, accurate answers</p>
            </div>

            <div className="info-card">
              <div className="card-icon yellow">👥</div>
              <h3>Student Support</h3>
              <p>Always here to help</p>
            </div>
          </div>
        </section>

        {/* ================= QUESTION AREA ================= */}
        {!answer && (
          <section className="question-section">
            <h2>How can I help you today?</h2>

            <p>Type your question or choose a popular topic below</p>

            <div className="suggestions">
              <button
                onClick={() =>
                  handleSuggestion(
                    "What are the attendance requirements for BTech students?",
                  )
                }
              >
                <span>▣</span>
                Attendance Requirements
              </button>

              <button
                onClick={() =>
                  handleSuggestion("What are the hostel rules for students?")
                }
              >
                <span>▰</span>
                Hostel Rules
              </button>

              <button
                onClick={() =>
                  handleSuggestion("Tell me about the BTech examination rules.")
                }
              >
                <span>▤</span>
                Examination Rules
              </button>

              <button
                onClick={() =>
                  handleSuggestion("Tell me about the BTech syllabus.")
                }
              >
                <span>▥</span>
                Syllabus Info
              </button>
            </div>
          </section>
        )}

        {/* ================= ANSWER ================= */}
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

        {/* ================= ERROR ================= */}
        {error && <div className="error-box">{error}</div>}

        {/* ================= INPUT ================= */}
        <div className="input-area">
          <span className="input-icon">✦</span>

          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about KIIT..."
            rows="1"
            disabled={loading}
          />

          <span className="attachment-icon">♧</span>

          <button
            className="ask-button"
            onClick={askQuestion}
            disabled={loading || !question.trim()}
          >
            <span>{loading ? "..." : "➤"}</span>
            {loading ? "Thinking" : "Ask"}
          </button>
        </div>

        {/* ================= FOOTER ================= */}
        <footer className="footer">
          <div className="creator">
            <div className="creator-icon">A</div>

            <div>
              <small>Made by</small>
              <strong>Akash Chakrabartty</strong>
              <span>B.Tech CSE | KIIT University</span>
            </div>
          </div>

          <div className="footer-center">
            <strong>KIIT AI Assistant</strong>
            <span>•</span>
            <span>Kalinga Institute of Industrial Technology</span>
            <small>Deemed to be University, Bhubaneswar, India</small>
          </div>

          <div className="footer-right">
            <span>Built for Students</span>
            <span>•</span>
            <span>With AI for a Better Campus</span>
            <small>Knowledge | Innovation | Excellence</small>
          </div>
        </footer>
      </main>
    </div>
  );
}
