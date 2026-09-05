"""Project responsibility: retrieved evidence -> grounded, verified answer."""

from reasoning.schemas import AnswerResponse, Citation, new_message_id
from reasoning.rules import calculate_sgpa, check_eligibility
from reasoning.llm_provider import LLMProvider


DEFAULT_ELIGIBILITY_RULE = {
    "min_cgpa": 6.0,
    "max_backlogs": 2,
}


def is_calculation_question(question: str) -> bool:
    q = question.lower()

    return (
        "sgpa" in q
        or "eligib" in q
        or "cgpa improve" in q
    )


def build_evidence_text(results: list[dict]) -> str:
    blocks = []

    for i, r in enumerate(results, start=1):
        blocks.append(
            f"[SOURCE {i}]\n"
            f"Document: {r.get('document_title', 'Unknown')}\n"
            f"Page: {r.get('page', 'N/A')}\n"
            f"Section: {r.get('section') or 'N/A'}\n"
            f"Passage ID: {r.get('passage_id', 'N/A')}\n"
            f"Text: {r.get('text', '')}"
        )

    return "\n\n".join(blocks)


def build_prompt(question: str, evidence_text: str) -> str:
    return f"""
You are a university information assistant.

Answer the user's question using ONLY the evidence provided below.

Rules:
1. Do not invent facts.
2. Do not use outside knowledge.
3. If the evidence does not contain enough information, clearly say that
   you could not verify the answer.
4. Keep the answer clear and useful for a university student.
5. For every factual claim, mention the relevant Passage ID in this format:
   (Passage ID: XXXX)

EVIDENCE:
{evidence_text}

QUESTION:
{question}

ANSWER:
""".strip()


def verify_citations(
    raw_text: str,
    evidence: list[dict],
) -> list[Citation]:
    """
    Only accepts Passage IDs that actually exist in the retrieved evidence.
    Model-generated fake Passage IDs are ignored.
    """

    found: list[Citation] = []
    seen = set()

    for r in evidence:
        passage_id = r.get("passage_id")

        if not passage_id:
            continue

        if passage_id in raw_text and passage_id not in seen:
            seen.add(passage_id)

            found.append(
                Citation(
                    passage_id=passage_id,
                    document_title=r.get("document_title", "Unknown"),
                    page=r.get("page", "N/A"),
                    section=r.get("section"),
                    academic_year=r.get("academic_year"),
                    url=r.get("url"),
                )
            )

    return found


def _confidence_for(
    status: str,
    top_score: float | None,
) -> float:
    if top_score is None:
        return 0.0

    try:
        score = float(top_score)
    except (TypeError, ValueError):
        return 0.0

    if status == "verified":
        return min(score, 0.95)

    if status == "partially_verified":
        return round(score * 0.7, 4)

    return 0.0


def answer(
    question: str,
    provider: LLMProvider,
    search_fn,
    user_context: dict | None = None,
    top_k: int = 5,
) -> AnswerResponse:

    user_context = user_context or {}

    # ---------------------------------------------------------
    # 1. Handle deterministic calculation questions
    # ---------------------------------------------------------

    if is_calculation_question(question) and "courses" in user_context:

        try:
            sgpa = calculate_sgpa(user_context["courses"])
        except Exception as e:
            print("SGPA calculation error:", repr(e))

            return AnswerResponse(
                message_id=new_message_id(),
                answer="I could not calculate the SGPA because the course data is invalid.",
                status="error",
                confidence=0.0,
            )

        if sgpa is None:
            return AnswerResponse(
                message_id=new_message_id(),
                answer="I couldn't compute an SGPA from the course data provided.",
                status="cannot_verify",
                confidence=0.0,
            )

        text = f"Your calculated SGPA is {sgpa}."

        if "cgpa" in user_context and "backlogs" in user_context:
            try:
                eligible = check_eligibility(
                    user_context["cgpa"],
                    user_context["backlogs"],
                    DEFAULT_ELIGIBILITY_RULE,
                )

                text += (
                    " Based on your CGPA and backlog count, "
                    f"you are {'eligible' if eligible else 'not eligible'} "
                    "for grade-improvement registration."
                )

            except Exception as e:
                print("Eligibility calculation error:", repr(e))

        return AnswerResponse(
            message_id=new_message_id(),
            answer=text,
            status="verified",
            confidence=0.95,
        )

    # ---------------------------------------------------------
    # 2. Retrieve relevant university evidence
    # ---------------------------------------------------------

    try:
        evidence = search_fn(
            question,
            top_k=top_k,
        )

    except Exception as e:
        print("Knowledge search error:", repr(e))

        return AnswerResponse(
            message_id=new_message_id(),
            answer=(
                "Something went wrong while searching the university "
                "knowledge base."
            ),
            status="error",
            confidence=0.0,
        )

    # ---------------------------------------------------------
    # 3. No evidence found
    # ---------------------------------------------------------

    if not evidence:
        return AnswerResponse(
            message_id=new_message_id(),
            answer=(
                "I could not verify this from the available "
                "university information."
            ),
            status="cannot_verify",
            confidence=0.0,
            citations=[],
            actions=[],
            warnings=[],
        )

    # ---------------------------------------------------------
    # 4. Build grounded LLM prompt
    # ---------------------------------------------------------

    evidence_text = build_evidence_text(evidence)

    prompt = build_prompt(
        question,
        evidence_text,
    )

    # ---------------------------------------------------------
    # 5. Generate answer using LLM provider
    # ---------------------------------------------------------

    try:
        raw_text = provider.generate(prompt)

        if not raw_text:
            raise RuntimeError(
                "LLM provider returned an empty response."
            )

        raw_text = str(raw_text).strip()

    except Exception as e:
        # IMPORTANT:
        # Print the real Gemini/provider error in the backend terminal.
        # This will help us identify the actual problem.
        print("=" * 70)
        print("LLM PROVIDER ERROR")
        print(repr(e))
        print("=" * 70)

        return AnswerResponse(
            message_id=new_message_id(),
            answer=(
                "The AI provider could not generate a response. "
                "Please check the backend terminal for the exact error."
            ),
            status="error",
            confidence=0.0,
            citations=[],
            actions=[],
            warnings=[
                "LLM provider generation failed."
            ],
        )

    # ---------------------------------------------------------
    # 6. Verify citations
    # ---------------------------------------------------------

    citations = verify_citations(
        raw_text,
        evidence,
    )

    # ---------------------------------------------------------
    # 7. Determine confidence/status
    # ---------------------------------------------------------

    top_score = None

    if evidence:
        try:
            top_score = float(
                evidence[0].get("score", 0.0)
            )
        except (TypeError, ValueError):
            top_score = 0.0

    if citations:
        status = "verified"

    elif top_score is not None and top_score > 0.3:
        status = "partially_verified"

    else:
        status = "cannot_verify"

    # ---------------------------------------------------------
    # 8. Add warnings
    # ---------------------------------------------------------

    warnings = []

    if status == "partially_verified":
        warnings.append(
            "This answer could not be fully verified against "
            "a specific passage."
        )

    if status == "cannot_verify":
        warnings.append(
            "The available evidence was not strong enough "
            "to fully verify this answer."
        )

    # ---------------------------------------------------------
    # 9. Return final structured response
    # ---------------------------------------------------------

    return AnswerResponse(
        message_id=new_message_id(),
        answer=raw_text,
        status=status,
        confidence=_confidence_for(
            status,
            top_score,
        ),
        citations=citations,
        actions=[],
        warnings=warnings,
    )