from typing import Any


def _get_score(
    result: dict | None,
    *keys: str,
) -> int | None:
    """Safely retrieve a numeric score from a nested result."""

    if not result:
        return None

    value: Any = result

    for key in keys:
        if not isinstance(value, dict):
            return None

        value = value.get(key)

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return max(0, min(100, round(value)))

    return None


def _score_label(score: int | None) -> str:
    """Return a human-readable label for a score."""

    if score is None:
        return "Not available"

    if score >= 85:
        return "Excellent"

    if score >= 70:
        return "Good"

    if score >= 50:
        return "Needs Improvement"

    return "Needs Attention"


def _score_status(score: int | None) -> str:
    """Return a simple status category for a score."""

    if score is None:
        return "unavailable"

    if score >= 85:
        return "excellent"

    if score >= 70:
        return "good"

    if score >= 50:
        return "average"

    return "weak"


def build_score_metrics(
    ats_result: dict | None,
    quality_result: dict | None,
    improvement_result: dict | None,
    job_result: dict | None = None,
) -> list[dict]:
    """Build dashboard-ready score metrics."""

    definitions = [
        ("ATS Readiness", ats_result, ("ats_score", "score")),
        ("Resume Quality", quality_result, ("score",)),
        ("Improvement Readiness", improvement_result, ("score",)),
        ("Job Match", job_result, ("score",)),
    ]

    metrics = []

    for name, result, keys in definitions:
        score = _get_score(result, *keys)

        metrics.append(
            {
                "name": name,
                "score": score,
                "label": _score_label(score),
                "status": _score_status(score),
            }
        )

    return metrics


def build_strengths(
    ats_result: dict | None,
    quality_result: dict | None,
    improvement_result: dict | None,
    job_result: dict | None = None,
) -> list[str]:
    """Identify strong areas from available analysis results."""

    metrics = build_score_metrics(
        ats_result,
        quality_result,
        improvement_result,
        job_result,
    )

    strengths = []

    for metric in metrics:
        score = metric["score"]

        if score is not None and score >= 85:
            strengths.append(
                f"{metric['name']} is excellent at {score}/100."
            )

        elif score is not None and score >= 70:
            strengths.append(
                f"{metric['name']} is performing well at {score}/100."
            )

    return strengths


def build_attention_areas(
    ats_result: dict | None,
    quality_result: dict | None,
    improvement_result: dict | None,
    job_result: dict | None = None,
) -> list[str]:
    """Identify areas that should receive attention."""

    metrics = build_score_metrics(
        ats_result,
        quality_result,
        improvement_result,
        job_result,
    )

    areas = []

    for metric in metrics:
        score = metric["score"]

        if score is not None and score < 70:
            areas.append(
                f"{metric['name']} needs attention at {score}/100."
            )

    return areas


def build_score_summary(
    ats_result: dict | None,
    quality_result: dict | None,
    improvement_result: dict | None,
    job_result: dict | None = None,
) -> dict:
    """Build a compact score summary for the dashboard."""

    metrics = build_score_metrics(
        ats_result,
        quality_result,
        improvement_result,
        job_result,
    )

    available_scores = [
        metric["score"]
        for metric in metrics
        if metric["score"] is not None
    ]

    if available_scores:
        average_score = round(
            sum(available_scores) / len(available_scores)
        )
    else:
        average_score = 0

    return {
        "average_score": average_score,
        "available_metrics": len(available_scores),
        "total_metrics": len(metrics),
        "metrics": metrics,
    }


def build_analytics_result(
    ats_result: dict | None,
    quality_result: dict | None,
    improvement_result: dict | None,
    job_result: dict | None = None,
) -> dict:
    """Build the complete v2.1 analytics payload."""

    summary = build_score_summary(
        ats_result,
        quality_result,
        improvement_result,
        job_result,
    )

    return {
        "summary": summary,
        "metrics": summary["metrics"],
        "strengths": build_strengths(
            ats_result,
            quality_result,
            improvement_result,
            job_result,
        ),
        "attention_areas": build_attention_areas(
            ats_result,
            quality_result,
            improvement_result,
            job_result,
        ),
    }