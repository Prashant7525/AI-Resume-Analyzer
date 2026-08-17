import re
from typing import Any


def _text(value: Any) -> str:
    """Convert a resume value into normalized text."""

    if value is None:
        return ""

    if isinstance(value, (list, tuple, set)):
        return " ".join(str(item) for item in value).strip()

    return str(value).strip()


def _word_count(text: str) -> int:
    """Return the number of words in text."""

    if not text:
        return 0

    return len(re.findall(r"\b[\w+#.-]+\b", text))


def _has_numbers(text: str) -> bool:
    """Return True when text contains measurable numeric information."""

    return bool(
        re.search(
            r"\b\d+(?:\.\d+)?\s*(?:%|percent|x|k|m|b)?\b",
            text,
            re.IGNORECASE,
        )
    )


def _bullet_count(text: str) -> int:
    """Count common bullet-point lines."""

    if not text:
        return 0

    count = 0

    for line in text.splitlines():
        if re.match(r"^\s*[•●▪◦\-*]\s+", line):
            count += 1

    return count


def check_summary(resume: dict) -> dict:
    """Evaluate the professional summary."""

    summary = _text(resume.get("summary"))
    words = _word_count(summary)

    if not summary:
        status = "missing"
        recommendation = (
            "Add a concise professional summary describing "
            "your role, strongest skills, and career focus."
        )

    elif words < 20:
        status = "too_short"
        recommendation = (
            "Expand your professional summary to briefly explain "
            "your experience, key skills, and career focus."
        )

    elif words > 100:
        status = "too_long"
        recommendation = (
            "Shorten your professional summary and keep only the "
            "most relevant information."
        )

    else:
        status = "good"
        recommendation = (
            "Your professional summary has a reasonable length."
        )

    return {
        "status": status,
        "word_count": words,
        "recommendation": recommendation,
    }


def check_experience(resume: dict) -> dict:
    """Evaluate work experience content."""

    experience = _text(resume.get("experience"))
    words = _word_count(experience)
    bullets = _bullet_count(experience)

    if not experience:
        status = "missing"
        recommendation = (
            "Add relevant work experience, internships, or "
            "practical experience."
        )

    elif bullets == 0:
        status = "no_bullets"
        recommendation = (
            "Use bullet points to describe responsibilities, "
            "technologies, and results in your experience."
        )

    elif not _has_numbers(experience):
        status = "no_metrics"
        recommendation = (
            "Add measurable results such as percentages, "
            "time saved, users supported, or projects completed."
        )

    else:
        status = "good"
        recommendation = (
            "Your experience includes structured bullet points "
            "and measurable information."
        )

    return {
        "status": status,
        "word_count": words,
        "bullet_count": bullets,
        "recommendation": recommendation,
    }


def check_projects(resume: dict) -> dict:
    """Evaluate project descriptions."""

    projects = _text(resume.get("projects"))
    words = _word_count(projects)
    bullets = _bullet_count(projects)

    if not projects:
        status = "missing"
        recommendation = (
            "Add relevant projects that demonstrate your "
            "technical and problem-solving skills."
        )

    elif bullets == 0:
        status = "no_bullets"
        recommendation = (
            "Describe projects using bullet points and mention "
            "your role, technologies, and results."
        )

    else:
        status = "good"
        recommendation = (
            "Your projects use a structured format."
        )

    return {
        "status": status,
        "word_count": words,
        "bullet_count": bullets,
        "recommendation": recommendation,
    }


def check_skills(resume: dict) -> dict:
    """Evaluate the skills section."""

    skills = _text(resume.get("skills"))

    if not skills:
        status = "missing"
        recommendation = (
            "Add a technical skills section containing "
            "relevant tools, languages, frameworks, and technologies."
        )

    elif len(skills.split(",")) < 3 and len(skills.split()) < 5:
        status = "limited"
        recommendation = (
            "Expand your skills section with relevant technologies "
            "that are supported by your actual experience."
        )

    else:
        status = "good"
        recommendation = (
            "Your skills section contains a reasonable amount "
            "of information."
        )

    return {
        "status": status,
        "recommendation": recommendation,
    }


def check_achievements(resume: dict) -> dict:
    """Evaluate achievement descriptions."""

    achievements = _text(resume.get("achievements"))
    bullets = _bullet_count(achievements)

    if not achievements:
        status = "missing"
        recommendation = (
            "Add achievements that demonstrate measurable "
            "results or accomplishments."
        )

    elif not _has_numbers(achievements):
        status = "no_metrics"
        recommendation = (
            "Strengthen achievements with measurable results "
            "such as percentages, counts, rankings, or time saved."
        )

    elif bullets == 0:
        status = "no_bullets"
        recommendation = (
            "Use bullet points to make achievements easier to scan."
        )

    else:
        status = "good"
        recommendation = (
            "Your achievements contain measurable information "
            "and use a structured format."
        )

    return {
        "status": status,
        "bullet_count": bullets,
        "recommendation": recommendation,
    }


def check_contact_information(resume: dict) -> dict:
    """Evaluate basic contact information."""

    missing = []

    if not _text(resume.get("name")):
        missing.append("name")

    if not _text(resume.get("email")):
        missing.append("email")

    if not _text(resume.get("phone")):
        missing.append("phone")

    if missing:
        status = "incomplete"
        recommendation = (
            "Complete your contact information: "
            + ", ".join(missing)
            + "."
        )
    else:
        status = "complete"
        recommendation = (
            "Your basic contact information is complete."
        )

    return {
        "status": status,
        "missing": missing,
        "recommendation": recommendation,
    }


def generate_improvements(resume: dict) -> list[str]:
    """Generate prioritized actionable resume improvements."""

    checks = {
        "summary": check_summary(resume),
        "experience": check_experience(resume),
        "projects": check_projects(resume),
        "skills": check_skills(resume),
        "achievements": check_achievements(resume),
        "contact": check_contact_information(resume),
    }

    improvements = []

    priority_order = [
        "contact",
        "summary",
        "experience",
        "skills",
        "projects",
        "achievements",
    ]

    for section in priority_order:
        result = checks[section]

        if result["status"] != "good" and result["status"] != "complete":
            improvements.append(
                result["recommendation"]
            )

    return improvements


def analyze_resume_improvements(resume: dict) -> dict:
    """Run the complete actionable resume improvement analysis."""

    checks = {
        "summary": check_summary(resume),
        "experience": check_experience(resume),
        "projects": check_projects(resume),
        "skills": check_skills(resume),
        "achievements": check_achievements(resume),
        "contact": check_contact_information(resume),
    }

    improvements = generate_improvements(resume)

    completed = 0

    for result in checks.values():
        status = result["status"]

        if status in {"good", "complete"}:
            completed += 1

    total = len(checks)

    score = round(
        completed / total * 100
    ) if total else 0

    return {
        "score": score,
        "checks": checks,
        "improvements": improvements,
        "completed": completed,
        "total": total,
    }