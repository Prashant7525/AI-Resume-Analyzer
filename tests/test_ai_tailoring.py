import json

import pytest

from app.ai.tailoring.service import (
    AITailoringError,
    tailor_resume_to_job,
)
from app.ai.tailoring.validators import (
    TailoringValidationError,
    validate_tailoring_inputs,
)


def test_validate_tailoring_inputs():
    resume, job = validate_tailoring_inputs(
        "Python developer",
        "Backend Python developer",
    )

    assert resume == "Python developer"
    assert job == "Backend Python developer"


def test_empty_resume_rejected():
    with pytest.raises(TailoringValidationError):
        validate_tailoring_inputs(
            "",
            "Python developer",
        )


def test_empty_job_description_rejected():
    with pytest.raises(TailoringValidationError):
        validate_tailoring_inputs(
            "Python developer",
            "",
        )


def test_tailoring_success(monkeypatch):
    response = {
        "match_summary": "Strong backend alignment.",
        "missing_skills": ["Docker"],
        "important_keywords": ["Python", "REST API"],
        "tailored_recommendations": [
            "Highlight existing REST API experience."
        ],
    }

    monkeypatch.setattr(
        "app.ai.tailoring.service.generate_text",
        lambda **kwargs: json.dumps(response),
    )

    result = tailor_resume_to_job(
        resume_text="Python developer with REST API experience.",
        job_description="Looking for Python and REST API experience.",
    )

    assert result["match_summary"]
    assert result["important_keywords"] == [
        "Python",
        "REST API",
    ]


def test_invalid_ai_response(monkeypatch):
    monkeypatch.setattr(
        "app.ai.tailoring.service.generate_text",
        lambda **kwargs: "not json",
    )

    with pytest.raises(AITailoringError):
        tailor_resume_to_job(
            resume_text="Python developer.",
            job_description="Python developer required.",
        )
