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

    # ========================================================
    # PERSONAL INFORMATION
    # ========================================================

    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""

    # ========================================================
    # PROFESSIONAL SUMMARY
    # ========================================================

    summary: str = ""

    # ========================================================
    # SKILLS
    # ========================================================

    skills: list[str] = field(
        default_factory=list
    )

    # ========================================================
    # EXPERIENCE
    # ========================================================

    experience: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ========================================================
    # PROJECTS
    # ========================================================

    projects: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ========================================================
    # EDUCATION
    # ========================================================

    education: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ========================================================
    # CERTIFICATIONS
    # ========================================================

    certifications: list[str] = field(
        default_factory=list
    )

    # ========================================================
    # ACHIEVEMENTS
    # ========================================================

    achievements: list[str] = field(
        default_factory=list
    )

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the builder model to a dictionary.
        """

        return asdict(self)

    # ========================================================
    # DESERIALIZATION
    # ========================================================

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any] | None,
    ) -> "ResumeBuilderData":
        """
        Build a resume model safely from a dictionary.

        Existing V4.0 data remains compatible while
        structured repeatable sections are supported.
        """

        if not isinstance(
            data,
            dict,
        ):
            return cls()

        return cls(
            # ------------------------------------------------
            # Personal information
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Summary
            # ------------------------------------------------

            summary=str(
                data.get(
                    "summary",
                    "",
                )
                or ""
            ),

            # ------------------------------------------------
            # Skills
            # ------------------------------------------------

            skills=[
                str(item)
                for item in _safe_list(
                    data.get("skills")
                )
                if str(item).strip()
            ],

            # ------------------------------------------------
            # Experience
            # ------------------------------------------------

            experience=[
                _normalize_experience_entry(
                    item
                )
                for item in _safe_list(
                    data.get("experience")
                )
                if isinstance(
                    item,
                    dict,
                )
            ],

            # ------------------------------------------------
            # Projects
            # ------------------------------------------------

            projects=[
                _normalize_project_entry(
                    item
                )
                for item in _safe_list(
                    data.get("projects")
                )
                if isinstance(
                    item,
                    dict,
                )
            ],

            # ------------------------------------------------
            # Education
            # ------------------------------------------------

            education=[
                _normalize_education_entry(
                    item
                )
                for item in _safe_list(
                    data.get("education")
                )
                if isinstance(
                    item,
                    dict,
                )
            ],

            # ------------------------------------------------
            # Certifications
            # ------------------------------------------------

            certifications=[
                str(item).strip()
                for item in _safe_list(
                    data.get("certifications")
                )
                if str(item).strip()
            ],

            # ------------------------------------------------
            # Achievements
            # ------------------------------------------------

            achievements=[
                str(item).strip()
                for item in _safe_list(
                    data.get("achievements")
                )
                if str(item).strip()
            ],
        )


# ============================================================
# SAFE DATA HELPERS
# ============================================================

def _safe_list(
    value: Any,
) -> list[Any]:
    """
    Return a list or an empty list.
    """

    return (
        value
        if isinstance(
            value,
            list,
        )
        else []
    )


def _safe_string(
    value: Any,
) -> str:
    """
    Convert a value safely to a stripped string.
    """

    if value is None:
        return ""

    return str(
        value
    ).strip()


def _safe_string_list(
    value: Any,
) -> list[str]:
    """
    Convert a value into a clean list of strings.
    """

    return [
        _safe_string(item)
        for item in _safe_list(value)
        if _safe_string(item)
    ]


# ============================================================
# EXPERIENCE
# ============================================================

def _normalize_experience_entry(
    value: Any,
) -> dict[str, Any]:
    """
    Normalize one experience entry.

    Supported fields:

        job_title
        company
        location
        start_date
        end_date
        bullets
    """

    if not isinstance(
        value,
        dict,
    ):
        return {}

    return {
        "job_title": _safe_string(
            value.get("job_title")
        ),
        "company": _safe_string(
            value.get("company")
        ),
        "location": _safe_string(
            value.get("location")
        ),
        "start_date": _safe_string(
            value.get("start_date")
        ),
        "end_date": _safe_string(
            value.get("end_date")
        ),
        "bullets": _safe_string_list(
            value.get("bullets")
        ),
    }


# ============================================================
# PROJECTS
# ============================================================

def _normalize_project_entry(
    value: Any,
) -> dict[str, Any]:
    """
    Normalize one project entry.

    Supported fields:

        name
        technologies
        description
        bullets
        url
    """

    if not isinstance(
        value,
        dict,
    ):
        return {}

    return {
        "name": _safe_string(
            value.get("name")
        ),
        "technologies": _safe_string(
            value.get("technologies")
        ),
        "description": _safe_string(
            value.get("description")
        ),
        "bullets": _safe_string_list(
            value.get("bullets")
        ),
        "url": _safe_string(
            value.get("url")
        ),
    }


# ============================================================
# EDUCATION
# ============================================================

def _normalize_education_entry(
    value: Any,
) -> dict[str, Any]:
    """
    Normalize one education entry.

    Supported fields:

        degree
        institution
        location
        start_date
        end_date
        year
        details
    """

    if not isinstance(
        value,
        dict,
    ):
        return {}

    return {
        "degree": _safe_string(
            value.get("degree")
        ),
        "institution": _safe_string(
            value.get("institution")
        ),
        "location": _safe_string(
            value.get("location")
        ),
        "start_date": _safe_string(
            value.get("start_date")
        ),
        "end_date": _safe_string(
            value.get("end_date")
        ),
        "year": _safe_string(
            value.get("year")
        ),
        "details": _safe_string(
            value.get("details")
        ),
    }


# ============================================================
# GENERIC BACKWARD-COMPATIBILITY HELPER
# ============================================================

def _safe_entry(
    value: Any,
) -> dict[str, str]:
    """
    Normalize a generic builder entry.

    Kept for backward compatibility with existing
    V4.0 code and tests.
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