"""
Tests for the V3.3 AI writing service.

Provider calls are mocked so these tests never require
a real API key or network connection.
"""

from unittest.mock import patch

import pytest

from app.ai.validators import AIValidationError
from app.ai.writing_service import (
    rewrite_bullet,
    rewrite_experience,
    rewrite_project,
    rewrite_summary,
)


# ============================================================
# BULLET
# ============================================================

@patch("app.ai.writing_service.generate_text")
def test_rewrite_bullet_calls_provider(mock_generate):
    mock_generate.return_value = (
        "Developed Python applications."
    )

    result = rewrite_bullet(
        "Built Python applications."
    )

    assert result == (
        "Developed Python applications."
    )

    mock_generate.assert_called_once()

    kwargs = mock_generate.call_args.kwargs

    assert "system_prompt" in kwargs
    assert "user_prompt" in kwargs
    assert "Built Python applications." in kwargs[
        "user_prompt"
    ]


# ============================================================
# SUMMARY
# ============================================================

@patch("app.ai.writing_service.generate_text")
def test_rewrite_summary_calls_provider(mock_generate):
    mock_generate.return_value = (
        "Python developer experienced in web applications."
    )

    result = rewrite_summary(
        "Python developer."
    )

    assert result == (
        "Python developer experienced in web applications."
    )

    mock_generate.assert_called_once()

    kwargs = mock_generate.call_args.kwargs

    assert "system_prompt" in kwargs
    assert "user_prompt" in kwargs
    assert "Python developer." in kwargs[
        "user_prompt"
    ]


# ============================================================
# PROJECT
# ============================================================

@patch("app.ai.writing_service.generate_text")
def test_rewrite_project_calls_provider(mock_generate):
    mock_generate.return_value = (
        "Developed a Flask-based resume analyzer."
    )

    result = rewrite_project(
        "Built a Flask resume analyzer."
    )

    assert result == (
        "Developed a Flask-based resume analyzer."
    )

    mock_generate.assert_called_once()

    kwargs = mock_generate.call_args.kwargs

    assert "system_prompt" in kwargs
    assert "user_prompt" in kwargs
    assert "Built a Flask resume analyzer." in kwargs[
        "user_prompt"
    ]


# ============================================================
# EXPERIENCE
# ============================================================

@patch("app.ai.writing_service.generate_text")
def test_rewrite_experience_calls_provider(mock_generate):
    mock_generate.return_value = (
        "Developed backend services using Python."
    )

    result = rewrite_experience(
        "Worked on backend services using Python."
    )

    assert result == (
        "Developed backend services using Python."
    )

    mock_generate.assert_called_once()

    kwargs = mock_generate.call_args.kwargs

    assert "system_prompt" in kwargs
    assert "user_prompt" in kwargs
    assert (
        "Worked on backend services using Python."
        in kwargs["user_prompt"]
    )


# ============================================================
# VALIDATION BEFORE PROVIDER
# ============================================================

@patch("app.ai.writing_service.generate_text")
def test_rewrite_bullet_validates_before_provider(
    mock_generate,
):
    with pytest.raises(AIValidationError):
        rewrite_bullet("   ")

    mock_generate.assert_not_called()


@patch("app.ai.writing_service.generate_text")
def test_rewrite_summary_validates_before_provider(
    mock_generate,
):
    with pytest.raises(AIValidationError):
        rewrite_summary("")

    mock_generate.assert_not_called()


@patch("app.ai.writing_service.generate_text")
def test_rewrite_project_validates_before_provider(
    mock_generate,
):
    with pytest.raises(AIValidationError):
        rewrite_project("   ")

    mock_generate.assert_not_called()


@patch("app.ai.writing_service.generate_text")
def test_rewrite_experience_validates_before_provider(
    mock_generate,
):
    with pytest.raises(AIValidationError):
        rewrite_experience("")

    mock_generate.assert_not_called()


# ============================================================
# PROVIDER OUTPUT
# ============================================================

@patch("app.ai.writing_service.generate_text")
def test_rewrite_bullet_returns_provider_output(
    mock_generate,
):
    expected = "Improved resume bullet."

    mock_generate.return_value = expected

    assert rewrite_bullet(
        "Original resume bullet."
    ) == expected