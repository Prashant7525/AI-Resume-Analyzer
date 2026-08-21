"""
Validation helpers for AI job tailoring.
"""
from __future__ import annotations


class TailoringValidationError(ValueError):
    """Raised when tailoring input is invalid."""


MAX_RESUME_TEXT_LENGTH = 50000
MAX_JOB_DESCRIPTION_LENGTH = 20000


def validate_tailoring_inputs(
    resume_text: str,
    job_description: str,
) -> tuple[str, str]:

    if not isinstance(resume_text, str):
        raise TailoringValidationError(
            "Resume text must be a string."
        )

    if not isinstance(job_description, str):
        raise TailoringValidationError(
            "Job description must be a string."
        )

    resume_text = resume_text.strip()
    job_description = job_description.strip()

    if not resume_text:
        raise TailoringValidationError(
            "Resume text is required."
        )

    if not job_description:
        raise TailoringValidationError(
            "Job description is required."
        )

    if len(resume_text) > MAX_RESUME_TEXT_LENGTH:
        raise TailoringValidationError(
            "Resume text is too long."
        )

    if len(job_description) > MAX_JOB_DESCRIPTION_LENGTH:
        raise TailoringValidationError(
            "Job description is too long."
        )

    return resume_text, job_description
