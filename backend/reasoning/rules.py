"""Member 2 responsibility: deterministic calculations. The LLM never
performs these computations -- it only ever reports a number this module
computed."""


def calculate_sgpa(courses: list[dict]) -> float | None:
    """courses: [{"credits": int, "grade_points": int}, ...].
    Returns None for an empty list (no defined SGPA) rather than
    raising or silently returning 0."""
    if not courses:
        return None
    total_credits = sum(c["credits"] for c in courses)
    if total_credits == 0:
        return None
    weighted = sum(c["credits"] * c["grade_points"] for c in courses)
    return round(weighted / total_credits, 2)


def check_eligibility(cgpa: float, backlogs: int, rule: dict) -> bool:
    """rule: {"min_cgpa": float, "max_backlogs": int}"""
    return cgpa >= rule["min_cgpa"] and backlogs <= rule["max_backlogs"]
