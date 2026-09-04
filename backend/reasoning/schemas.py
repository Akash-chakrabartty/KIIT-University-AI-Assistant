import uuid
from typing import Literal, Optional
from pydantic import BaseModel


class Citation(BaseModel):
    passage_id: str
    document_title: str
    page: int
    section: Optional[str] = None
    academic_year: Optional[str] = None
    url: Optional[str] = None


class Action(BaseModel):
    step: int
    title: str
    completed: bool = False
    url: Optional[str] = None


class AnswerResponse(BaseModel):
    message_id: str
    answer: str
    status: Literal["verified", "partially_verified", "cannot_verify",
                     "needs_clarification", "error"]
    confidence: float
    citations: list[Citation] = []
    actions: list[Action] = []
    warnings: list[str] = []


def new_message_id() -> str:
    return f"MSG-{uuid.uuid4().hex[:8]}"
