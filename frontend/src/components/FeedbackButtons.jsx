import React, { useState } from "react";

export default function FeedbackButtons({
  conversationId,
  messageId,
  apiBase,
}) {
  const [sent, setSent] = useState(null);

  async function send(rating) {
    await fetch(`${apiBase}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: conversationId,
        message_id: messageId,
        rating,
      }),
    });
    setSent(rating);
  }

  if (sent) return <p style={{ marginTop: 8 }}>Thanks for your feedback!</p>;

  return (
    <div style={{ marginTop: 8 }}>
      <button onClick={() => send("helpful")}>Helpful</button>{" "}
      <button onClick={() => send("not_helpful")}>Not helpful</button>
    </div>
  );
}
