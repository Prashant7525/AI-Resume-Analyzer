"""
AI writing service for the AI Resume Analyzer.

V3.3
- Centralized resume writing operations
- Input validation
- Prompt construction
- AI provider integration
- Consistent error handling
- No Flask route logic
"""

from __future__ import annotations

from app.ai.provider import (
    generate_text,
)
from app.ai.prompts import (
    BULLET_REWRITE_SYSTEM_PROMPT,
    EXPERIENCE_REWRITE_SYSTEM_PROMPT,
    PROJECT_REWRITE_SYSTEM_PROMPT,
    SUMMARY_REWRITE_SYSTEM_PROMPT,
    build_bullet_rewrite_prompt,
    build_experience_rewrite_prompt,
    build_project_rewrite_prompt,
    build_summary_rewrite_prompt,
)
from app.ai.validators import (
    validate_bullet,
    validate_experience,
    validate_project,
    validate_summary,
)


# ============================================================
# BULLET REWRITE
# ============================================================

def rewrite_bullet(
    bullet: str,
) -> str:
    """
    Rewrite a resume bullet using the AI provider.
    """

    validated_bullet = validate_bullet(
        bullet
    )

    prompt = build_bullet_rewrite_prompt(
        validated_bullet
    )

    return generate_text(
        system_prompt=BULLET_REWRITE_SYSTEM_PROMPT,
        user_prompt=prompt,
    )


# ============================================================
# SUMMARY REWRITE
# ============================================================

def rewrite_summary(
    summary: str,
) -> str:
    """
    Improve a professional resume summary.
    """

    validated_summary = validate_summary(
        summary
    )

    prompt = build_summary_rewrite_prompt(
        validated_summary
    )

    return generate_text(
        system_prompt=SUMMARY_REWRITE_SYSTEM_PROMPT,
        user_prompt=prompt,
    )


# ============================================================
# PROJECT REWRITE
# ============================================================

def rewrite_project(
    project: str,
) -> str:
    """
    Improve a resume project description.
    """

    validated_project = validate_project(
        project
    )

    prompt = build_project_rewrite_prompt(
        validated_project
    )

    return generate_text(
        system_prompt=PROJECT_REWRITE_SYSTEM_PROMPT,
        user_prompt=prompt,
    )


# ============================================================
# EXPERIENCE REWRITE
# ============================================================

def rewrite_experience(
    bullet: str,
) -> str:
    """
    Improve an experience bullet.
    """

    validated_bullet = validate_experience(
        bullet
    )

    prompt = build_experience_rewrite_prompt(
        validated_bullet
    )

    return generate_text(
        system_prompt=EXPERIENCE_REWRITE_SYSTEM_PROMPT,
        user_prompt=prompt,
    )