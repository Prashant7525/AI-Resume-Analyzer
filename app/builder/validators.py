"""
Validation helpers for the V4.0 Resume Builder.

The builder accepts a small, explicit data model and keeps nested
repeatable sections safe.  The helpers are deliberately framework-free
so they can be tested independently of Flask.
"""

from __future__ import annotations

import re
from typing import Any


MAX_FIELD_LENGTH = 5000
MAX_SUMMARY_LENGTH = 3000
MAX_ITEMS = 50
MAX_BULLETS = 20

# The builder UI only needs these nested list fields.  Supporting them
# here prevents the old generic validator from silently dropping bullets.
NESTED_STRING_LIST_FIELDS = frozenset({"bullets"})


def sanitize_builder_text(
    value: Any,
    *,
    max_length: int = MAX_FIELD_LENGTH,
) -> str:
    """Normalize text and remove control characters."""

    if not isinstance(value, str):
        return ""

    value = value.replace("\x00", "")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)

    lines = [line.rstrip() for line in value.split("\n")]
    return "\n".join(lines).strip()[:max_length]


def validate_list(value: Any) -> list[str]:
    """Validate a simple list of strings."""

    if not isinstance(value, list):
        return []

    result: list[str] = []

    for item in value[:MAX_ITEMS]:
        cleaned = sanitize_builder_text(item)
        if cleaned:
            result.append(cleaned)

    return result


def validate_entry_list(
    value: Any,
) -> list[dict[str, Any]]:
    """
    Validate repeatable builder entries.

    Scalar values are sanitized as strings. Known nested list fields,
    currently ``bullets``, are validated as string lists.
    Unknown scalar keys are retained for backward compatibility.
    """

    if not isinstance(value, list):
        return []

    result: list[dict[str, Any]] = []

    for item in value[:MAX_ITEMS]:
        if not isinstance(item, dict):
            continue

        entry: dict[str, Any] = {}

        for key, raw_value in item.items():
            key_text = sanitize_builder_text(
                str(key),
                max_length=100,
            )

            if not key_text:
                continue

            if key_text in NESTED_STRING_LIST_FIELDS:
                entry[key_text] = validate_list(raw_value)[:MAX_BULLETS]
                continue

            if isinstance(raw_value, str):
                cleaned = sanitize_builder_text(raw_value)
                if cleaned:
                    entry[key_text] = cleaned

        if any(
            value
            for value in entry.values()
            if value
        ):
            result.append(entry)

    return result
