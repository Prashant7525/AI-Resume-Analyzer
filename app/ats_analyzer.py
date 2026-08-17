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
        suggestions.append(
            "Add relevant work experience or internships."
        )

    if not _has_content(resume.get("projects")):
        suggestions.append(
            "Add relevant projects that demonstrate your skills."
        )

    if not _has_content(resume.get("education")):
        suggestions.append("Add your educational background.")

    if not _has_content(resume.get("certifications")):
        suggestions.append(
            "Consider adding relevant certifications."
        )

    if not _has_content(resume.get("achievements")):
        suggestions.append(
            "Add measurable achievements or accomplishments."
        )

    return suggestions


def calculate_content_quality_score(resume: dict) -> dict:
    """
    Evaluate the quality signals of important resume sections.

    Maximum score: 50 points.

    Summary       10
    Skills        10
    Experience    10
    Projects      10
    Achievements  10
    """

    scores = {
        "summary": 0,
        "skills": 0,
        "experience": 0,
        "projects": 0,
        "achievements": 0,
    }

    summary = str(resume.get("summary", "")).strip()
    skills = str(resume.get("skills", "")).strip()
    experience = str(resume.get("experience", "")).strip()
    projects = str(resume.get("projects", "")).strip()
    achievements = str(resume.get("achievements", "")).strip()

    # Summary: 10 points
    if summary:
        scores["summary"] = 5

        if len(summary.split()) >= 20:
            scores["summary"] += 5

    # Skills: 10 points
    if skills:
        scores["skills"] = 5

        skill_items = [
            item.strip()
            for item in skills.replace("\n", ",").split(",")
            if item.strip()
        ]

        if len(skill_items) >= 5:
            scores["skills"] += 5

    # Experience: 10 points
    if experience:
        scores["experience"] = 5

        if len(experience.split()) >= 15:
            scores["experience"] += 5

    # Projects: 10 points
    if projects:
        scores["projects"] = 5

        if len(projects.split()) >= 15:
            scores["projects"] += 5

    # Achievements: 10 points
    if achievements:
        scores["achievements"] = 5

        # Numbers often indicate measurable achievements.
        if any(char.isdigit() for char in achievements):
            scores["achievements"] += 5

    total = sum(scores.values())

    return {
        "score": total,
        "max_score": 50,
        "breakdown": scores,
    }


def check_resume_structure(resume: dict) -> dict:
    """Check additional ATS-friendly structural signals."""

    contact = check_contact_information(resume)

    checks = {
        "has_name": _has_content(resume.get("name")),
        "has_contact": contact["passed"],
        "has_summary": _has_content(resume.get("summary")),
        "has_skills": _has_content(resume.get("skills")),
        "has_experience": _has_content(resume.get("experience")),
        "has_projects": _has_content(resume.get("projects")),
        "has_education": _has_content(resume.get("education")),
    }

    passed = sum(checks.values())

    return {
        **checks,
        "passed": passed,
        "total": len(checks),
    }


def calculate_ats_score(resume: dict) -> dict:
    """
    Calculate an overall ATS score out of 100.

    50 points come from resume completeness.
    50 points come from content quality.
    """

    completeness = calculate_completeness_score(resume)
    content_quality = calculate_content_quality_score(resume)

    completeness_points = round(
        (completeness / 90) * 50
    )

    quality_points = content_quality["score"]

    total_score = min(
        100,
        completeness_points + quality_points,
    )

    return {
        "score": total_score,
        "max_score": 100,
        "completeness": {
            "score": completeness,
            "max_score": 90,
            "weighted_score": completeness_points,
        },
        "content_quality": content_quality,
    }


def analyze_resume(resume: dict) -> dict:
    """Run the complete rule-based ATS analysis."""

    completeness_score = calculate_completeness_score(resume)
    contact = check_contact_information(resume)
    sections = check_required_sections(resume)
    suggestions = generate_suggestions(resume)
    content_quality = calculate_content_quality_score(resume)
    structure = check_resume_structure(resume)
    ats = calculate_ats_score(resume)

    return {
        # Kept for backwards compatibility with v1.2-v1.5.
        "score": completeness_score,

        # New v1.6 overall ATS score.
        "ats_score": ats,

        "contact": contact,
        "sections": sections,
        "structure": structure,
        "content_quality": content_quality,
        "suggestions": suggestions,
    }