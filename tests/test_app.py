from app.resume_parser import (
    clean_text,
    extract_email,
    extract_name,
    parse_resume,
    parse_sections,
)


SAMPLE_RESUME = """
ALEX JOHNSON

PROFESSIONAL SUMMARY
Software developer with experience in application development.

TECHNICAL SKILLS
Python, Java, SQL, JavaScript

PROJECTS
Task Manager
Weather Dashboard

EDUCATION
Bachelor of Science in Computer Science

CERTIFICATIONS
Python Programming Certificate

ACHIEVEMENTS
Completed several programming projects.

CODING PROFILES
ExampleProfile
"""


def test_clean_text():
    text = "Hello   World\r\n\r\nPython"

    result = clean_text(text)

    assert result == "Hello World\nPython"


def test_extract_name():
    result = extract_name(SAMPLE_RESUME)

    assert result == "ALEX JOHNSON"


def test_extract_email():
    text = "Contact: example@gmail.com"

    assert extract_email(text) == "example@gmail.com"


def test_parse_sections():
    sections = parse_sections(SAMPLE_RESUME)

    assert "Software developer" in sections["summary"]
    assert "Python, Java, SQL" in sections["skills"]
    assert "Task Manager" in sections["projects"]
    assert "Bachelor of Science" in sections["education"]
    assert "Python Programming Certificate" in sections["certifications"]
    assert "Completed several programming projects" in sections["achievements"]


def test_parse_resume():
    resume = parse_resume(SAMPLE_RESUME)

    assert resume["name"] == "ALEX JOHNSON"
    assert resume["summary"] != ""
    assert resume["skills"] != ""
    assert resume["projects"] != ""
    assert resume["education"] != ""
    assert resume["certifications"] != ""
    assert resume["achievements"] != ""