"""
Resume improvement and recommendation engine.

V3.0
- Resume section analysis
- Actionable recommendations
- Priority-based improvements
- Strength detection
- Personalized improvement guidance
- Backward-compatible V2.x analysis results
"""

from __future__ import annotations

import re
from typing import Any


# ============================================================
# SAFE TEXT HELPERS
# ============================================================


def _text(value: Any) -> str:
    """Convert a resume value into normalized text."""

    if value is None:
        return ""

    if isinstance(value, (list, tuple, set)):
        return " ".join(
            str(item)
            for item in value
        ).strip()

    return str(value).strip()


def _word_count(text: str) -> int:
    """Return the number of words in text."""

    if not text:
        return 0

    return len(
        re.findall(
            r"\b[\w+#.-]+\b",
            text,
        )
    )


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

        if re.match(
            r"^\s*[•●▪◦\-*]\s+",
            line,
        ):
            count += 1

    return count


# ============================================================
# V3.0 RECOMMENDATION HELPERS
# ============================================================


def _priority_for_status(status: str) -> str:
    """
    Return a recommendation priority for a section status.

    Priority levels:
        critical
        high
        medium
        low
    """

    if status in {
        "missing",
        "incomplete",
    }:
        return "critical"

    if status in {
        "too_short",
        "too_long",
        "no_metrics",
        "no_bullets",
        "limited",
    }:
        return "high"

    return "low"


def _section_label(section: str) -> str:
    """Return a human-readable section name."""

    labels = {
        "summary": "Professional Summary",
        "experience": "Work Experience",
        "projects": "Projects",
        "skills": "Skills",
        "achievements": "Achievements",
        "contact": "Contact Information",
    }

    return labels.get(
        section,
        section.replace(
            "_",
            " ",
        ).title(),
    )


def _build_priority_recommendation(
    section: str,
    result: dict,
) -> dict:
    """
    Build a structured V3.0 recommendation.
    """

    status = result.get(
        "status",
        "",
    )

    return {
        "section": section,
        "section_label": _section_label(
            section
        ),
        "status": status,
        "priority": _priority_for_status(
            status
        ),
        "recommendation": result.get(
            "recommendation",
            "",
        ),
    }


# ============================================================
# SECTION CHECKS
# ============================================================


def check_summary(resume: dict) -> dict:
    """Evaluate the professional summary."""

    summary = _text(
        resume.get("summary")
    )

    words = _word_count(
        summary
    )

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

    experience = _text(
        resume.get("experience")
    )

    words = _word_count(
        experience
    )

    bullets = _bullet_count(
        experience
    )

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

    projects = _text(
        resume.get("projects")
    )

    words = _word_count(
        projects
    )

    bullets = _bullet_count(
        projects
    )

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

    skills = _text(
        resume.get("skills")
    )

    if not skills:

        status = "missing"

        recommendation = (
            "Add a technical skills section containing "
            "relevant tools, languages, frameworks, and technologies."
        )

    elif (
        len(skills.split(",")) < 3
        and len(skills.split()) < 5
    ):

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

    achievements = _text(
        resume.get("achievements")
    )

    bullets = _bullet_count(
        achievements
    )

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

    if not _text(
        resume.get("name")
    ):
        missing.append("name")

    if not _text(
        resume.get("email")
    ):
        missing.append("email")

    if not _text(
        resume.get("phone")
    ):
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


# ============================================================
# CHECK COLLECTION
# ============================================================


def _run_checks(resume: dict) -> dict:
    """Run all resume section checks."""

    return {
        "summary": check_summary(
            resume
        ),
        "experience": check_experience(
            resume
        ),
        "projects": check_projects(
            resume
        ),
        "skills": check_skills(
            resume
        ),
        "achievements": check_achievements(
            resume
        ),
        "contact": check_contact_information(
            resume
        ),
    }


# ============================================================
# V2 COMPATIBILITY
# ============================================================


def generate_improvements(
    resume: dict,
) -> list[str]:
    """
    Generate prioritized actionable resume improvements.

    This preserves the V2.x public API.
    """

    checks = _run_checks(
        resume
    )

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

        result = checks[
            section
        ]

        if result["status"] not in {
            "good",
            "complete",
        }:

            improvements.append(
                result["recommendation"]
            )

    return improvements


# ============================================================
# V3.0 PRIORITY RECOMMENDATIONS
# ============================================================


def generate_priority_improvements(
    resume: dict,
) -> list[dict]:
    """
    Generate structured, prioritized V3.0 recommendations.

    Each recommendation contains:
        section
        section_label
        status
        priority
        recommendation
    """

    checks = _run_checks(
        resume
    )

    priority_order = [
        "contact",
        "summary",
        "experience",
        "skills",
        "projects",
        "achievements",
    ]

    recommendations = []

    for section in priority_order:

        result = checks[
            section
        ]

        if result["status"] in {
            "good",
            "complete",
        }:
            continue

        recommendations.append(
            _build_priority_recommendation(
                section,
                result,
            )
        )

    priority_rank = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    recommendations.sort(
        key=lambda item: (
            priority_rank.get(
                item["priority"],
                99,
            ),
            priority_order.index(
                item["section"]
            ),
        )
    )

    return recommendations


# ============================================================
# V3.0 STRENGTH DETECTION
# ============================================================


def generate_strengths(
    resume: dict,
) -> list[dict]:
    """
    Identify strong resume sections.

    Returns structured strength information.
    """

    checks = _run_checks(
        resume
    )

    strengths = []

    for section, result in checks.items():

        status = result.get(
            "status"
        )

        if status not in {
            "good",
            "complete",
        }:
            continue

        strengths.append(
            {
                "section": section,
                "section_label": _section_label(
                    section
                ),
                "status": status,
                "message": result.get(
                    "recommendation",
                    "",
                ),
            }
        )

    return strengths


# ============================================================
# V3.0 ACTIONABLE GUIDANCE
# ============================================================


def _action_for_recommendation(
    recommendation: dict,
) -> str:
    """
    Convert a recommendation into a concrete next action.
    """

    section = recommendation[
        "section"
    ]

    status = recommendation[
        "status"
    ]

    actions = {
        (
            "contact",
            "incomplete",
        ): (
            "Add your name, professional email address, "
            "and phone number at the top of the resume."
        ),
        (
            "summary",
            "missing",
        ): (
            "Write a 2–4 sentence summary that connects "
            "your target role, strongest skills, and experience."
        ),
        (
            "summary",
            "too_short",
        ): (
            "Add your experience level, strongest technical "
            "skills, and the type of role you are targeting."
        ),
        (
            "summary",
            "too_long",
        ): (
            "Remove generic statements and keep only details "
            "directly relevant to your target role."
        ),
        (
            "experience",
            "missing",
        ): (
            "Add internships, work experience, freelance work, "
            "or substantial practical experience."
        ),
        (
            "experience",
            "no_bullets",
        ): (
            "Convert long experience paragraphs into concise "
            "bullet points beginning with strong action verbs."
        ),
        (
            "experience",
            "no_metrics",
        ): (
            "Rewrite several bullets to include measurable "
            "outcomes, scale, impact, or performance improvements."
        ),
        (
            "skills",
            "missing",
        ): (
            "Add a clearly labeled skills section containing "
            "technologies you can demonstrate through your resume."
        ),
        (
            "skills",
            "limited",
        ): (
            "Add relevant languages, frameworks, databases, "
            "tools, and platforms that match your actual experience."
        ),
        (
            "projects",
            "missing",
        ): (
            "Add 1–3 relevant projects with your role, "
            "technologies used, and the problem you solved."
        ),
        (
            "projects",
            "no_bullets",
        ): (
            "Turn project descriptions into concise bullets "
            "covering implementation, technology, and outcomes."
        ),
        (
            "achievements",
            "missing",
        ): (
            "Add accomplishments that demonstrate impact, "
            "leadership, performance, or measurable results."
        ),
        (
            "achievements",
            "no_metrics",
        ): (
            "Quantify achievements using percentages, counts, "
            "rankings, time saved, scale, or other measurable outcomes."
        ),
        (
            "achievements",
            "no_bullets",
        ): (
            "Present achievements as concise bullet points "
            "so recruiters can scan them quickly."
        ),
    }

    return actions.get(
        (
            section,
            status,
        ),
        recommendation.get(
            "recommendation",
            "",
        ),
    )


def generate_action_plan(
    resume: dict,
) -> list[dict]:
    """
    Generate a practical action plan from V3.0 recommendations.
    """

    recommendations = generate_priority_improvements(
        resume
    )

    action_plan = []

    for number, recommendation in enumerate(
        recommendations,
        start=1,
    ):

        action_plan.append(
            {
                "number": number,
                "section": recommendation[
                    "section"
                ],
                "section_label": recommendation[
                    "section_label"
                ],
                "priority": recommendation[
                    "priority"
                ],
                "action": _action_for_recommendation(
                    recommendation
                ),
                "reason": recommendation[
                    "recommendation"
                ],
            }
        )

    return action_plan


# ============================================================
# COMPLETE V3.0 ANALYSIS
# ============================================================


def analyze_resume_improvements(
    resume: dict,
) -> dict:
    """
    Run the complete V3.0 actionable resume analysis.

    Existing V2.x result keys are preserved.
    """

    checks = _run_checks(
        resume
    )

    improvements = generate_improvements(
        resume
    )

    priority_improvements = (
        generate_priority_improvements(
            resume
        )
    )

    strengths = generate_strengths(
        resume
    )

    action_plan = generate_action_plan(
        resume
    )

    completed = 0

    for result in checks.values():

        status = result[
            "status"
        ]

        if status in {
            "good",
            "complete",
        }:

            completed += 1

    total = len(
        checks
    )

    score = (
        round(
            completed / total * 100
        )
        if total
        else 0
    )

    return {
        "score": score,
        "checks": checks,
        "improvements": improvements,
        "priority_improvements": priority_improvements,
        "strengths": strengths,
        "action_plan": action_plan,
        "completed": completed,
        "total": total,
    }