from app.job_matcher import (
    calculate_keyword_coverage,
    calculate_match_score,
    extract_keywords,
    extract_skills,
    generate_job_suggestions,
    generate_keyword_suggestions,
    match_resume_to_job,
    normalize_text,
    resume_to_text,
)


RESUME = {
    "name": "Alex Johnson",
    "email": "alex@example.com",
    "phone": "+1 555 123 4567",
    "summary": "Software developer with Python experience.",
    "skills": "Python, SQL, JavaScript, Git",
    "experience": "Developed web applications using Python and Flask.",
    "projects": "Created a React dashboard.",
    "education": "Bachelor of Science in Computer Science",
    "certifications": "",
    "achievements": "",
    "other": "",
}


JOB_DESCRIPTION = """
We are looking for a software developer with experience in
Python, SQL, JavaScript, Git, Docker, AWS, and REST APIs.
"""


def test_normalize_text():
    result = normalize_text("  Python   Developer ")

    assert result == "python developer"


def test_extract_skills():
    text = """
    Python, SQL, JavaScript, Docker and AWS experience.
    """

    skills = extract_skills(text)

    assert "python" in skills
    assert "sql" in skills
    assert "javascript" in skills
    assert "docker" in skills
    assert "aws" in skills


def test_resume_to_text():
    text = resume_to_text(RESUME)

    assert "Python experience" in text
    assert "JavaScript" in text
    assert "React dashboard" in text


def test_calculate_match_score():
    resume_skills = {
        "python",
        "sql",
        "javascript",
        "git",
    }

    job_skills = {
        "python",
        "sql",
        "javascript",
        "git",
        "docker",
        "aws",
    }

    assert calculate_match_score(
        resume_skills,
        job_skills,
    ) == 67


def test_generate_job_suggestions():
    suggestions = generate_job_suggestions(
        {"python", "sql"},
        {"docker", "aws"},
    )

    assert len(suggestions) == 2
    assert "docker" in suggestions[0].lower()
    assert "python" in suggestions[1].lower()


def test_match_resume_to_job():
    result = match_resume_to_job(
        RESUME,
        JOB_DESCRIPTION,
    )

    assert result["score"] == 57

    assert "python" in result["matched_skills"]
    assert "sql" in result["matched_skills"]
    assert "javascript" in result["matched_skills"]
    assert "git" in result["matched_skills"]

    assert "docker" in result["missing_skills"]
    assert "aws" in result["missing_skills"]
    assert "rest api" in result["missing_skills"]


# ---------------------------------------------------------
# v1.7 Keyword Intelligence Tests
# ---------------------------------------------------------


def test_extract_keywords():
    text = """
    We need experience in backend development,
    REST APIs, databases, testing and deployment.
    """

    keywords = extract_keywords(text)

    assert "backend" in keywords
    assert "api" in keywords
    assert "database" in keywords
    assert "testing" in keywords
    assert "deployment" in keywords


def test_calculate_keyword_coverage():
    resume_keywords = {
        "backend",
        "database",
        "testing",
    }

    job_keywords = {
        "backend",
        "database",
        "testing",
        "deployment",
    }

    assert calculate_keyword_coverage(
        resume_keywords,
        job_keywords,
    ) == 75


def test_generate_keyword_suggestions():
    suggestions = generate_keyword_suggestions(
        {"backend", "testing"},
        {"deployment", "cloud"},
    )

    assert len(suggestions) == 2
    assert "deployment" in suggestions[0].lower()
    assert "backend" in suggestions[1].lower()


def test_match_resume_to_job_includes_keyword_analysis():
    result = match_resume_to_job(
        RESUME,
        JOB_DESCRIPTION,
    )

    assert "resume_keywords" in result
    assert "job_keywords" in result
    assert "matched_keywords" in result
    assert "missing_keywords" in result
    assert "keyword_coverage" in result
    assert "keyword_suggestions" in result


def test_keyword_analysis_handles_empty_job_description():
    result = match_resume_to_job(
        RESUME,
        "",
    )

    assert result["keyword_coverage"] == 0
    assert result["job_keywords"] == []
    assert result["matched_keywords"] == []
    assert result["missing_keywords"] == []