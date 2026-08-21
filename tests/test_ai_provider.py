"""
Tests for V3.3 AI input validation.

These tests verify that AI writing inputs are safely
validated before being sent to the provider.
"""

import pytest

from app.ai.validators import (
    AIValidationError,
    MAX_BULLET_LENGTH,
    MAX_EXPERIENCE_LENGTH,
    MAX_PROJECT_LENGTH,
    MAX_SUMMARY_LENGTH,
    validate_bullet,
    validate_experience,
    validate_project,
    validate_summary,
    validate_text,
)


# ============================================================
# GENERIC TEXT VALIDATION
# ============================================================

def test_validate_text_returns_trimmed_text():
    result = validate_text(
        "   Hello resume   ",
        field_name="Test input",
        max_length=100,
    )

    assert result == "Hello resume"


def test_validate_text_rejects_empty_text():
    with pytest.raises(AIValidationError):
        validate_text(
            "",
            field_name="Test input",
            max_length=100,
        )


def test_validate_text_rejects_whitespace_only_text():
    with pytest.raises(AIValidationError):
        validate_text(
            "   \n\t  ",
            field_name="Test input",
            max_length=100,
        )


def test_validate_text_rejects_non_string():
    with pytest.raises(AIValidationError):
        validate_text(
            123,
            field_name="Test input",
            max_length=100,
        )


def test_validate_text_rejects_excessively_long_text():
    with pytest.raises(AIValidationError):
        validate_text(
            "A" * 101,
            field_name="Test input",
            max_length=100,
        )


def test_validate_text_accepts_text_at_exact_limit():
    value = "A" * 100

    result = validate_text(
        value,
        field_name="Test input",
        max_length=100,
    )

    assert result == value


# ============================================================
# BULLET VALIDATION
# ============================================================

def test_validate_bullet_accepts_valid_bullet():
    bullet = "Developed a Python application."

    assert validate_bullet(bullet) == bullet


def test_validate_bullet_uses_expected_limit():
    bullet = "A" * MAX_BULLET_LENGTH

    assert validate_bullet(bullet) == bullet


def test_validate_bullet_rejects_too_long_bullet():
    with pytest.raises(AIValidationError):
        validate_bullet(
            "A" * (MAX_BULLET_LENGTH + 1)
        )


# ============================================================
# SUMMARY VALIDATION
# ============================================================

def test_validate_summary_accepts_valid_summary():
    summary = (
        "Python developer with experience building "
        "web applications."
    )

    assert validate_summary(summary) == summary


def test_validate_summary_uses_expected_limit():
    summary = "A" * MAX_SUMMARY_LENGTH

    assert validate_summary(summary) == summary


def test_validate_summary_rejects_too_long_summary():
    with pytest.raises(AIValidationError):
        validate_summary(
            "A" * (MAX_SUMMARY_LENGTH + 1)
        )


# ============================================================
# PROJECT VALIDATION
# ============================================================

def test_validate_project_accepts_valid_project():
    project = (
        "Built a Flask application for resume analysis."
    )

    assert validate_project(project) == project


def test_validate_project_uses_expected_limit():
    project = "A" * MAX_PROJECT_LENGTH

    assert validate_project(project) == project


def test_validate_project_rejects_too_long_project():
    with pytest.raises(AIValidationError):
        validate_project(
            "A" * (MAX_PROJECT_LENGTH + 1)
        )


# ============================================================
# EXPERIENCE VALIDATION
# ============================================================

def test_validate_experience_accepts_valid_bullet():
    bullet = (
        "Developed backend services using Python."
    )

    assert validate_experience(bullet) == bullet


def test_validate_experience_uses_expected_limit():
    bullet = "A" * MAX_EXPERIENCE_LENGTH

    assert validate_experience(bullet) == bullet


def test_validate_experience_rejects_too_long_bullet():
    with pytest.raises(AIValidationError):
        validate_experience(
            "A" * (MAX_EXPERIENCE_LENGTH + 1)
        )