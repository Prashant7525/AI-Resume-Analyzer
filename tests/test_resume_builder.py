import pytest

from app.builder.model import (
    ResumeBuilderData,
)
from app.builder.service import (
    builder_payload,
    normalize_builder_data,
)
from app.builder.validators import (
    sanitize_builder_text,
)


def test_builder_model_defaults():

    resume = ResumeBuilderData()

    assert resume.name == ""
    assert resume.skills == []
    assert resume.experience == []


def test_builder_text_sanitization():

    value = (
        "Hello\x00\r\n"
        "World"
    )

    result = sanitize_builder_text(
        value
    )

    assert "\x00" not in result
    assert "\r" not in result
    assert "Hello\nWorld" == result


def test_normalize_builder_data():

    data = {
        "name": "Prashant",
        "email": "test@example.com",
        "skills": [
            "Python",
            "Flask",
        ],
        "experience": [
            {
                "role": "Developer",
                "company": "Example",
            }
        ],
    }

    result = normalize_builder_data(
        data
    )

    assert result.name == "Prashant"
    assert result.email == "test@example.com"
    assert result.skills == [
        "Python",
        "Flask",
    ]
    assert result.experience[0]["role"] == (
        "Developer"
    )


def test_invalid_collections_are_safe():

    result = normalize_builder_data(
        {
            "skills": "Python",
            "experience": "invalid",
        }
    )

    assert result.skills == []
    assert result.experience == []


def test_builder_payload():

    result = builder_payload(
        {
            "name": "Test User",
            "summary": "Developer",
        }
    )

    assert result["name"] == "Test User"
    assert result["summary"] == "Developer"