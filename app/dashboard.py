"""
Unified dashboard calculations for the AI Resume Analyzer.

V2.2
- Unified overall score
- ATS / quality / job-match / improvement breakdown
- Deduplicated recommendations
- Quick summary information
"""

from __future__ import annotations

import re


# ============================================================
# SCORE HELPERS
# ============================================================


def _clamp_score(score) -> int:
    """Return a score safely constrained to 0-100."""

    try:
        value = int(round(float(score)))
    except (TypeError, ValueError):
        return 0

    return max(0, min(100, value))


def _get_score(result: dict | None, *paths) -> int | None:
    """
    Safely extract a score from a nested result dictionary.

    Example:
        _get_score(ats_result, "ats_score", "score")
    """

    if not isinstance(result, dict):
        return None

    current = result

    for key in paths:

        if not isinstance(current, dict):
            return None

        current = current.get(key)

    if current is None:
        return None

    try:
        return _clamp_score(current)

    except (TypeError, ValueError):
        return None


# ============================================================
# RECOMMENDATION HELPERS
# ============================================================


def _clean_recommendation(text) -> str:
    """Normalize recommendation text for comparison/display."""

    if not text:
        return ""

    text = str(text).strip()

    # Normalize common dash characters.
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Remove common bullet prefixes.
    text = re.sub(
        r"^[\-\*\u2022\u25aa\u25ab\u25cf]+\s*",
        "",
        text,
    )

    # Collapse repeated whitespace.
    text = " ".join(text.split())

    return text


def _recommendation_key(text) -> str:
    """
    Create a normalized comparison key.

    The goal is to identify recommendations that communicate
    the same action even when their wording is slightly different.
    """

    value = _clean_recommendation(text).lower()

    if not value:
        return ""

    # Remove punctuation.
    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value,
    )

    # Collapse whitespace.
    value = " ".join(value.split())

    # --------------------------------------------------------
    # Normalize common wording variations.
    # --------------------------------------------------------

    replacements = {

        # ----------------------------------------------------
        # Work experience / internships
        # ----------------------------------------------------

        "add relevant work experience or internships":
            "work experience",

        "add relevant work experience internships":
            "work experience",

        "add relevant work experience internships practical experience":
            "work experience",

        "add relevant work experience or internships practical experience":
            "work experience",

        "add relevant work experience internships or practical experience":
            "work experience",

        "consider adding relevant work experience or internships":
            "work experience",

        "consider adding relevant work experience internships":
            "work experience",

        "consider adding relevant work experience internships practical experience":
            "work experience",

        "relevant work experience or internships":
            "work experience",

        "relevant work experience internships":
            "work experience",

        "relevant work experience internships practical experience":
            "work experience",

        "relevant work experience or internships practical experience":
            "work experience",

        "relevant work experience internships or practical experience":
            "work experience",

        # ----------------------------------------------------
        # Experience section
        # ----------------------------------------------------

        "consider adding these sections experience":
            "experience section",

        "consider adding the experience section":
            "experience section",

        "add an experience section":
            "experience section",

        "add experience section":
            "experience section",

        # ----------------------------------------------------
        # Skills
        # ----------------------------------------------------

        "add relevant skills":
            "relevant skills",

        "include relevant skills":
            "relevant skills",

        "list relevant skills":
            "relevant skills",

        # ----------------------------------------------------
        # Projects
        # ----------------------------------------------------

        "add projects":
            "projects",

        "add relevant projects":
            "relevant projects",

        "include relevant projects":
            "relevant projects",

        # ----------------------------------------------------
        # Education
        # ----------------------------------------------------

        "add education section":
            "education section",

        "include education section":
            "education section",

        # ----------------------------------------------------
        # Contact information
        # ----------------------------------------------------

        "add contact information":
            "contact information",

        "include contact information":
            "contact information",
    }

    if value in replacements:
        return replacements[value]

    return value


def _append_unique(
    items: list[str],
    seen: set[str],
    value,
) -> None:
    """Append a recommendation only when it is genuinely new."""

    cleaned = _clean_recommendation(value)

    if not cleaned:
        return

    key = _recommendation_key(cleaned)

    if not key:
        return

    if key in seen:
        return

    seen.add(key)
    items.append(cleaned)


# ============================================================
# RECOMMENDATION COLLECTION
# ============================================================


def collect_recommendations(
    ats_result: dict | None = None,
    quality_result: dict | None = None,
    job_result: dict | None = None,
    improvement_result: dict | None = None,
) -> list[str]:
    """
    Collect recommendations from all analysis modules.

    Recommendations are deduplicated while preserving priority.

    Priority:
        1. ATS
        2. Resume quality
        3. Resume improvements
        4. Job matching
        5. Keyword intelligence
    """

    recommendations: list[str] = []
    seen: set[str] = set()

    # --------------------------------------------------------
    # ATS recommendations.
    # --------------------------------------------------------

    if isinstance(ats_result, dict):

        ats_suggestions = ats_result.get(
            "suggestions",
            [],
        )

        if isinstance(ats_suggestions, list):

            for suggestion in ats_suggestions:

                _append_unique(
                    recommendations,
                    seen,
                    suggestion,
                )

    # --------------------------------------------------------
    # Resume quality recommendations.
    # --------------------------------------------------------

    if isinstance(quality_result, dict):

        quality_suggestions = quality_result.get(
            "suggestions",
            [],
        )

        if isinstance(quality_suggestions, list):

            for suggestion in quality_suggestions:

                _append_unique(
                    recommendations,
                    seen,
                    suggestion,
                )

    # --------------------------------------------------------
    # Resume improvement recommendations.
    # --------------------------------------------------------

    if isinstance(improvement_result, dict):

        improvement_suggestions = improvement_result.get(
            "improvements",
            [],
        )

        if isinstance(improvement_suggestions, list):

            for suggestion in improvement_suggestions:

                _append_unique(
                    recommendations,
                    seen,
                    suggestion,
                )

    # --------------------------------------------------------
    # Job-match recommendations.
    # --------------------------------------------------------

    if isinstance(job_result, dict):

        suggestions = job_result.get(
            "suggestions",
            [],
        )

        if isinstance(suggestions, list):

            for suggestion in suggestions:

                _append_unique(
                    recommendations,
                    seen,
                    suggestion,
                )

        # ----------------------------------------------------
        # Keyword intelligence recommendations.
        # ----------------------------------------------------

        keyword_suggestions = job_result.get(
            "keyword_suggestions",
            [],
        )

        if isinstance(keyword_suggestions, list):

            for suggestion in keyword_suggestions:

                _append_unique(
                    recommendations,
                    seen,
                    suggestion,
                )

    return recommendations


# ============================================================
# OVERALL SCORE
# ============================================================


def calculate_overall_score(
    ats_result: dict | None,
    quality_result: dict | None,
    job_result: dict | None = None,
    improvement_result: dict | None = None,
) -> int:
    """
    Calculate the unified resume score.

    WITHOUT a job description:

        ATS           = 50%
        Quality       = 30%
        Improvements  = 20%

    WITH a job description:

        ATS           = 35%
        Quality       = 25%
        Job Match     = 20%
        Improvements  = 20%
    """

    ats_score = _get_score(
        ats_result,
        "ats_score",
        "score",
    )

    quality_score = _get_score(
        quality_result,
        "score",
    )

    improvement_score = _get_score(
        improvement_result,
        "score",
    )

    # Safe fallbacks.
    if ats_score is None:
        ats_score = 0

    if quality_score is None:
        quality_score = 0

    if improvement_score is None:
        improvement_score = 0

    # --------------------------------------------------------
    # With job description.
    # --------------------------------------------------------

    if job_result is not None:

        job_score = _get_score(
            job_result,
            "score",
        )

        if job_score is None:
            job_score = 0

        weighted_score = (
            ats_score * 0.35
            + quality_score * 0.25
            + job_score * 0.20
            + improvement_score * 0.20
        )

    # --------------------------------------------------------
    # Without job description.
    # --------------------------------------------------------

    else:

        weighted_score = (
            ats_score * 0.50
            + quality_score * 0.30
            + improvement_score * 0.20
        )

    return _clamp_score(
        round(weighted_score)
    )


# ============================================================
# SCORE BREAKDOWN
# ============================================================


def build_score_breakdown(
    ats_result: dict | None,
    quality_result: dict | None,
    job_result: dict | None = None,
    improvement_result: dict | None = None,
) -> dict:
    """Build the score breakdown displayed by the dashboard."""

    return {
        "ats": _get_score(
            ats_result,
            "ats_score",
            "score",
        ),

        "quality": _get_score(
            quality_result,
            "score",
        ),

        "job_match": (
            _get_score(
                job_result,
                "score",
            )
            if job_result is not None
            else None
        ),

        "improvements": _get_score(
            improvement_result,
            "score",
        ),
    }


# ============================================================
# SCORE LABEL
# ============================================================


def _score_label(score: int | None) -> str:
    """Return a human-readable score label."""

    if score is None:
        return "Unavailable"

    if score >= 85:
        return "Excellent"

    if score >= 70:
        return "Good"

    if score >= 60:
        return "Needs attention"

    return "Needs improvement"


# ============================================================
# QUICK SUMMARY
# ============================================================


def build_quick_summary(
    breakdown: dict,
    recommendations: list[str],
) -> dict:
    """
    Build a compact summary for the top of the results page.
    """

    valid_scores = {
        key: value
        for key, value in breakdown.items()
        if value is not None
    }

    strongest_area = None
    weakest_area = None

    if valid_scores:

        strongest_key = max(
            valid_scores,
            key=valid_scores.get,
        )

        weakest_key = min(
            valid_scores,
            key=valid_scores.get,
        )

        names = {
            "ats": "ATS Readiness",
            "quality": "Resume Quality",
            "job_match": "Job Match",
            "improvements": "Improvement Readiness",
        }

        strongest_area = {
            "name": names.get(
                strongest_key,
                strongest_key,
            ),
            "score": valid_scores[strongest_key],
        }

        weakest_area = {
            "name": names.get(
                weakest_key,
                weakest_key,
            ),
            "score": valid_scores[weakest_key],
        }

    return {
        "strongest_area": strongest_area,

        "weakest_area": weakest_area,

        "recommendation": (
            recommendations[0]
            if recommendations
            else "Your resume has no immediate recommendation."
        ),
    }


# ============================================================
# DASHBOARD RESULT
# ============================================================


def build_dashboard_result(
    resume: dict,
    ats_result: dict | None,
    quality_result: dict | None,
    job_result: dict | None = None,
    improvement_result: dict | None = None,
) -> dict:
    """Build the complete V2.2 dashboard payload."""

    overall_score = calculate_overall_score(
        ats_result,
        quality_result,
        job_result,
        improvement_result,
    )

    breakdown = build_score_breakdown(
        ats_result,
        quality_result,
        job_result,
        improvement_result,
    )

    recommendations = collect_recommendations(
        ats_result,
        quality_result,
        job_result,
        improvement_result,
    )

    quick_summary = build_quick_summary(
        breakdown,
        recommendations,
    )

    return {
        "overall_score": overall_score,

        "breakdown": breakdown,

        "has_job_match": job_result is not None,

        "recommendations": recommendations,

        "recommendation_count": len(
            recommendations
        ),

        "quick_summary": quick_summary,

        "score_labels": {
            key: _score_label(value)
            for key, value in breakdown.items()
        },

        "resume": resume,
    }