"""
AI service for V3.4 job tailoring.

V3.4
- AI-powered job tailoring
- Structured tailoring response validation
- Development fallback when AI provider is unavailable
- Production-safe provider behavior
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from app.ai.provider import (
    AIProviderError,
    generate_text,
    is_ai_configured,
)
from app.ai.tailoring.prompts import (
    TAILORING_SYSTEM_PROMPT,
    build_tailoring_prompt,
)
from app.ai.tailoring.validators import (
    validate_tailoring_inputs,
)


class AITailoringError(RuntimeError):
    """Raised when AI job tailoring fails."""


# ============================================================
# DEVELOPMENT FALLBACK
# ============================================================

COMMON_JOB_TERMS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "kotlin",
    "c",
    "c++",
    "flask",
    "django",
    "fastapi",
    "sql",
    "mysql",
    "postgresql",
    "sqlite",
    "mongodb",
    "rest",
    "api",
    "rest api",
    "backend",
    "frontend",
    "full stack",
    "html",
    "css",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "cloud",
    "linux",
    "ci/cd",
    "testing",
    "debugging",
    "data structures",
    "algorithms",
    "database",
    "databases",
    "machine learning",
    "artificial intelligence",
    "ai",
    "pandas",
    "numpy",
    "react",
    "angular",
    "node.js",
    "node",
}


def _normalise_text(value: str) -> str:
    """
    Normalize text for matching.
    """

    return re.sub(
        r"\s+",
        " ",
        value.lower(),
    ).strip()


def _extract_job_terms(
    job_description: str,
) -> list[str]:
    """
    Extract relevant technical terms from the job description.
    """

    normalized = _normalise_text(
        job_description
    )

    found: list[str] = []

    for term in COMMON_JOB_TERMS:

        if term in normalized:

            found.append(
                term
            )

    return sorted(
        set(found)
    )


def _extract_resume_terms(
    resume_text: str,
) -> set[str]:
    """
    Detect supported technical terms in the resume.
    """

    normalized = _normalise_text(
        resume_text
    )

    found: set[str] = set()

    for term in COMMON_JOB_TERMS:

        if term in normalized:
            found.add(term)

    return found


def _development_tailoring(
    *,
    resume_text: str,
    job_description: str,
) -> dict[str, Any]:
    """
    Generate deterministic tailoring results for development.

    This allows the complete V3.4 workflow to be tested without
    requiring a live AI provider.

    This fallback is intentionally deterministic and does not
    claim to be an AI-generated result.
    """

    job_terms = _extract_job_terms(
        job_description
    )

    resume_terms = _extract_resume_terms(
        resume_text
    )

    matched = [
        term
        for term in job_terms
        if term in resume_terms
    ]

    missing = [
        term
        for term in job_terms
        if term not in resume_terms
    ]

    important_keywords = job_terms[:10]

    recommendations: list[str] = []

    if missing:

        recommendations.append(
            "Highlight relevant missing job keywords "
            "only where they are genuinely supported by "
            "your experience."
        )

    if "backend" in job_terms:
        recommendations.append(
            "Emphasize backend development, APIs, "
            "server-side implementation, and related "
            "project work where applicable."
        )

    if (
        "python" in job_terms
        and "python" in resume_terms
    ):
        recommendations.append(
            "Highlight Python implementations and "
            "specific technical contributions in "
            "relevant projects."
        )

    if (
        "api" in job_terms
        or "rest api" in job_terms
    ):
        recommendations.append(
            "Mention REST/API development in relevant "
            "projects or experience when supported by "
            "the resume."
        )

    if "docker" in job_terms:
        recommendations.append(
            "Add Docker only when you have genuine "
            "Docker experience."
        )

    if "testing" in job_terms:
        recommendations.append(
            "Highlight automated testing, debugging, "
            "and code-quality practices where applicable."
        )

    if not recommendations:

        recommendations.append(
            "Strengthen the resume by emphasizing the "
            "most relevant skills and measurable project "
            "outcomes for this role."
        )

    if job_terms:

        coverage = round(
            (
                len(matched)
                / len(job_terms)
            )
            * 100
        )

    else:

        coverage = 0

    if matched:

        match_summary = (
            f"Development tailoring result: "
            f"{coverage}% of detected job terms are "
            f"present in the resume."
        )

    else:

        match_summary = (
            "Development tailoring result: no strong "
            "keyword overlap was detected."
        )

    return {
        "match_summary": match_summary,
        "missing_skills": missing[:10],
        "important_keywords": important_keywords,
        "tailored_recommendations": recommendations[:6],
        "development_mode": True,
        "matched_keywords": matched[:10],
    }


# ============================================================
# RESPONSE PARSING
# ============================================================

def _parse_response(
    text: str,
) -> dict[str, Any]:
    """
    Parse and validate structured AI output.
    """

    try:

        result = json.loads(
            text
        )

    except (
        TypeError,
        json.JSONDecodeError,
    ) as exc:

        raise AITailoringError(
            "AI tailoring returned invalid data."
        ) from exc

    if not isinstance(
        result,
        dict,
    ):

        raise AITailoringError(
            "AI tailoring returned an invalid response."
        )

    required_keys = {
        "match_summary",
        "missing_skills",
        "important_keywords",
        "tailored_recommendations",
    }

    if not required_keys.issubset(
        result
    ):

        raise AITailoringError(
            "AI tailoring response is incomplete."
        )

    if not isinstance(
        result.get(
            "match_summary"
        ),
        str,
    ):

        raise AITailoringError(
            "AI tailoring match summary is invalid."
        )

    for key in (
        "missing_skills",
        "important_keywords",
        "tailored_recommendations",
    ):

        if not isinstance(
            result.get(key),
            list,
        ):

            raise AITailoringError(
                f"AI tailoring field '{key}' is invalid."
            )

    result["missing_skills"] = [
        str(item)
        for item in result[
            "missing_skills"
        ]
    ]

    result["important_keywords"] = [
        str(item)
        for item in result[
            "important_keywords"
        ]
    ]

    result["tailored_recommendations"] = [
        str(item)
        for item in result[
            "tailored_recommendations"
        ]
    ]

    result.setdefault(
        "development_mode",
        False,
    )

    return result


# ============================================================
# MAIN SERVICE
# ============================================================

def tailor_resume_to_job(
    *,
    resume_text: str,
    job_description: str,
) -> dict[str, Any]:
    """
    Generate job-tailoring recommendations.

    Uses the configured AI provider when available.

    In development, a deterministic fallback is used only
    when the real provider reports that it is not configured.

    In production, missing AI configuration remains an error.
    """

    resume_text, job_description = (
        validate_tailoring_inputs(
            resume_text,
            job_description,
        )
    )

    app_env = os.getenv(
        "APP_ENV",
        "development",
    ).strip().lower()

    # --------------------------------------------------------
    # Try the provider first.
    #
    # This is important for:
    # - real AI usage
    # - unit-test monkeypatching
    # - detecting invalid AI responses
    # --------------------------------------------------------

    try:

        response = generate_text(
            system_prompt=
                TAILORING_SYSTEM_PROMPT,

            user_prompt=
                build_tailoring_prompt(
                    resume_text,
                    job_description,
                ),
        )

        return _parse_response(
            response
        )

    except AIProviderError as exc:

        # ----------------------------------------------------
        # Development fallback when the provider is simply
        # not configured.
        # ----------------------------------------------------

        if (
            app_env != "production"
            and str(exc)
            == "AI provider is not configured."
        ):

            return _development_tailoring(
                resume_text=resume_text,
                job_description=job_description,
            )

        raise AITailoringError(
            "Unable to generate job-tailoring recommendations."
        ) from exc

    except AITailoringError:

        # Preserve structured-response errors.
        raise