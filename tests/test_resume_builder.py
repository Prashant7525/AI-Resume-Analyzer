import pytest

from app.builder.model import ResumeBuilderData
from app.builder.service import builder_payload, normalize_builder_data
from app.builder.validators import (
    MAX_ITEMS,
    sanitize_builder_text,
    validate_entry_list,
)


def test_builder_model_defaults():
    resume = ResumeBuilderData()

    assert resume.name == ""
    assert resume.skills == []
    assert resume.experience == []


def test_builder_text_sanitization():
    value = "Hello\x00\r\nWorld"

    result = sanitize_builder_text(value)

    assert "\x00" not in result
    assert "\r" not in result
    assert "Hello\nWorld" == result


def test_normalize_builder_data():
    data = {
        "name": "Prashant",
        "email": "test@example.com",
        "skills": ["Python", "Flask"],
        "experience": [
            {
                "role": "Developer",
                "company": "Example",
                "bullets": [
                    "Built a Flask API.",
                    "Added automated tests.",
                ],
            }
        ],
    }

    result = normalize_builder_data(data)

    assert result.name == "Prashant"
    assert result.email == "test@example.com"
    assert result.skills == ["Python", "Flask"]
    assert result.experience[0]["role"] == "Developer"
    assert result.experience[0]["bullets"] == [
        "Built a Flask API.",
        "Added automated tests.",
    ]


def test_structured_project_and_education_are_preserved():
    result = normalize_builder_data(
        {
            "projects": [
                {
                    "name": "Resume Builder",
                    "technologies": "Python, Flask",
                    "description": "Built a resume builder.",
                    "bullets": ["Added live preview."],
                    "url": "https://example.com",
                }
            ],
            "education": [
                {
                    "degree": "B.Tech",
                    "institution": "University",
                    "year": "2026",
                }
            ],
        }
    )

    assert result.projects[0]["name"] == "Resume Builder"
    assert result.projects[0]["bullets"] == ["Added live preview."]
    assert result.education[0]["degree"] == "B.Tech"
    assert result.education[0]["year"] == "2026"


def test_invalid_collections_are_safe():
    result = normalize_builder_data(
        {
            "skills": "Python",
            "experience": "invalid",
            "projects": None,
            "education": {},
        }
    )

    assert result.skills == []
    assert result.experience == []
    assert result.projects == []
    assert result.education == []


def test_nested_non_string_values_are_not_leaked():
    result = validate_entry_list(
        [
            {
                "company": "Example",
                "bullets": ["Safe", 123, None],
                "metadata": {"secret": "value"},
            }
        ]
    )

    assert result == [
        {
            "company": "Example",
            "bullets": ["Safe"],
        }
    ]


def test_limits_are_enforced():
    result = normalize_builder_data(
        {
            "skills": [f"Skill {i}" for i in range(MAX_ITEMS + 10)],
            "experience": [
                {"company": f"Company {i}"}
                for i in range(MAX_ITEMS + 10)
            ],
        }
    )

    assert len(result.skills) == MAX_ITEMS
    assert len(result.experience) == MAX_ITEMS


def test_builder_payload():
    result = builder_payload(
        {
            "name": "Test User",
            "summary": "Developer",
            "experience": [
                {
                    "job_title": "Developer",
                    "bullets": ["Built software."],
                }
            ],
        }
    )

    assert result["name"] == "Test User"
    assert result["summary"] == "Developer"
    assert result["experience"][0]["bullets"] == [
        "Built software."
    ]


def test_non_string_personal_fields_are_safe():
    result = normalize_builder_data(
        {
            "name": 123,
            "email": None,
            "phone": ["not", "a", "phone"],
        }
    )

    assert result.name == ""
    assert result.email == ""
    assert result.phone == ""


def test_legacy_entry_aliases_are_migrated():
    result = normalize_builder_data(
        {
            "experience": [{"role": "Developer", "company": "Example"}],
            "projects": [{"title": "Portfolio"}],
            "education": [{"degree": "B.Tech", "school": "University"}],
        }
    )

    assert result.experience[0]["job_title"] == "Developer"
    assert result.projects[0]["name"] == "Portfolio"
    assert result.education[0]["institution"] == "University"
