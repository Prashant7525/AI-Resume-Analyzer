"""
Resume-level intelligence summary engine.

V3.2.4
- Combines section intelligence
- Combines bullet intelligence
- Combines achievement intelligence
- Calculates a separate intelligence score
- Detects top strengths
- Detects top attention areas
- Generates a concise summary
"""

from __future__ import annotations

from typing import Any


# ============================================================
# CONFIGURATION
# ============================================================

MAX_INTELLIGENCE_SCORE = 100

SECTION_WEIGHT = 40
BULLET_WEIGHT = 35
ACHIEVEMENT_WEIGHT = 25


# ============================================================
# SAFE HELPERS
# ============================================================

def _number(
    value: Any,
    default: float = 0,
) -> float:
    """Return a safe numeric value."""

    if isinstance(
        value,
        bool,
    ):
        return default

    if isinstance(
        value,
        (int, float),
    ):
        return float(value)

    return default


def _text(
    value: Any,
) -> str:
    """Return a safe text value."""

    if value is None:
        return ""

    return str(
        value
    ).strip()


# ============================================================
# STATUS HELPERS
# ============================================================

def _status_for_score(
    score: float,
) -> str:
    """Convert an intelligence score into a status."""

    if score >= 85:
        return "strong"

    if score >= 70:
        return "good"

    if score >= 50:
        return "needs_attention"

    return "weak"


# ============================================================
# SECTION INTELLIGENCE
# ============================================================

def _extract_section_summary(
    section_intelligence: dict | None,
) -> dict:
    """
    Extract the important section-intelligence signals.
    """

    section_intelligence = (
        section_intelligence
        or {}
    )

    score = _number(
        section_intelligence.get(
            "score"
        )
    )

    section_count = int(
        _number(
            section_intelligence.get(
                "section_count"
            )
        )
    )

    total_sections = int(
        _number(
            section_intelligence.get(
                "total_sections"
            )
        )
    )

    coverage_score = _number(
        section_intelligence.get(
            "coverage_score"
        )
    )

    average_section_score = _number(
        section_intelligence.get(
            "average_section_score"
        )
    )

    sections = section_intelligence.get(
        "sections",
        {},
    )

    if not isinstance(
        sections,
        dict,
    ):
        sections = {}

    return {
        "score": round(
            score
        ),
        "status": _status_for_score(
            score
        ),
        "section_count": section_count,
        "total_sections": total_sections,
        "coverage_score": round(
            coverage_score
        ),
        "average_section_score": round(
            average_section_score
        ),
        "sections": sections,
    }


# ============================================================
# BULLET INTELLIGENCE
# ============================================================

def _extract_bullet_summary(
    bullet_intelligence: dict | None,
) -> dict:
    """
    Extract important bullet-quality signals.
    """

    bullet_intelligence = (
        bullet_intelligence
        or {}
    )

    score = _number(
        bullet_intelligence.get(
            "average_score"
        )
    )

    total_bullets = int(
        _number(
            bullet_intelligence.get(
                "total_bullets"
            )
        )
    )

    strong_bullets = int(
        _number(
            bullet_intelligence.get(
                "strong_bullets"
            )
        )
    )

    needs_attention = int(
        _number(
            bullet_intelligence.get(
                "needs_attention_bullets"
            )
        )
    )

    sections = bullet_intelligence.get(
        "sections",
        {},
    )

    if not isinstance(
        sections,
        dict,
    ):
        sections = {}

    return {
        "score": round(
            score
        ),
        "status": _status_for_score(
            score
        ),
        "total_bullets": total_bullets,
        "strong_bullets": strong_bullets,
        "needs_attention_bullets":
            needs_attention,
        "sections": sections,
    }


# ============================================================
# ACHIEVEMENT INTELLIGENCE
# ============================================================

def _extract_achievement_summary(
    achievement_intelligence: dict | None,
) -> dict:
    """
    Extract important achievement-quality signals.
    """

    achievement_intelligence = (
        achievement_intelligence
        or {}
    )

    score = _number(
        achievement_intelligence.get(
            "average_score"
        )
    )

    total = int(
        _number(
            achievement_intelligence.get(
                "total"
            )
        )
    )

    strong_count = int(
        _number(
            achievement_intelligence.get(
                "strong_count"
            )
        )
    )

    needs_attention_count = int(
        _number(
            achievement_intelligence.get(
                "needs_attention_count"
            )
        )
    )

    measurable_count = int(
        _number(
            achievement_intelligence.get(
                "measurable_count"
            )
        )
    )

    ranking_count = int(
        _number(
            achievement_intelligence.get(
                "ranking_count"
            )
        )
    )

    achievements = achievement_intelligence.get(
        "achievements",
        [],
    )

    if not isinstance(
        achievements,
        list,
    ):
        achievements = []

    return {
        "score": round(
            score
        ),
        "status": _status_for_score(
            score
        ),
        "total": total,
        "strong_count": strong_count,
        "needs_attention_count":
            needs_attention_count,
        "measurable_count":
            measurable_count,
        "ranking_count":
            ranking_count,
        "achievements": achievements,
    }


# ============================================================
# STRENGTH DETECTION
# ============================================================

def _build_strengths(
    sections: dict,
    bullets: dict,
    achievements: dict,
) -> list[dict]:
    """
    Build high-level resume strengths.
    """

    strengths: list[dict] = []

    # --------------------------------------------------------
    # Sections
    # --------------------------------------------------------

    if sections["score"] >= 85:

        strengths.append(
            {
                "area": "sections",
                "label": "Resume Structure",
                "score": sections["score"],
                "message": (
                    "Your resume sections are well structured "
                    "and consistently populated."
                ),
            }
        )

    elif sections["coverage_score"] >= 85:

        strengths.append(
            {
                "area": "sections",
                "label": "Section Coverage",
                "score": sections[
                    "coverage_score"
                ],
                "message": (
                    "Your resume covers most important sections."
                ),
            }
        )

    # --------------------------------------------------------
    # Bullets
    # --------------------------------------------------------

    if bullets["score"] >= 85:

        strengths.append(
            {
                "area": "bullets",
                "label": "Bullet Quality",
                "score": bullets["score"],
                "message": (
                    "Your bullets show strong action, specificity, "
                    "technical detail, and measurable impact."
                ),
            }
        )

    elif (
        bullets["total_bullets"] > 0
        and bullets["strong_bullets"]
        >= max(
            1,
            bullets["total_bullets"]
            // 2,
        )
    ):

        strengths.append(
            {
                "area": "bullets",
                "label": "Bullet Usage",
                "score": bullets["score"],
                "message": (
                    "A substantial portion of your bullets "
                    "demonstrates strong resume-writing signals."
                ),
            }
        )

    # --------------------------------------------------------
    # Achievements
    # --------------------------------------------------------

    if achievements["score"] >= 85:

        strengths.append(
            {
                "area": "achievements",
                "label": "Achievement Quality",
                "score": achievements[
                    "score"
                ],
                "message": (
                    "Your achievements contain strong measurable "
                    "evidence and impact signals."
                ),
            }
        )

    elif (
        achievements["measurable_count"] > 0
    ):

        strengths.append(
            {
                "area": "achievements",
                "label": "Measurable Achievements",
                "score": achievements[
                    "score"
                ],
                "message": (
                    "Your achievements include measurable results."
                ),
            }
        )

    strengths.sort(
        key=lambda item: item[
            "score"
        ],
        reverse=True,
    )

    return strengths


# ============================================================
# ATTENTION AREA DETECTION
# ============================================================

def _build_attention_areas(
    sections: dict,
    bullets: dict,
    achievements: dict,
) -> list[dict]:
    """
    Build high-level areas requiring improvement.
    """

    attention: list[dict] = []

    # --------------------------------------------------------
    # Sections
    # --------------------------------------------------------

    missing_sections = [
        section
        for section, data
        in sections["sections"].items()
        if isinstance(
            data,
            dict,
        )
        and data.get(
            "status"
        ) == "missing"
    ]

    if missing_sections:

        attention.append(
            {
                "area": "sections",
                "label": "Missing Sections",
                "score": sections[
                    "score"
                ],
                "message": (
                    "Important resume sections are missing: "
                    + ", ".join(
                        section.replace(
                            "_",
                            " ",
                        ).title()
                        for section
                        in missing_sections
                    )
                    + "."
                ),
            }
        )

    elif sections["score"] < 70:

        attention.append(
            {
                "area": "sections",
                "label": "Section Quality",
                "score": sections[
                    "score"
                ],
                "message": (
                    "Several resume sections need stronger "
                    "content or structure."
                ),
            }
        )

    # --------------------------------------------------------
    # Bullets
    # --------------------------------------------------------

    if bullets["total_bullets"] == 0:

        attention.append(
            {
                "area": "bullets",
                "label": "Bullet Quality",
                "score": bullets[
                    "score"
                ],
                "message": (
                    "No analyzable bullets were detected in "
                    "experience, projects, or achievements."
                ),
            }
        )

    elif bullets[
        "needs_attention_bullets"
    ] > 0:

        attention.append(
            {
                "area": "bullets",
                "label": "Bullet Improvement",
                "score": bullets[
                    "score"
                ],
                "message": (
                    f"{bullets['needs_attention_bullets']} "
                    "bullet(s) need stronger wording, metrics, "
                    "specificity, or impact."
                ),
            }
        )

    # --------------------------------------------------------
    # Achievements
    # --------------------------------------------------------

    if achievements["total"] == 0:

        attention.append(
            {
                "area": "achievements",
                "label": "Achievements",
                "score": achievements[
                    "score"
                ],
                "message": (
                    "Add measurable achievements to demonstrate "
                    "results and impact."
                ),
            }
        )

    elif achievements[
        "needs_attention_count"
    ] > 0:

        attention.append(
            {
                "area": "achievements",
                "label": "Achievement Improvement",
                "score": achievements[
                    "score"
                ],
                "message": (
                    f"{achievements['needs_attention_count']} "
                    "achievement(s) need stronger measurable "
                    "evidence or impact."
                ),
            }
        )

    attention.sort(
        key=lambda item: item[
            "score"
        ]
    )

    return attention


# ============================================================
# INTELLIGENCE SCORE
# ============================================================

def calculate_intelligence_score(
    section_score: float,
    bullet_score: float,
    achievement_score: float,
) -> int:
    """
    Calculate the separate V3.2.4 intelligence score.

    This score is independent from the existing 70-point
    resume quality score.
    """

    score = (

        section_score
        * SECTION_WEIGHT
        / 100

        +

        bullet_score
        * BULLET_WEIGHT
        / 100

        +

        achievement_score
        * ACHIEVEMENT_WEIGHT
        / 100
    )

    return max(
        0,
        min(
            MAX_INTELLIGENCE_SCORE,
            round(score),
        ),
    )


# ============================================================
# SUMMARY TEXT
# ============================================================

def _build_summary_message(
    score: int,
    strengths: list[dict],
    attention: list[dict],
) -> str:
    """
    Build a concise human-readable intelligence summary.
    """

    if score >= 85:

        opening = (
            "Your resume demonstrates strong overall intelligence "
            "across structure, bullets, and achievements."
        )

    elif score >= 70:

        opening = (
            "Your resume has a solid intelligence foundation, "
            "with several areas that can still be strengthened."
        )

    elif score >= 50:

        opening = (
            "Your resume has a developing intelligence profile "
            "and would benefit from targeted improvements."
        )

    else:

        opening = (
            "Your resume needs substantial improvement in "
            "structure, bullet quality, and measurable evidence."
        )

    if strengths:

        opening += (
            " Strongest area: "
            + strengths[0]["label"]
            + "."
        )

    if attention:

        opening += (
            " Main attention area: "
            + attention[0]["label"]
            + "."
        )

    return opening


# ============================================================
# COMPLETE RESUME INTELLIGENCE
# ============================================================

def analyze_resume_intelligence(
    *,
    section_intelligence: dict | None = None,
    bullet_intelligence: dict | None = None,
    achievement_intelligence: dict | None = None,
) -> dict:
    """
    Combine V3.2 section, bullet, and achievement
    intelligence into a single resume-level summary.
    """

    sections = _extract_section_summary(
        section_intelligence
    )

    bullets = _extract_bullet_summary(
        bullet_intelligence
    )

    achievements = _extract_achievement_summary(
        achievement_intelligence
    )

    intelligence_score = (
        calculate_intelligence_score(
            sections["score"],
            bullets["score"],
            achievements["score"],
        )
    )

    strengths = _build_strengths(
        sections,
        bullets,
        achievements,
    )

    attention = _build_attention_areas(
        sections,
        bullets,
        achievements,
    )

    summary = _build_summary_message(
        intelligence_score,
        strengths,
        attention,
    )

    return {
        "score": intelligence_score,

        "max_score":
            MAX_INTELLIGENCE_SCORE,

        "status": _status_for_score(
            intelligence_score
        ),

        "summary": summary,

        "components": {
            "sections": sections,
            "bullets": bullets,
            "achievements": achievements,
        },

        "strengths": strengths,

        "attention_areas": attention,
    }