"""
Resume Builder data model for V4.0.

The model is intentionally dependency-free and keeps the public field
names stable for the existing application/tests.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.builder.validators import (
    MAX_BULLETS,
    MAX_ITEMS,
    MAX_SUMMARY_LENGTH,
    sanitize_builder_text,
    validate_entry_list,
    validate_list,
)


@dataclass
class ResumeBuilderData:
    """Structured resume data used by the V4.0 builder."""

    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""

    summary: str = ""

    skills: list[str] = field(default_factory=list)

    experience: list[dict[str, Any]] = field(default_factory=list)
    projects: list[dict[str, Any]] = field(default_factory=list)
    education: list[dict[str, Any]] = field(default_factory=list)

    certifications: list[str] = field(default_factory=list)
    achievements: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable copy of the builder data."""

        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any] | None,
    ) -> "ResumeBuilderData":
        """Safely build a normalized model from arbitrary input."""

        if not isinstance(data, dict):
            return cls()

        return cls(
            name=sanitize_builder_text(data.get("name")),
            email=sanitize_builder_text(data.get("email")),
            phone=sanitize_builder_text(data.get("phone")),
            location=sanitize_builder_text(data.get("location")),
            linkedin=sanitize_builder_text(data.get("linkedin")),
            github=sanitize_builder_text(data.get("github")),
            summary=sanitize_builder_text(
                data.get("summary"),
                max_length=MAX_SUMMARY_LENGTH,
            ),
            skills=validate_list(data.get("skills"))[:MAX_ITEMS],
            experience=[
                _normalize_experience_entry(item)
                for item in validate_entry_list(data.get("experience"))
                if isinstance(item, dict)
            ],
            projects=[
                _normalize_project_entry(item)
                for item in validate_entry_list(data.get("projects"))
                if isinstance(item, dict)
            ],
            education=[
                _normalize_education_entry(item)
                for item in validate_entry_list(data.get("education"))
                if isinstance(item, dict)
            ],
            certifications=validate_list(
                data.get("certifications")
            )[:MAX_ITEMS],
            achievements=validate_list(
                data.get("achievements")
            )[:MAX_ITEMS],
        )


def _safe_list(value: Any) -> list[Any]:
    """Return a list or an empty list."""

    return value if isinstance(value, list) else []


def _safe_string(value: Any) -> str:
    """Return a normalized string."""

    return sanitize_builder_text(value)


def _safe_string_list(value: Any) -> list[str]:
    """Return a normalized list of strings."""

    return validate_list(value)[:MAX_BULLETS]


def _normalize_experience_entry(value: Any) -> dict[str, Any]:
    """Normalize an experience entry while retaining legacy scalar keys."""

    if not isinstance(value, dict):
        return {}

    entry: dict[str, Any] = {
        str(key): _safe_string(raw)
        for key, raw in value.items()
        if isinstance(raw, str)
    }

    for key in (
        "job_title",
        "company",
        "location",
        "start_date",
        "end_date",
    ):
        entry[key] = _safe_string(value.get(key))

    # Legacy builder data used ``role`` for the job title.
    if not entry["job_title"]:
        entry["job_title"] = _safe_string(
            value.get("role")
        )

    entry["bullets"] = _safe_string_list(value.get("bullets"))
    return entry


def _normalize_project_entry(value: Any) -> dict[str, Any]:
    """Normalize a project entry while retaining legacy scalar keys."""

    if not isinstance(value, dict):
        return {}

    entry: dict[str, Any] = {
        str(key): _safe_string(raw)
        for key, raw in value.items()
        if isinstance(raw, str)
    }

    for key in (
        "name",
        "technologies",
        "description",
        "url",
    ):
        entry[key] = _safe_string(value.get(key))

    # Preserve compatibility with older project payloads.
    if not entry["name"]:
        entry["name"] = _safe_string(
            value.get("title")
        )

    entry["bullets"] = _safe_string_list(value.get("bullets"))
    return entry


def _normalize_education_entry(value: Any) -> dict[str, Any]:
    """Normalize an education entry."""

    if not isinstance(value, dict):
        return {}

    entry: dict[str, Any] = {
        str(key): _safe_string(raw)
        for key, raw in value.items()
        if isinstance(raw, str)
    }

    for key in (
        "degree",
        "institution",
        "location",
        "start_date",
        "end_date",
        "year",
        "details",
    ):
        entry[key] = _safe_string(value.get(key))

    if not entry["institution"]:
        entry["institution"] = _safe_string(
            value.get("school")
        )

    return entry


def _safe_entry(value: Any) -> dict[str, str]:
    """
    Backward-compatible generic helper.

    Only scalar values are included because the old helper promised
    ``dict[str, str]``.
    """

    if not isinstance(value, dict):
        return {}

    return {
        str(key): str(item)
        for key, item in value.items()
        if not isinstance(item, (list, dict))
    }
