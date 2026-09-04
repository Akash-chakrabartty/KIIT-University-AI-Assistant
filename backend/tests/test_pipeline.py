import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reasoning.pipeline import (
    build_evidence_text, verify_citations, answer, is_calculation_question
)
from reasoning.llm_provider import LLMProvider

EVIDENCE = [{
    "passage_id": "DOC001-P17-C03",
    "text": "Students may apply for a grade-improvement examination once per academic year...",
    "score": 0.91,
    "document_title": "Academic Regulation 2026",
    "page": 17,
    "section": "4.2",
    "academic_year": "2026-27",
    "url": "https://example.edu/regulation.pdf",
}]


class FakeProvider(LLMProvider):
    def __init__(self, text):
        self._text = text

    def generate(self, prompt: str) -> str:
        return self._text


def test_verify_citations_keeps_only_real_ids():
    raw = "Yes, per clause 4.2. (Passage ID: DOC001-P17-C03) (Passage ID: FAKE-999)"
    citations = verify_citations(raw, EVIDENCE)
    assert len(citations) == 1
    assert citations[0].passage_id == "DOC001-P17-C03"


def test_verify_citations_none_found():
    raw = "Yes, you are eligible."
    citations = verify_citations(raw, EVIDENCE)
    assert citations == []


def test_build_evidence_text_contains_passage_id():
    text = build_evidence_text(EVIDENCE)
    assert "DOC001-P17-C03" in text


def test_is_calculation_question():
    assert is_calculation_question("What is my SGPA this semester?")
    assert is_calculation_question("Am I eligible for a minor?")
    assert not is_calculation_question("Can I improve my CGPA?")


def test_answer_verified_status():
    provider = FakeProvider("Yes, under clause 4.2. (Passage ID: DOC001-P17-C03)")
    result = answer("Can I improve my CGPA?", provider, lambda q, top_k=5: EVIDENCE)
    assert result.status == "verified"
    assert len(result.citations) == 1
    assert result.confidence <= 0.95


def test_answer_cannot_verify_no_evidence():
    provider = FakeProvider("irrelevant")
    result = answer("Some obscure question", provider, lambda q, top_k=5: [])
    assert result.status == "cannot_verify"
    assert result.confidence == 0.0


def test_answer_sgpa_calculation_bypasses_llm():
    class ExplodingProvider(LLMProvider):
        def generate(self, prompt: str) -> str:
            raise AssertionError("LLM should never be called for SGPA calculation")

    result = answer(
        "What is my SGPA?", ExplodingProvider(), lambda q, top_k=5: EVIDENCE,
        user_context={"courses": [{"credits": 4, "grade_points": 8},
                                   {"credits": 3, "grade_points": 7}]},
    )
    assert result.status == "verified"
    assert "7.57" in result.answer


def test_answer_error_on_llm_exception():
    class BrokenProvider(LLMProvider):
        def generate(self, prompt: str) -> str:
            raise RuntimeError("API down")

    result = answer("Can I improve my CGPA?", BrokenProvider(), lambda q, top_k=5: EVIDENCE)
    assert result.status == "error"
    assert result.confidence == 0.0
