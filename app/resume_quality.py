"""
Resume quality analysis engine.

V3.2
- Resume length analysis
- Section analysis
- Bullet usage analysis
- Achievement analysis
- Contact analysis
- Structure analysis
- Quality scoring
- Quality suggestions
- Section intelligence
"""

from __future__ import annotations

import re
from typing import Any

from app.section_intelligence import (
    analyze_section_intelligence,
)


# ============================================================
# QUALITY CONFIGURATION
# ============================================================

QUALITY_WEIGHTS = {
    "length": 15,
    "sections": 15,
    "bullets": 10,
    "achievements": 10,
    "contact": 10,
    "structure": 10,
}

MAX_SCORE = sum(
    QUALITY_WEIGHTS.values()
)


# ============================================================
# SAFE TEXT HELPERS
# ============================================================

def _text(
    value: Any,
) -> str:
    """Convert a resume value into normalized text."""

    if value is None:

        return ""

    if isinstance(
        value,
        (list, tuple, set),
    ):

        return " ".join(
            str(item)
            for item in value
        ).strip()

    return str(value).strip()


def count_words(
    text: str,
) -> int:
    """Count words in a piece of text."""

    if not text:

        return 0

    return len(
        re.findall(
            r"\b[\w+#.-]+\b",
            text,
        )
    )


def count_bullets(
    text: str,
) -> int:
    """Count common bullet-point lines."""

    if not text:

        return 0

    count = 0

    for line in text.splitlines():

        stripped = line.strip()

        if re.match(
            r"^[•●▪◦\-*]\s+",
            stripped,
        ):

            count += 1

    return count


def count_quantifiable_achievements(
    text: str,
) -> int:
    """
    Count achievement lines containing measurable information.

    Numbers, percentages, currency values, and common
    measurement expressions are treated as measurable signals.
    """

    if not text:

        return 0

    count = 0

    for line in text.splitlines():

        stripped = line.strip()

        if not stripped:
            continue

        if re.search(
            r"\b\d+(?:\.\d+)?\s*(?:%|percent|x|k|m|b)?\b",
            stripped,
            re.IGNORECASE,
        ):

            count += 1

    return count


# ============================================================
# RESUME LENGTH
# ============================================================

def analyze_resume_length(
    resume: dict,
) -> dict:
    """Analyze the approximate amount of resume content."""

    fields = [
        "summary",
        "skills",
        "experience",
        "projects",
        "education",
        "certifications",
        "achievements",
        "other",
    ]

    combined_text = " ".join(
        _text(
            resume.get(
                field
            )
        )
        for field in fields
    )

    word_count = count_words(
        combined_text
    )

    if word_count == 0:

        rating = "empty"

    elif word_count < 150:

        rating = "short"

    elif word_count <= 1000:

        rating = "good"

    else:

        rating = "long"

    return {
        "word_count": word_count,
        "rating": rating,
    }


# ============================================================
# SECTION LENGTHS
# ============================================================

def analyze_section_lengths(
    resume: dict,
) -> dict:
    """Analyze the word count of important resume sections."""

    sections = [
        "summary",
        "skills",
        "experience",
        "projects",
        "education",
        "certifications",
        "achievements",
    ]

    result = {}

    for section in sections:

        text = _text(
            resume.get(
                section
            )
        )

        result[section] = {
            "word_count": count_words(
                text
            ),
            "has_content": bool(
                text
            ),
        }

    return result


# ============================================================
# BULLET USAGE
# ============================================================

def analyze_bullet_usage(
    resume: dict,
) -> dict:
    """Analyze bullet-point usage across resume sections."""

    sections = [
        "summary",
        "skills",
        "experience",
        "projects",
        "education",
        "certifications",
        "achievements",
        "other",
    ]

    bullet_counts = {
        section: count_bullets(
            _text(
                resume.get(
                    section
                )
            )
        )
        for section in sections
    }

    total_bullets = sum(
        bullet_counts.values()
    )

    return {
        "total": total_bullets,
        "by_section": bullet_counts,
        "has_bullets": (
            total_bullets > 0
        ),
    }


# ============================================================
# ACHIEVEMENTS
# ============================================================

def analyze_achievements(
    resume: dict,
) -> dict:
    """Analyze whether achievements contain measurable information."""

    achievements = _text(
        resume.get(
            "achievements"
        )
    )

    achievement_lines = [
        line.strip()
        for line in achievements.splitlines()
        if line.strip()
    ]

    measurable = (
        count_quantifiable_achievements(
            achievements
        )
    )

    return {
        "total": len(
            achievement_lines
        ),
        "quantifiable": measurable,
        "has_achievements": bool(
            achievements
        ),
        "has_quantifiable": (
            measurable > 0
        ),
    }


# ============================================================
# CONTACT
# ============================================================

def analyze_contact(
    resume: dict,
) -> dict:
    """Check basic contact information."""

    name_found = bool(
        _text(
            resume.get(
                "name"
            )
        )
    )

    email_found = bool(
        _text(
            resume.get(
                "email"
            )
        )
    )

    phone_found = bool(
        _text(
            resume.get(
                "phone"
            )
        )
    )

    passed = sum(
        [
            name_found,
            email_found,
            phone_found,
        ]
    )

    return {
        "name": name_found,
        "email": email_found,
        "phone": phone_found,
        "passed": passed,
        "total": 3,
    }


# ============================================================
# STRUCTURE
# ============================================================

def analyze_structure(
    resume: dict,
) -> dict:
    """Check consistency of important resume sections."""

    sections = [
        "summary",
        "skills",
        "experience",
        "projects",
        "education",
        "certifications",
        "achievements",
    ]

    present_sections = [
        section
        for section in sections
        if _text(
            resume.get(
                section
            )
        )
    ]

    missing_sections = [
        section
        for section in sections
        if not _text(
            resume.get(
                section
            )
        )
    ]

    return {
        "present_sections": present_sections,
        "missing_sections": missing_sections,
        "present_count": len(
            present_sections
        ),
        "total_sections": len(
            sections
        ),
    }


# ============================================================
# QUALITY SCORE
# ============================================================

def calculate_quality_score(
    length: dict,
    sections: dict,
    bullets: dict,
    achievements: dict,
    contact: dict,
    structure: dict,
) -> dict:
    """
    Calculate a deterministic resume quality score out of 70.
    """

    breakdown = {}

    # --------------------------------------------------------
    # Length: 15 points
    # --------------------------------------------------------

    if length["rating"] == "good":

        breakdown["length"] = 15

    elif length["rating"] in {
        "short",
        "long",
    }:

        breakdown["length"] = 8

    else:

        breakdown["length"] = 0

    # --------------------------------------------------------
    # Sections: 15 points
    # --------------------------------------------------------

    section_ratio = (

        structure["present_count"]
        / structure["total_sections"]

        if structure["total_sections"]
        else 0
    )

    breakdown["sections"] = round(
        section_ratio
        * QUALITY_WEIGHTS["sections"]
    )

    # --------------------------------------------------------
    # Bullets: 10 points
    # --------------------------------------------------------

    if bullets["total"] >= 5:

        breakdown["bullets"] = 10

    elif bullets["total"] > 0:

        breakdown["bullets"] = 5

    else:

        breakdown["bullets"] = 0

    # --------------------------------------------------------
    # Achievements: 10 points
    # --------------------------------------------------------

    if achievements["has_quantifiable"]:

        breakdown["achievements"] = 10

    elif achievements["has_achievements"]:

        breakdown["achievements"] = 5

    else:

        breakdown["achievements"] = 0

    # --------------------------------------------------------
    # Contact: 10 points
    # --------------------------------------------------------

    contact_ratio = (

        contact["passed"]
        / contact["total"]

        if contact["total"]
        else 0
    )

    breakdown["contact"] = round(
        contact_ratio
        * QUALITY_WEIGHTS["contact"]
    )

    # --------------------------------------------------------
    # Structure: 10 points
    # --------------------------------------------------------

    if structure["present_count"] >= 5:

        breakdown["structure"] = 10

    elif structure["present_count"] >= 3:

        breakdown["structure"] = 5

    else:

        breakdown["structure"] = 0

    score = sum(
        breakdown.values()
    )

    return {
        "score": score,
        "max_score": MAX_SCORE,
        "breakdown": breakdown,
    }


# ============================================================
# QUALITY SUGGESTIONS
# ============================================================

def generate_quality_suggestions(
    length: dict,
    sections: dict,
    bullets: dict,
    achievements: dict,
    contact: dict,
    structure: dict,
) -> list[str]:
    """Generate deterministic resume quality suggestions."""

    suggestions = []

    if length["rating"] == "empty":

        suggestions.append(
            "Add meaningful resume content before analysis."
        )

    elif length["rating"] == "short":

        suggestions.append(
            "Consider adding more relevant experience, projects, "
            "skills, or achievements."
        )

    elif length["rating"] == "long":

        suggestions.append(
            "Consider shortening the resume by removing "
            "repetitive or less relevant content."
        )

    if not bullets["has_bullets"]:

        suggestions.append(
            "Use bullet points for experience, projects, and "
            "achievements to improve readability."
        )

    if not achievements["has_achievements"]:

        suggestions.append(
            "Add measurable achievements or accomplishments."
        )

    elif not achievements["has_quantifiable"]:

        suggestions.append(
            "Add numbers, percentages, or measurable results "
            "to your achievements where appropriate."
        )

    if not contact["name"]:

        suggestions.append(
            "Add your full name."
        )

    if not contact["email"]:

        suggestions.append(
            "Add a professional email address."
        )

    if not contact["phone"]:

        suggestions.append(
            "Add a phone number."
        )

    if structure["missing_sections"]:

        missing = ", ".join(
            section.title()
            for section
            in structure[
                "missing_sections"
            ]
        )

        suggestions.append(
            f"Consider adding these sections: {missing}."
        )

    if (
        sections["summary"]["word_count"]
        > 100
    ):

        suggestions.append(
            "Keep the professional summary concise and focused."
        )

    return suggestions


# ============================================================
# COMPLETE QUALITY ANALYSIS
# ============================================================

def analyze_resume_quality(
    resume: dict,
) -> dict:
    """
    Run the complete resume quality analysis.

    V3.2 additionally includes section intelligence.
    """

    length = analyze_resume_length(
        resume
    )

    sections = analyze_section_lengths(
        resume
    )

    bullets = analyze_bullet_usage(
        resume
    )

    achievements = analyze_achievements(
        resume
    )

    contact = analyze_contact(
        resume
    )

    structure = analyze_structure(
        resume
    )

    score = calculate_quality_score(
        length,
        sections,
        bullets,
        achievements,
        contact,
        structure,
    )

    suggestions = generate_quality_suggestions(
        length,
        sections,
        bullets,
        achievements,
        contact,
        structure,
    )

    # --------------------------------------------------------
    # V3.2 Section Intelligence
    # --------------------------------------------------------

    section_intelligence = (
        analyze_section_intelligence(
            resume
        )
    )

    return {
        "score": score["score"],

        "max_score": score[
            "max_score"
        ],

        "breakdown": score[
            "breakdown"
        ],

        "length": length,

        "sections": sections,

        "bullets": bullets,

        "achievements": achievements,

        "contact": contact,

        "structure": structure,

        "suggestions": suggestions,

        # V3.2
        "section_intelligence":
            section_intelligence,
    }