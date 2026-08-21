"""
AI service for V3.4 job tailoring.
"""
from __future__ import annotations

import json
from typing import Any

from app.ai.provider import (
    AIProviderError,
    generate_text,
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


def _parse_response(text: str) -> dict[str, Any]:
    try:
        result = json.loads(text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise AITailoringError(
            "AI tailoring returned invalid data."
        ) from exc

    if not isinstance(result, dict):
        raise AITailoringError(
            "AI tailoring returned an invalid response."
        )

    required_keys = {
        "match_summary",
        "missing_skills",
        "important_keywords",
        "tailored_recommendations",
    }

    if not required_keys.issubset(result):
        raise AITailoringError(
            "AI tailoring response is incomplete."
        )

    return result


def tailor_resume_to_job(
    *,
    resume_text: str,
    job_description: str,
) -> dict[str, Any]:

    resume_text, job_description = validate_tailoring_inputs(
        resume_text,
        job_description,
    )

    try:
        response = generate_text(
            system_prompt=TAILORING_SYSTEM_PROMPT,
            user_prompt=build_tailoring_prompt(
                resume_text,
                job_description,
            ),
        )
    except AIProviderError as exc:
        raise AITailoringError(
            "Unable to generate job-tailoring recommendations."
        ) from exc

    return _parse_response(response)
