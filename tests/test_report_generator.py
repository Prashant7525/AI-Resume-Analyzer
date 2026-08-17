from app.report_generator import generate_resume_report


RESUME = {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
}


ATS_RESULT = {
    "ats_score": {
        "score": 80,
        "completeness": {
            "score": 9,
            "max_score": 10,
        },
        "content_quality": {
            "score": 40,
            "max_score": 50,
        },
    },
}


QUALITY_RESULT = {
    "score": 65,
    "max_score": 70,
}


IMPROVEMENT_RESULT = {
    "score": 83,
    "max_score": 100,
    "improvements": [
        "Add relevant work experience.",
        "Improve achievement metrics.",
    ],
}


JOB_RESULT = {
    "score": 78,
    "keyword_coverage": 72,
    "matched_skills": [
        "Python",
        "Flask",
    ],
    "missing_skills": [
        "Docker",
    ],
}


DASHBOARD_RESULT = {
    "overall_score": 78,
    "breakdown": {
        "ats": 80,
        "quality": 65,
        "improvements": 83,
        "job_match": 78,
    },
    "has_job_match": True,
    "recommendations": [
        "Add relevant work experience.",
        "Improve achievement metrics.",
    ],
}


ANALYTICS_RESULT = {
    "summary": {
        "average_score": 76,
    },
    "strengths": [
        "Strong technical skills.",
    ],
    "attention_areas": [
        "Add more experience.",
    ],
}


def test_generate_basic_report():
    pdf = generate_resume_report(
        RESUME,
        ATS_RESULT,
        QUALITY_RESULT,
        IMPROVEMENT_RESULT,
        JOB_RESULT,
        DASHBOARD_RESULT,
        ANALYTICS_RESULT,
    )

    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000


def test_generate_report_without_optional_results():
    pdf = generate_resume_report(
        RESUME,
        ATS_RESULT,
        QUALITY_RESULT,
    )

    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF")


def test_generate_report_with_empty_results():
    pdf = generate_resume_report(
        RESUME,
    )

    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF")


def test_generate_report_handles_missing_resume():
    pdf = generate_resume_report(
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )

    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF")