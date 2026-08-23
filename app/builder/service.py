"""
Service layer for the V4.0 Resume Builder.
"""

from __future__ import annotations

from typing import Any

from app.builder.model import ResumeBuilderData


def normalize_builder_data(
    data: dict[str, Any] | None,
) -> ResumeBuilderData:
    """Normalize incoming builder data through one canonical path."""

    return ResumeBuilderData.from_dict(data)


def builder_payload(
    data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return normalized builder data as a dictionary."""

    return normalize_builder_data(data).to_dict()
