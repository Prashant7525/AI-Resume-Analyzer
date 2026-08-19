"""
Score explanations for the AI Resume Analyzer.

V3.1
- Explains how the overall score is calculated
- Explains ATS score
- Explains resume quality score
- Explains job match score
- Explains improvement readiness
- Uses existing analysis results without changing scoring logic
"""

from __future__ import annotations


def _safe_score(value, default=0) -> int:
    """Safely convert a value into a score between 0 and 100."""

    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        return default

    return max(0, min(100, score))


def _score_label(score: int) -> str:
    """Return a human-readable score label."""

    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 60:
        return "Needs attention"

    return "Needs improvement"


def build_ats_explanation(ats_result: dict | None) -> dict:
    """Explain the ATS score using the existing ATS analysis."""

    if not isinstance(ats_result, dict):
        return {
            "score": None,
            "max_score": 100,
            "label": "Unavailable",
            "explanation": "ATS analysis is not available.",
            "factors": [],
        }

    ats = ats_result.get("ats_score", {})

    score = _safe_score(
        ats.get("score")
    )

    completeness = ats.get(
        "completeness",
        {},
    )

    content_quality = ats.get(
        "content_quality",
        {},
    )

    completeness_score = _safe_score(
        completeness.get("score")
    )

    completeness_max = completeness.get(
        "max_score",
        90,
    )

    weighted_completeness = _safe_score(
        completeness.get("weighted_score")
    )

    quality_score = _safe_score(
        content_quality.get("score")
    )

    quality_max = content_quality.get(
        "max_score",
        50,
    )

    return {
        "score": score,
        "max_score": 100,
        "label": _score_label(score),

        "explanation": (
            "The ATS score combines resume completeness "
            "and content quality. Completeness contributes "
            "up to 50 points and content quality contributes "
            "up to 50 points."
        ),

        "factors": [
            {
                "name": "Resume Completeness",
                "score": completeness_score,
                "max_score": completeness_max,
                "weighted_score": weighted_completeness,
                "weighted_max": 50,
                "description": (
                    "Measures whether important resume sections "
                    "such as summary, skills, experience, projects, "
                    "education, certifications, and achievements "
                    "are present."
                ),
            },
            {
                "name": "Content Quality",
                "score": quality_score,
                "max_score": quality_max,
                "weighted_score": quality_score,
                "weighted_max": 50,
                "description": (
                    "Evaluates the quality signals of the summary, "
                    "skills, experience, projects, and achievements."
                ),
            },
        ],
    }


def build_quality_explanation(
    quality_result: dict | None,
) -> dict:
    """Explain the resume quality score."""

    if not isinstance(quality_result, dict):
        return {
            "score": None,
            "max_score": 70,
            "label": "Unavailable",
            "explanation": "Resume quality analysis is not available.",
            "factors": [],
        }

    score = _safe_score(
        quality_result.get("score")
    )

    max_score = quality_result.get(
        "max_score",
        70,
    )

    breakdown = quality_result.get(
        "breakdown",
        {},
    )

    weights = {
        "length": 15,
        "sections": 15,
        "bullets": 10,
        "achievements": 10,
        "contact": 10,
        "structure": 10,
    }

    descriptions = {
        "length": (
            "Checks whether the resume contains an appropriate "
            "amount of content."
        ),
        "sections": (
            "Measures the presence of important resume sections."
        ),
        "bullets": (
            "Rewards effective use of bullet points for readability."
        ),
        "achievements": (
            "Rewards achievements that contain measurable information."
        ),
        "contact": (
            "Checks whether name, email, and phone information "
            "are available."
        ),
        "structure": (
            "Measures how many important resume sections are present."
        ),
    }

    names = {
        "length": "Resume Length",
        "sections": "Sections",
        "bullets": "Bullet Usage",
        "achievements": "Achievements",
        "contact": "Contact Information",
        "structure": "Structure",
    }

    factors = []

    for key, weight in weights.items():
        factors.append(
            {
                "name": names[key],
                "score": _safe_score(
                    breakdown.get(key)
                ),
                "max_score": weight,
                "description": descriptions[key],
            }
        )

    return {
        "score": score,
        "max_score": max_score,
        "label": _score_label(score),
        "explanation": (
            "Resume quality measures the structure, readability, "
            "content length, achievements, and contact completeness "
            "of the resume."
        ),
        "factors": factors,
    }


def build_job_match_explanation(
    job_result: dict | None,
) -> dict:
    """Explain the job compatibility score."""

    if not isinstance(job_result, dict):
        return {
            "score": None,
            "max_score": 100,
            "label": "Unavailable",
            "explanation": (
                "No job description was provided, so job matching "
                "was not performed."
            ),
            "factors": [],
        }

    score = _safe_score(
        job_result.get("score")
    )

    matched_skills = job_result.get(
        "matched_skills",
        [],
    )

    missing_skills = job_result.get(
        "missing_skills",
        [],
    )

    keyword_coverage = _safe_score(
        job_result.get("keyword_coverage")
    )

    return {
        "score": score,
        "max_score": 100,
        "label": _score_label(score),
        "explanation": (
            "The job match score measures how compatible the "
            "resume is with the supplied job description."
        ),
        "factors": [
            {
                "name": "Matched Skills",
                "score": len(matched_skills)
                if isinstance(matched_skills, list)
                else 0,
                "max_score": None,
                "description": (
                    "Skills detected in both the resume and "
                    "job description."
                ),
            },
            {
                "name": "Missing Skills",
                "score": len(missing_skills)
                if isinstance(missing_skills, list)
                else 0,
                "max_score": None,
                "description": (
                    "Skills requested by the job description "
                    "that were not detected in the resume."
                ),
            },
            {
                "name": "Keyword Coverage",
                "score": keyword_coverage,
                "max_score": 100,
                "description": (
                    "Percentage of relevant job-description "
                    "keywords detected in the resume."
                ),
            },
        ],
    }


def build_improvement_explanation(
    improvement_result: dict | None,
) -> dict:
    """Explain the improvement readiness score."""

    if not isinstance(improvement_result, dict):
        return {
            "score": None,
            "max_score": 100,
            "label": "Unavailable",
            "explanation": (
                "Resume improvement analysis is not available."
            ),
            "factors": [],
        }

    score = _safe_score(
        improvement_result.get("score")
    )

    checks = improvement_result.get(
        "checks",
        {},
    )

    good = 0
    total = 0

    if isinstance(checks, dict):
        total = len(checks)

        for check in checks.values():
            if not isinstance(check, dict):
                continue

            if check.get("status") in {
                "good",
                "complete",
            }:
                good += 1

    return {
        "score": score,
        "max_score": 100,
        "label": _score_label(score),
        "explanation": (
            "Improvement readiness reflects how prepared the "
            "resume is based on the improvement checks performed "
            "by the analyzer."
        ),
        "factors": [
            {
                "name": "Completed Checks",
                "score": good,
                "max_score": total,
                "description": (
                    "Number of improvement areas currently "
                    "identified as good or complete."
                ),
            },
        ],
    }


def build_score_explanations(
    dashboard_result: dict | None,
    ats_result: dict | None,
    quality_result: dict | None,
    job_result: dict | None = None,
    improvement_result: dict | None = None,
) -> dict:
    """
    Build all score explanations.

    Existing scoring calculations remain unchanged.
    """

    dashboard_result = (
        dashboard_result
        if isinstance(dashboard_result, dict)
        else {}
    )

    overall_score = _safe_score(
        dashboard_result.get(
            "overall_score"
        )
    )

    has_job_match = (
        job_result is not None
    )

    if has_job_match:
        formula = (
            "ATS 35% + Resume Quality 25% + "
            "Job Match 20% + Improvement Readiness 20%"
        )
    else:
        formula = (
            "ATS 50% + Resume Quality 30% + "
            "Improvement Readiness 20%"
        )

    return {
        "overall": {
            "score": overall_score,
            "max_score": 100,
            "label": _score_label(overall_score),
            "formula": formula,
            "explanation": (
                "The overall score combines the major resume "
                "analysis areas into one unified score."
            ),
        },

        "ats": build_ats_explanation(
            ats_result
        ),

        "quality": build_quality_explanation(
            quality_result
        ),

        "job_match": build_job_match_explanation(
            job_result
        ),

        "improvements": build_improvement_explanation(
            improvement_result
        ),
    }