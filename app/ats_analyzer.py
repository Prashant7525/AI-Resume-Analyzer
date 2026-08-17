from typing import Any


SECTION_WEIGHTS = {
    "summary": 10,
    "skills": 20,
    "experience": 20,
    "projects": 15,
    "education": 15,
    "certifications": 5,
    "achievements": 5,
}


def _has_content(value: Any) -> bool:
    """Return True when a resume field contains meaningful content."""
    if value is None:
        return False

    if isinstance(value, (list, tuple, set)):
        return any(str(item).strip() for item in value)

    return bool(str(value).strip())


def calculate_completeness_score(resume: dict) -> int:
    """Calculate a score based on the presence of important resume sections."""

    score = 0

    for section, weight in SECTION_WEIGHTS.items():
        if _has_content(resume.get(section)):
            score += weight

    return score


def check_contact_information(resume: dict) -> dict:
    """Check whether basic contact information is available."""

    email_found = _has_content(resume.get("email"))
    phone_found = _has_content(resume.get("phone"))

    return {
        "email": email_found,
        "phone": phone_found,
        "passed": email_found and phone_found,
    }


def check_required_sections(resume: dict) -> dict:
    """Check the presence of core resume sections."""

    sections = {
        "summary": _has_content(resume.get("summary")),
        "skills": _has_content(resume.get("skills")),
        "education": _has_content(resume.get("education")),
        "projects": _has_content(resume.get("projects")),
        "experience": _has_content(resume.get("experience")),
    }

    return sections


def generate_suggestions(resume: dict) -> list[str]:
    """Generate deterministic suggestions from missing resume information."""

    suggestions = []

    if not _has_content(resume.get("name")):
        suggestions.append("Add your full name.")

    if not _has_content(resume.get("email")):
        suggestions.append("Add a professional email address.")

    if not _has_content(resume.get("phone")):
        suggestions.append("Add a phone number.")

    if not _has_content(resume.get("summary")):
        suggestions.append("Add a concise professional summary.")

    if not _has_content(resume.get("skills")):
        suggestions.append("Add a technical skills section.")

    if not _has_content(resume.get("experience")):
        suggestions.append("Add relevant work experience or internships.")

    if not _has_content(resume.get("projects")):
        suggestions.append("Add relevant projects that demonstrate your skills.")

    if not _has_content(resume.get("education")):
        suggestions.append("Add your educational background.")

    if not _has_content(resume.get("certifications")):
        suggestions.append("Consider adding relevant certifications.")

    if not _has_content(resume.get("achievements")):
        suggestions.append("Add measurable achievements or accomplishments.")

    return suggestions


def analyze_resume(resume: dict) -> dict:
    """Run the complete rule-based ATS analysis."""

    completeness_score = calculate_completeness_score(resume)
    contact = check_contact_information(resume)
    sections = check_required_sections(resume)
    suggestions = generate_suggestions(resume)

    return {
        "score": completeness_score,
        "contact": contact,
        "sections": sections,
        "suggestions": suggestions,
    }