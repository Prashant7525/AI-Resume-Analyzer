"""
Input validation helpers for the AI Resume Analyzer.

V3.3
- Validate AI writing inputs
- Normalize user-provided text
- Enforce safe input limits
- Prevent empty or excessively large prompts
- Provide consistent validation errors
"""

from __future__ import annotations


# ============================================================
# INPUT LIMITS
# ============================================================

MAX_BULLET_LENGTH = 3000

MAX_SUMMARY_LENGTH = 5000

MAX_PROJECT_LENGTH = 5000

MAX_EXPERIENCE_LENGTH = 3000


# ============================================================
# EXCEPTIONS
# ============================================================

class AIValidationError(ValueError):
    """
    Raised when AI writing input fails validation.
    """


# ============================================================
# GENERIC TEXT VALIDATION
# ============================================================

def validate_text(
    value: str,
    *,
    field_name: str,
    max_length: int,
) -> str:
    """
    Validate and normalize AI input text.

    Returns:
        Cleaned text.

    Raises:
        AIValidationError:
            When the input is invalid.
    """

    if not isinstance(
        value,
        str,
    ):
        raise AIValidationError(
            f"{field_name} must be text."
        )

    cleaned = value.strip()

    if not cleaned:
        raise AIValidationError(
            f"{field_name} cannot be empty."
        )

    if len(cleaned) > max_length:
        raise AIValidationError(
            f"{field_name} is too long. "
            f"Maximum length is {max_length} characters."
        )

    return cleaned


# ============================================================
# BULLET VALIDATION
# ============================================================

def validate_bullet(
    bullet: str,
) -> str:
    """
    Validate a resume bullet before AI rewriting.
    """

    return validate_text(
        bullet,
        field_name="Resume bullet",
        max_length=MAX_BULLET_LENGTH,
    )


# ============================================================
# SUMMARY VALIDATION
# ============================================================

def validate_summary(
    summary: str,
) -> str:
    """
    Validate a professional summary before AI rewriting.
    """

    return validate_text(
        summary,
        field_name="Professional summary",
        max_length=MAX_SUMMARY_LENGTH,
    )


# ============================================================
# PROJECT VALIDATION
# ============================================================

def validate_project(
    project: str,
) -> str:
    """
    Validate a project description before AI rewriting.
    """

    return validate_text(
        project,
        field_name="Project description",
        max_length=MAX_PROJECT_LENGTH,
    )


# ============================================================
# EXPERIENCE VALIDATION
# ============================================================

def validate_experience(
    bullet: str,
) -> str:
    """
    Validate an experience bullet before AI rewriting.
    """

    return validate_text(
        bullet,
        field_name="Experience bullet",
        max_length=MAX_EXPERIENCE_LENGTH,
    )