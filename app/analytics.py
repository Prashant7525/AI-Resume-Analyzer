"""
Resume analytics for the AI Resume Analyzer.

V2.2 scoring:

85-100 -> Excellent
70-84  -> Good
0-69   -> Needs attention
"""

from __future__ import annotations


def _clamp_score(score) -> int:
    """Safely clamp a score to 0-100."""

    try:
        value = int(round(float(score)))
    except (TypeError, ValueError):
        return 0

    return max(0, min(100, value))


def _score_status(score: int | None) -> str:
    """
    Convert a score into an analytics status.

    85-100 -> excellent
    70-84  -> good
    0-69   -> attention
    """

    if score is None:
        return "unavailable"

    if score >= 85:
        return "excellent"

    if score >= 70:
        return "good"

    return "attention"


def _score_label(score: int | None) -> str:
    """Return a descriptive label for a score."""

    if score is None:
        return "Score unavailable."

    if score >= 85:
        return "Excellent performance."

    if score >= 70:
        return "Performing well."

    return "Needs attention."


def _get_score(result: dict | None, *paths):
    """Safely retrieve a nested score."""

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


def build_analytics(
    ats_result: dict | None,
    quality_result: dict | None,
    improvement_result: dict | None,
    job_result: dict | None = None,
) -> dict:
    """
    Build analytics data for the dashboard.
    """

    metrics = [
        {
            "name": "ATS Readiness",
            "score": _get_score(
                ats_result,
                "ats_score",
                "score",
            ),
            "label": "ATS compatibility and resume structure.",
        },
        {
            "name": "Resume Quality",
            "score": _get_score(
                quality_result,
                "score",
            ),
            "label": "Overall resume quality and presentation.",
        },
        {
            "name": "Improvements",
            "score": _get_score(
                improvement_result,
                "score",
            ),
            "label": "Readiness for targeted resume improvements.",
        },
    ]

    if job_result is not None:

        metrics.append(
            {
                "name": "Job Match",
                "score": _get_score(
                    job_result,
                    "score",
                ),
                "label": "Compatibility with the supplied job description.",
            }
        )

    valid_scores = [
        metric["score"]
        for metric in metrics
        if metric["score"] is not None
    ]

    average_score = (
        round(
            sum(valid_scores) / len(valid_scores)
        )
        if valid_scores
        else 0
    )

    for metric in metrics:

        score = metric["score"]

        metric["status"] = _score_status(
            score
        )

        metric["rating"] = _score_label(
            score
        )

    strengths = []
    attention_areas = []

    for metric in metrics:

        score = metric["score"]

        if score is None:
            continue

        if score >= 85:

            strengths.append(
                f"{metric['name']} is excellent at {score}/100."
            )

        elif score >= 70:

            strengths.append(
                f"{metric['name']} is performing well at {score}/100."
            )

        else:

            attention_areas.append(
                f"{metric['name']} needs attention at {score}/100."
            )

    # If everything is at least 70, do not display
    # a misleading empty attention section.
    if not attention_areas:

        attention_areas = [
            "No major score area requires immediate attention."
        ]

    return {
        "metrics": metrics,

        "summary": {
            "average_score": average_score,
            "metric_count": len(valid_scores),
        },

        "strengths": strengths,

        "attention_areas": attention_areas,
    }