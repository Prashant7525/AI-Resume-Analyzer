from app.job_matcher import (
    calculate_match_score,
    extract_skills,
    generate_job_suggestions,
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