from app.resume_improvements import (
    analyze_resume_improvements,
    check_achievements,
    check_contact_information,
    check_experience,
    check_projects,
    check_skills,
    check_summary,
    generate_improvements,
)


RESUME = {
    "name": "Alex Johnson",
    "email": "alex@example.com",
    "phone": "+1 555 123 4567",

    "summary": (
        "Software developer with experience building web applications "
        "and backend services using Python, SQL, JavaScript, and modern "
        "development tools while delivering reliable and maintainable solutions."

    ),

    "skills": (
        "Python, Java, SQL, JavaScript, Git, Docker"
    ),

    "experience": (
        "• Developed web applications using Python.\n"
        "• Improved application response time by 30%.\n"
        "• Worked with SQL databases."
    ),

    "projects": (
        "• Built a task management application.\n"
        "• Created a weather dashboard."
    ),

    "education": (
        "Bachelor of Science in Computer Science"
    ),

    "certifications": (
        "Python Programming Certificate"
    ),

    "achievements": (
        "• Increased project performance by 25%.\n"
        "• Completed 5 software projects."
    ),

    "other": "",
}


INCOMPLETE_RESUME = {
    "name": "",
    "email": "",
    "phone": "",
    "summary": "",
    "skills": "",
    "experience": "",
    "projects": "",
    "education": "",
    "certifications": "",
    "achievements": "",
    "other": "",
}


def test_check_summary_good():
    result = check_summary(RESUME)

    assert result["status"] == "good"
    assert result["word_count"] > 20


def test_check_summary_missing():
    result = check_summary(INCOMPLETE_RESUME)

    assert result["status"] == "missing"
    assert "summary" in result["recommendation"].lower()


def test_check_summary_too_short():
    resume = {
        "summary": "Python developer.",
    }

    result = check_summary(resume)

    assert result["status"] == "too_short"


def test_check_experience_good():
    result = check_experience(RESUME)

    assert result["status"] == "good"
    assert result["bullet_count"] == 3


def test_check_experience_missing():
    result = check_experience(INCOMPLETE_RESUME)

    assert result["status"] == "missing"


def test_check_experience_without_bullets():
    resume = {
        "experience": (
            "Developed applications using Python and SQL."
        ),
    }

    result = check_experience(resume)

    assert result["status"] == "no_bullets"


def test_check_projects_good():
    result = check_projects(RESUME)

    assert result["status"] == "good"
    assert result["bullet_count"] == 2


def test_check_projects_missing():
    result = check_projects(INCOMPLETE_RESUME)

    assert result["status"] == "missing"


def test_check_skills_good():
    result = check_skills(RESUME)

    assert result["status"] == "good"


def test_check_skills_missing():
    result = check_skills(INCOMPLETE_RESUME)

    assert result["status"] == "missing"


def test_check_achievements_good():
    result = check_achievements(RESUME)

    assert result["status"] == "good"
    assert result["bullet_count"] == 2


def test_check_achievements_missing():
    result = check_achievements(INCOMPLETE_RESUME)

    assert result["status"] == "missing"


def test_check_achievements_without_metrics():
    resume = {
        "achievements": (
            "• Completed several software projects.\n"
            "• Helped improve the development process."
        ),
    }

    result = check_achievements(resume)

    assert result["status"] == "no_metrics"


def test_check_contact_information_complete():
    result = check_contact_information(RESUME)

    assert result["status"] == "complete"
    assert result["missing"] == []


def test_check_contact_information_incomplete():
    result = check_contact_information(INCOMPLETE_RESUME)

    assert result["status"] == "incomplete"
    assert "name" in result["missing"]
    assert "email" in result["missing"]
    assert "phone" in result["missing"]


def test_generate_improvements_for_good_resume():
    improvements = generate_improvements(RESUME)

    assert improvements == []


def test_generate_improvements_for_incomplete_resume():
    improvements = generate_improvements(INCOMPLETE_RESUME)

    assert len(improvements) > 0

    text = " ".join(improvements).lower()

    assert "contact" in text or "name" in text
    assert "summary" in text


def test_analyze_resume_improvements():
    result = analyze_resume_improvements(RESUME)

    assert result["score"] == 100
    assert result["completed"] == 6
    assert result["total"] == 6
    assert result["improvements"] == []


def test_analyze_incomplete_resume():
    result = analyze_resume_improvements(
        INCOMPLETE_RESUME
    )

    assert result["score"] == 0
    assert result["completed"] == 0
    assert result["total"] == 6
    assert len(result["improvements"]) > 0
