"""
Validation helpers for the V4.0 Resume Builder.
"""

from __future__ import annotations

import re
from typing import Any


MAX_FIELD_LENGTH = 5000
MAX_SUMMARY_LENGTH = 3000
MAX_ITEMS = 50


def sanitize_builder_text(
    value: Any,
    *,
    max_length: int = MAX_FIELD_LENGTH,
) -> str:
    """
    Normalize builder text.
    """

    if not isinstance(
        value,
        str,
    ):
        return ""

    value = value.replace(
        "\x00",
        "",
    )

    value = value.replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    )

    value = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]",
        "",
        value,
    )

    lines = [
        line.rstrip()
        for line in value.split("\n")
    ]

    return "\n".join(
        lines
    ).strip()[:max_length]


def validate_list(
    value: Any,
) -> list[str]:
    """
    Validate a simple string list.
    """

    if not isinstance(
        value,
        list,
    ):
        return []

    return [
        sanitize_builder_text(item)
        for item in value[:MAX_ITEMS]
        if isinstance(item, str)
        and sanitize_builder_text(item)
    ]


def validate_entry_list(
    value: Any,
) -> list[dict[str, str]]:
    """
    Validate structured builder entries.
    """

    if not isinstance(
        value,
        list,
    ):
        return []

    result: list[dict[str, str]] = []

    for item in value[:MAX_ITEMS]:

        if not isinstance(
            item,
            dict,
        ):
            continue

        entry = {
            str(key): sanitize_builder_text(
                val,
                max_length=MAX_FIELD_LENGTH,
            )
            for key, val in item.items()
            if isinstance(
                val,
                str,
            )
        }

        if any(
            entry.values()
        ):
            result.append(
                entry
            )

    return result