import json
import uuid
from fastapi import APIRouter, Request
from pydantic import BaseModel

from reasoning.pipeline import answer as run_answer
from reasoning.schemas import AnswerResponse
from knowledge.search import search as knowledge_search

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    conversation_id: str | None = None
    user_context: dict | None = None


class FeedbackRequest(BaseModel):
    conversation_id: str
    message_id: str
    rating: str
    comment: str | None = None


def _error_response(message: str) -> dict:
    return {"answer": message, "status": "error", "confidence": 0.0,
            "citations": [], "actions": [], "warnings": []}


@router.post("/chat")
def chat(req: ChatRequest, request: Request):
    conn = request.app.state.db

    if not req.question or len(req.question) > 2000:
        return _error_response("Question must be between 1 and 2000 characters.")

    conversation_id = req.conversation_id or str(uuid.uuid4())
    conn.execute(
        "INSERT OR IGNORE INTO conversations (id) VALUES (?)", (conversation_id,)
    )
    conn.execute(
        "INSERT INTO messages (id, conversation_id, role, text) VALUES (?, ?, 'user', ?)",
        (str(uuid.uuid4()), conversation_id, req.question),
    )

    def search_fn(q, top_k=5):
        return knowledge_search(conn, q, top_k=top_k)

    result: AnswerResponse = run_answer(
        req.question, request.app.state.llm_provider, search_fn, req.user_context
    )

    conn.execute(
        "INSERT INTO messages (id, conversation_id, role, text, response_json) VALUES (?, ?, 'assistant', ?, ?)",
        (result.message_id, conversation_id, result.answer, result.model_dump_json()),
    )
    conn.commit()

    return {**result.model_dump(), "conversation_id": conversation_id}


@router.post("/feedback")
def feedback(req: FeedbackRequest, request: Request):
    conn = request.app.state.db
    conn.execute(
        "INSERT INTO feedback (conversation_id, message_id, rating, comment) VALUES (?, ?, ?, ?)",
        (req.conversation_id, req.message_id, req.rating, req.comment),
    )
    conn.commit()
    return {"status": "ok"}


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, request: Request):
    conn = request.app.state.db
    rows = conn.execute(
        "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at",
        (conversation_id,),
    ).fetchall()
    return [dict(r) for r in rows]


@router.get("/admin/summary")
def admin_summary(request: Request):
    conn = request.app.state.db
    rows = conn.execute(
        "SELECT response_json FROM messages WHERE role = 'assistant' AND response_json IS NOT NULL"
    ).fetchall()
    total = len(rows)
    cannot_verify = 0
    for r in rows:
        try:
            if json.loads(r["response_json"])["status"] == "cannot_verify":
                cannot_verify += 1
        except (TypeError, KeyError, json.JSONDecodeError):
            continue
    fb = conn.execute(
        "SELECT rating, COUNT(*) as c FROM feedback GROUP BY rating"
    ).fetchall()
    fb_counts = {r["rating"]: r["c"] for r in fb}
    return {
        "questions_total": total,
        "cannot_verify": cannot_verify,
        "helpful": fb_counts.get("helpful", 0),
        "not_helpful": fb_counts.get("not_helpful", 0),
    }
