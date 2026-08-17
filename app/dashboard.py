from typing import Any


def _get_score(result: dict | None, *keys: str) -> int:
    """Safely retrieve a numeric score from a nested result."""

    if not result:
        return 0

    current: Any = result

    for key in keys:
        if not isinstance(current, dict):
            return 0

        current = current.get(key)

    if isinstance(current, (int, float)):
        return int(current)

    return 0


def _clamp_score(score: int) -> int:
    """Keep a score inside the 0-100 range."""

    return max(0, min(100, int(score)))


def calculate_overall_score(
    ats_result: dict | None,
    quality_result: dict | None,
    job_result: dict | None = None,
    improvement_result: dict | None = None,
) -> int:
    """
    Calculate a unified resume score.

    Without a job description:
        ATS           = 50%
        Quality       = 30%
        Improvements  = 20%

    With a job description:
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

    if job_result is not None:
        job_score = _get_score(
            job_result,
            "score",
        )

        weighted_score = (
            ats_score * 0.35
            + quality_score * 0.25
            + job_score * 0.20
            + improvement_score * 0.20
        )

    else:
        weighted_score = (
            ats_score * 0.50
            + quality_score * 0.30
            + improvement_score * 0.20
        )

    return _clamp_score(round(weighted_score))


def build_score_breakdown(
    ats_result: dict | None,
    quality_result: dict | None,
    job_result: dict | None = None,
    improvement_result: dict | None = None,
) -> dict:
    """Build a normalized score breakdown for the dashboard."""

    breakdown = {
        "ats": _get_score(
            ats_result,
            "ats_score",
            "score",
        ),
        "quality": _get_score(
            quality_result,
            "score",
        ),
        "job_match": None,
        "improvements": None,
    }

    if job_result is not None:
        breakdown["job_match"] = _get_score(
            job_result,
            "score",
        )

    if improvement_result is not None:
        breakdown["improvements"] = _get_score(
            improvement_result,
            "score",
        )

    return breakdown


def collect_recommendations(
    ats_result: dict | None,
    quality_result: dict | None,
    job_result: dict | None = None,
    improvement_result: dict | None = None,
) -> list[str]:
    """Collect recommendations from all available analyzers."""

    recommendations = []

    if improvement_result:
        recommendations.extend(
            improvement_result.get(
                "improvements",
                [],
            )
        )

    if quality_result:
        recommendations.extend(
            quality_result.get(
                "suggestions",
                [],
            )
        )

    if ats_result:
        recommendations.extend(
            ats_result.get(
                "suggestions",
                [],
            )
        )

    if job_result:
        recommendations.extend(
            job_result.get(
                "suggestions",
                [],
            )
        )

        recommendations.extend(
            job_result.get(
                "keyword_suggestions",
                [],
            )
        )

    # Remove duplicates while preserving order.
    unique = []

    for recommendation in recommendations:
        if recommendation and recommendation not in unique:
            unique.append(recommendation)

    return unique


def build_dashboard_result(
    resume: dict,
    ats_result: dict,
    quality_result: dict,
    job_result: dict | None = None,
    improvement_result: dict | None = None,
) -> dict:
    """Build the complete unified dashboard payload."""

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

    return {
        "overall_score": overall_score,
        "breakdown": breakdown,
        "recommendations": recommendations,
        "recommendation_count": len(recommendations),
        "has_job_match": job_result is not None,
        "resume_name": resume.get(
            "name",
            "",
        ),
    }