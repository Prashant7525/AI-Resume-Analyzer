"""
Resume section intelligence engine.

V3.2
- Section-level quality analysis
- Section presence detection
- Word-count analysis
- Bullet usage analysis
- Quantifiable-result detection
- Strength detection
- Attention-area detection
- Deterministic section scores
"""

from __future__ import annotations

import re
from typing import Any


# ============================================================
# CONFIGURATION
# ============================================================

SECTION_ORDER = [
    "summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
    "achievements",
]


SECTION_LABELS = {
    "summary": "Professional Summary",
    "skills": "Skills",
    "experience": "Work Experience",
    "projects": "Projects",
    "education": "Education",
    "certifications": "Certifications",
    "achievements": "Achievements",
}


# ============================================================
# TEXT HELPERS
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
    """Count words in a section."""

    if not text:
        return 0

    return len(
        re.findall(
            r"\b[\w+#.-]+\b",
            text,
        )
    )


def _bullet_count(text: str) -> int:
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


def _line_count(text: str) -> int:
    """Count meaningful non-empty lines."""

    if not text:
        return 0

    return sum(
        1
        for line in text.splitlines()
        if line.strip()
    )


def _has_numbers(text: str) -> bool:
    """
    Return True when measurable numeric information
    is present.
    """

    if not text:
        return False

    return bool(
        re.search(
            r"\b\d+(?:\.\d+)?\s*"
            r"(?:%|percent|x|k|m|b)?\b",
            text,
            re.IGNORECASE,
        )
    )


# ============================================================
# SECTION REQUIREMENTS
# ============================================================

def _section_expectations(
    section: str,
) -> dict:
    """
    Return deterministic expectations for a section.

    Thresholds are intentionally practical for both
    experienced candidates and fresher/student resumes.
    """

    expectations = {

        "summary": {
            "min_words": 8,
            "max_words": 100,
            "expects_bullets": False,
            "expects_metrics": False,
        },

        "skills": {
            "min_words": 3,
            "max_words": None,
            "expects_bullets": False,
            "expects_metrics": False,
        },

        "experience": {
            "min_words": 15,
            "max_words": None,
            "expects_bullets": True,
            "expects_metrics": True,
        },

        "projects": {
            "min_words": 10,
            "max_words": None,
            "expects_bullets": True,
            "expects_metrics": False,
        },

        "education": {
            "min_words": 3,
            "max_words": None,
            "expects_bullets": False,
            "expects_metrics": False,
        },

        "certifications": {
            "min_words": 2,
            "max_words": None,
            "expects_bullets": False,
            "expects_metrics": False,
        },

        "achievements": {
            "min_words": 6,
            "max_words": None,
            "expects_bullets": True,
            "expects_metrics": True,
        },
    }

    return expectations.get(
        section,
        {
            "min_words": 1,
            "max_words": None,
            "expects_bullets": False,
            "expects_metrics": False,
        },
    )


# ============================================================
# SCORE COMPONENTS
# ============================================================

def _presence_score(
    text: str,
) -> int:
    """Return 0 or 25 depending on section presence."""

    return 25 if text else 0


def _length_score(
    text: str,
    min_words: int,
    max_words: int | None,
) -> tuple[int, str | None]:
    """
    Score section length.

    Returns:
        (points, attention message)
    """

    words = _word_count(text)

    if not text:
        return 0, None

    if words < min_words:
        return (
            0,
            f"Section is short at {words} words.",
        )

    if (
        max_words is not None
        and words > max_words
    ):
        return (
            12,
            f"Section is long at {words} words.",
        )

    return 25, None


def _bullet_score(
    text: str,
    expects_bullets: bool,
) -> tuple[int, str | None]:
    """
    Score bullet usage.

    Bullet expectations are only applied to sections where
    bullets are appropriate.
    """

    if not text:
        return 0, None

    bullets = _bullet_count(text)

    if not expects_bullets:
        return 25, None

    if bullets >= 3:
        return 25, None

    if bullets > 0:
        return (
            12,
            f"Only {bullets} bullet point(s) detected.",
        )

    return (
        0,
        "Use bullet points to make this section easier to scan.",
    )


def _metrics_score(
    text: str,
    expects_metrics: bool,
) -> tuple[int, str | None]:
    """
    Score measurable information.

    Metrics are treated as an improvement signal rather than
    an absolute requirement for every section.
    """

    if not text:
        return 0, None

    if not expects_metrics:
        return 25, None

    if _has_numbers(text):
        return 25, None

    return (
        10,
        "Consider adding measurable results or impact.",
    )


# ============================================================
# SECTION ANALYSIS
# ============================================================

def analyze_section(
    section: str,
    value: Any,
) -> dict:
    """
    Analyze one resume section.
    """

    text = _text(value)

    label = SECTION_LABELS.get(
        section,
        section.replace(
            "_",
            " ",
        ).title(),
    )

    expectations = _section_expectations(
        section
    )

    words = _word_count(text)
    bullets = _bullet_count(text)
    lines = _line_count(text)
    has_metrics = _has_numbers(text)

    # --------------------------------------------------------
    # Missing section
    # --------------------------------------------------------

    if not text:

        return {
            "section": section,
            "label": label,
            "status": "missing",
            "score": 0,
            "max_score": 100,
            "word_count": 0,
            "line_count": 0,
            "bullet_count": 0,
            "has_metrics": False,
            "strengths": [],
            "attention": [
                f"{label} is missing."
            ],
            "recommendation": (
                f"Add a relevant {label.lower()} section."
            ),
        }

    # --------------------------------------------------------
    # Individual scoring components
    # --------------------------------------------------------

    presence_points = _presence_score(
        text
    )

    length_points, length_attention = _length_score(
        text,
        expectations["min_words"],
        expectations["max_words"],
    )

    bullet_points, bullet_attention = _bullet_score(
        text,
        expectations["expects_bullets"],
    )

    metrics_points, metrics_attention = _metrics_score(
        text,
        expectations["expects_metrics"],
    )

    score = (
        presence_points
        + length_points
        + bullet_points
        + metrics_points
    )

    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    # --------------------------------------------------------
    # Strengths
    # --------------------------------------------------------

    strengths: list[str] = [
        "Section is present."
    ]

    if length_points == 25:

        strengths.append(
            "Section length is appropriate."
        )

    if (
        expectations["expects_bullets"]
        and bullets >= 3
    ):

        strengths.append(
            "Good bullet-point usage."
        )

    if (
        expectations["expects_metrics"]
        and has_metrics
    ):

        strengths.append(
            "Measurable information detected."
        )

    if (
        not expectations["expects_bullets"]
        and section in {
            "summary",
            "skills",
            "education",
            "certifications",
        }
    ):

        strengths.append(
            "Section format is appropriate."
        )

    # --------------------------------------------------------
    # Attention areas
    # --------------------------------------------------------

    attention: list[str] = []

    if length_attention:

        attention.append(
            length_attention
        )

    if bullet_attention:

        attention.append(
            bullet_attention
        )

    if metrics_attention:

        attention.append(
            metrics_attention
        )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    if words < expectations["min_words"]:

        status = "needs_attention"

    elif (
        expectations["expects_bullets"]
        and bullets == 0
    ):

        status = "needs_attention"

    elif (
        expectations["expects_metrics"]
        and not has_metrics
    ):

        status = "needs_attention"

    elif score >= 85:

        status = "strong"

    elif score >= 65:

        status = "good"

    elif score >= 40:

        status = "needs_attention"

    else:

        status = "weak"

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    if attention:

        recommendation = attention[0]

    else:

        recommendation = (
            f"{label} is in good shape. "
            "Continue refining it for your target role."
        )

    return {
        "section": section,
        "label": label,
        "status": status,
        "score": score,
        "max_score": 100,
        "word_count": words,
        "line_count": lines,
        "bullet_count": bullets,
        "has_metrics": has_metrics,
        "strengths": strengths,
        "attention": attention,
        "recommendation": recommendation,
    }


# ============================================================
# COMPLETE SECTION INTELLIGENCE
# ============================================================

def analyze_section_intelligence(
    resume: dict,
) -> dict:
    """
    Analyze every major resume section.
    """

    sections = {}

    for section in SECTION_ORDER:

        sections[section] = analyze_section(
            section,
            resume.get(section),
        )

    present = [
        result
        for result in sections.values()
        if result["status"] != "missing"
    ]

    missing = [
        result
        for result in sections.values()
        if result["status"] == "missing"
    ]

    strong = [
        result
        for result in sections.values()
        if result["status"] == "strong"
    ]

    needs_attention = [
        result
        for result in sections.values()
        if result["status"]
        in {
            "needs_attention",
            "weak",
        }
    ]

    scores = [
        result["score"]
        for result in present
    ]

    average_score = (
        round(
            sum(scores) / len(scores)
        )
        if scores
        else 0
    )

    coverage_score = round(
        len(present)
        / len(SECTION_ORDER)
        * 100
    )

    intelligence_score = round(
        average_score * 0.75
        + coverage_score * 0.25
    )

    intelligence_score = max(
        0,
        min(
            100,
            intelligence_score,
        ),
    )

    return {
        "score": intelligence_score,
        "max_score": 100,
        "coverage_score": coverage_score,
        "average_section_score": average_score,
        "sections": sections,
        "present_sections": [
            result["section"]
            for result in present
        ],
        "missing_sections": [
            result["section"]
            for result in missing
        ],
        "strong_sections": [
            result["section"]
            for result in strong
        ],
        "needs_attention": [
            result["section"]
            for result in needs_attention
        ],
        "section_count": len(present),
        "total_sections": len(SECTION_ORDER),
    }