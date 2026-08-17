from app.ats_analyzer import (
    analyze_resume,
    calculate_completeness_score,
    check_contact_information,
    check_required_sections,
    generate_suggestions,
)


COMPLETE_RESUME = {
    "name": "Alex Johnson",
    "email": "alex@example.com",
    "phone": "+1 555 123 4567",
    "summary": "Software developer with application development experience.",
    "skills": "Python, Java, SQL, JavaScript",
    "projects": "Task Manager, Weather Dashboard",
    "education": "Bachelor of Science in Computer Science",
    "certifications": "Python Programming Certificate",
    "achievements": "Completed several software projects.",
    "experience": "Software Developer Intern",
    "other": "",
}


INCOMPLETE_RESUME = {
    "name": "",
    "email": "",
    "phone": "",
    "summary": "",
    "skills": "",
    "projects": "",
    "education": "",
    "certifications": "",
    "achievements": "",
    "experience": "",
    "other": "",
}


def test_complete_resume_gets_full_completeness_score():
    score = calculate_completeness_score(COMPLETE_RESUME)

    assert score == 90


def test_contact_information_check():
    result = check_contact_information(COMPLETE_RESUME)

    assert result["email"] is True
    assert result["phone"] is True
    assert result["passed"] is True


def test_required_sections_check():
    result = check_required_sections(COMPLETE_RESUME)

    assert result["summary"] is True
    assert result["skills"] is True
    assert result["education"] is True
    assert result["projects"] is True
    assert result["experience"] is True


def test_incomplete_resume_generates_suggestions():
    suggestions = generate_suggestions(INCOMPLETE_RESUME)

    assert "Add your full name." in suggestions
    assert "Add a professional email address." in suggestions
    assert "Add a phone number." in suggestions
    assert "Add a concise professional summary." in suggestions
    assert "Add a technical skills section." in suggestions


def test_analyze_resume():
    result = analyze_resume(COMPLETE_RESUME)

    assert result["score"] == 90
    assert result["contact"]["passed"] is True
    assert result["sections"]["skills"] is True
    assert result["sections"]["projects"] is True
    assert result["suggestions"] == []