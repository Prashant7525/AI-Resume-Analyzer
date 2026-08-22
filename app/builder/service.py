"""
Service layer for the V4.0 Resume Builder.
"""

from __future__ import annotations

from typing import Any

from app.builder.model import (
    ResumeBuilderData,
)
from app.builder.validators import (
    sanitize_builder_text,
    validate_entry_list,
    validate_list,
)


def normalize_builder_data(
    data: dict[str, Any] | None,
) -> ResumeBuilderData:
    """
    Normalize incoming builder data.
    """

    if not isinstance(
        data,
        dict,
    ):
        return ResumeBuilderData()

    return ResumeBuilderData(
        name=sanitize_builder_text(
            data.get("name", "")
        ),
        email=sanitize_builder_text(
            data.get("email", "")
        ),
        phone=sanitize_builder_text(
            data.get("phone", "")
        ),
        location=sanitize_builder_text(
            data.get("location", "")
        ),
        linkedin=sanitize_builder_text(
            data.get("linkedin", "")
        ),
        github=sanitize_builder_text(
            data.get("github", "")
        ),
        summary=sanitize_builder_text(
            data.get("summary", ""),
            max_length=3000,
        ),
        skills=validate_list(
            data.get("skills")
        ),
        experience=validate_entry_list(
            data.get("experience")
        ),
        projects=validate_entry_list(
            data.get("projects")
        ),
        education=validate_entry_list(
            data.get("education")
        ),
        certifications=validate_list(
            data.get("certifications")
        ),
        achievements=validate_list(
            data.get("achievements")
        ),
    )


def builder_payload(
    data: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Return normalized builder data as a dictionary.
    """

    return normalize_builder_data(
        data
    ).to_dict()