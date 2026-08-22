"""
Resume Builder data model for V4.0.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ResumeBuilderData:
    """
    Structured resume data used by the V4.0 builder.
    """

    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""

    summary: str = ""

    skills: list[str] = field(
        default_factory=list
    )

    experience: list[dict[str, str]] = field(
        default_factory=list
    )

    projects: list[dict[str, str]] = field(
        default_factory=list
    )

    education: list[dict[str, str]] = field(
        default_factory=list
    )

    certifications: list[str] = field(
        default_factory=list
    )

    achievements: list[str] = field(
        default_factory=list
    )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the builder model to a dictionary.
        """

        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any] | None,
    ) -> "ResumeBuilderData":
        """
        Build a resume model safely from a dictionary.
        """

        if not isinstance(
            data,
            dict,
        ):
            return cls()

        return cls(
            name=str(
                data.get(
                    "name",
                    "",
                )
                or ""
            ),
            email=str(
                data.get(
                    "email",
                    "",
                )
                or ""
            ),
            phone=str(
                data.get(
                    "phone",
                    "",
                )
                or ""
            ),
            location=str(
                data.get(
                    "location",
                    "",
                )
                or ""
            ),
            linkedin=str(
                data.get(
                    "linkedin",
                    "",
                )
                or ""
            ),
            github=str(
                data.get(
                    "github",
                    "",
                )
                or ""
            ),
            summary=str(
                data.get(
                    "summary",
                    "",
                )
                or ""
            ),
            skills=[
                str(item)
                for item in _safe_list(
                    data.get("skills")
                )
            ],
            experience=[
                _safe_entry(item)
                for item in _safe_list(
                    data.get("experience")
                )
            ],
            projects=[
                _safe_entry(item)
                for item in _safe_list(
                    data.get("projects")
                )
            ],
            education=[
                _safe_entry(item)
                for item in _safe_list(
                    data.get("education")
                )
            ],
            certifications=[
                str(item)
                for item in _safe_list(
                    data.get("certifications")
                )
            ],
            achievements=[
                str(item)
                for item in _safe_list(
                    data.get("achievements")
                )
            ],
        )


def _safe_list(value: Any) -> list:
    """
    Return a list or an empty list.
    """

    return (
        value
        if isinstance(value, list)
        else []
    )


def _safe_entry(value: Any) -> dict[str, str]:
    """
    Normalize a builder entry.
    """

    if not isinstance(
        value,
        dict,
    ):
        return {}

    return {
        str(key): str(item)
        for key, item in value.items()
    }