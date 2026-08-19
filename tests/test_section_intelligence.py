from app.section_intelligence import (
    analyze_section,
    analyze_section_intelligence,
)


def test_missing_experience_section():

    resume = {
        "experience": "",
    }

    result = analyze_section(
        "experience",
        resume["experience"],
    )

    assert result["status"] == "missing"
    assert result["score"] == 0
    assert result["word_count"] == 0
    assert result["bullet_count"] == 0
    assert result["has_metrics"] is False


def test_strong_experience_section():

    experience = """
    • Developed a Python automation platform.
    • Improved processing time by 35%.
    • Supported 500+ users.
    • Reduced manual work by 20%.
    """

    result = analyze_section(
        "experience",
        experience,
    )

    assert result["status"] == "strong"
    assert result["bullet_count"] == 4
    assert result["has_metrics"] is True
    assert result["score"] >= 85


def test_experience_without_bullets():

    experience = """
    Developed Python applications and worked with SQL
    databases to improve internal business processes.
    """

    result = analyze_section(
        "experience",
        experience,
    )

    assert result["bullet_count"] == 0
    assert result["score"] < 70
    assert any(
        "bullet" in item.lower()
        for item in result["attention"]
    )


def test_experience_without_metrics():

    experience = """
    • Developed backend applications using Python.
    • Created database integrations.
    • Maintained internal tools for the team.
    """

    result = analyze_section(
        "experience",
        experience,
    )

    assert result["bullet_count"] == 3
    assert result["has_metrics"] is False

    assert any(
        "measurable"
        in item.lower()
        or "impact"
        in item.lower()
        for item in result["attention"]
    )


def test_summary_length():

    summary = (
        "Software developer with experience building "
        "Python applications and backend systems."
    )

    result = analyze_section(
        "summary",
        summary,
    )

    assert result["status"] in {
        "good",
        "strong",
    }

    assert result["word_count"] > 0


def test_summary_too_short():

    result = analyze_section(
        "summary",
        "Python developer.",
    )

    assert result["status"] in {
        "needs_attention",
        "weak",
    }

    assert any(
        "short"
        in item.lower()
        for item in result["attention"]
    )


def test_project_with_bullets():

    projects = """
    • Built a resume analyzer using Flask and Python.
    • Added SQLite persistence and PDF reporting.
    • Implemented ATS scoring and job matching.
    """

    result = analyze_section(
        "projects",
        projects,
    )

    assert result["bullet_count"] == 3
    assert result["score"] >= 70


def test_skills_section():

    skills = (
        "Python, Java, SQL, Flask, Django, "
        "Git, Docker, Linux"
    )

    result = analyze_section(
        "skills",
        skills,
    )

    assert result["status"] in {
        "good",
        "strong",
    }

    assert result["score"] >= 70


def test_complete_section_intelligence():

    resume = {
        "summary": (
            "Software developer with experience "
            "building backend applications."
        ),

        "skills": (
            "Python, SQL, Flask, Git, Docker"
        ),

        "experience": """
        • Built backend services.
        • Improved processing time by 30%.
        • Supported 500 users.
        """,

        "projects": """
        • Built a Flask resume analyzer.
        • Added SQLite history storage.
        • Generated PDF reports.
        """,

        "education": (
            "Bachelor of Science in Computer Science"
        ),

        "certifications": (
            "Python Programming Certificate"
        ),

        "achievements": """
        • Ranked in the top 10%.
        • Completed 20 programming projects.
        """,
    }

    result = analyze_section_intelligence(
        resume
    )

    assert result["max_score"] == 100

    assert result["section_count"] == 7

    assert result["total_sections"] == 7

    assert result["coverage_score"] == 100

    assert len(
        result["sections"]
    ) == 7

    assert result["missing_sections"] == []


def test_section_intelligence_detects_missing_sections():

    resume = {
        "summary": "Python developer.",
        "skills": "Python, SQL",
        "experience": "",
        "projects": "",
        "education": "",
        "certifications": "",
        "achievements": "",
    }

    result = analyze_section_intelligence(
        resume
    )

    assert (
        "experience"
        in result["missing_sections"]
    )

    assert (
        "projects"
        in result["missing_sections"]
    )

    assert (
        "education"
        in result["missing_sections"]
    )

    assert result["section_count"] == 2


def test_quality_result_contains_section_intelligence():

    from app.resume_quality import (
        analyze_resume_quality,
    )

    resume = {
        "summary": (
            "Software developer with experience "
            "building applications."
        ),

        "skills": (
            "Python, SQL, Flask"
        ),

        "experience": (
            "• Developed backend applications "
            "and improved processing by 20%."
        ),

        "projects": (
            "• Built a Python resume analyzer."
        ),

        "education": (
            "Bachelor of Science"
        ),

        "certifications": "",
        "achievements": "",
        "name": "Alex",
        "email": "alex@example.com",
        "phone": "1234567890",
        "other": "",
    }

    result = analyze_resume_quality(
        resume
    )

    assert (
        "section_intelligence"
        in result
    )

    intelligence = result[
        "section_intelligence"
    ]

    assert intelligence[
        "max_score"
    ] == 100

    assert isinstance(
        intelligence["sections"],
        dict,
    )