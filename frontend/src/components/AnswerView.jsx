import React from "react";
import CitationCard from "./CitationCard";
import ActionChecklist from "./ActionChecklist";

export default function AnswerView({ answer }) {
  switch (answer.status) {
    case "verified":
    case "partially_verified":
      return (
        <div style={{ marginTop: 16 }}>
          <p>{answer.answer}</p>
          {answer.status === "partially_verified" &&
            answer.warnings.map((w, i) => (
              <div
                key={i}
                style={{ background: "#fff3cd", padding: 8, borderRadius: 4 }}
              >
                {w}
              </div>
            ))}
          {answer.citations.map((c) => (
            <CitationCard key={c.passage_id} citation={c} />
          ))}
          {answer.actions.length > 0 && (
            <ActionChecklist actions={answer.actions} />
          )}
        </div>
      );
    case "cannot_verify":
      return (
        <p style={{ marginTop: 16, fontStyle: "italic" }}>
          I could not verify this from the available information.
        </p>
      );
    case "needs_clarification":
      return <p style={{ marginTop: 16 }}>{answer.answer}</p>;
    case "error":
    default:
      return (
        <p style={{ marginTop: 16, color: "red" }}>
          This assistant is temporarily unavailable. Please try again shortly.
        </p>
      );
  }
}
