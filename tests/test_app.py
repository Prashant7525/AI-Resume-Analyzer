import io

import pytest

from app.main import (
    app,
    sanitize_text,
)


SAMPLE_RESUME = """
ALEX JOHNSON

PROFESSIONAL SUMMARY
Software developer with experience in application development.

TECHNICAL SKILLS
Python, Java, SQL, JavaScript

EXPERIENCE
Software Developer
Developed applications using Python and SQL.

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


# ============================================================
# TEST CLIENT
# ============================================================

@pytest.fixture
def client():
    """
    Create a Flask test client.
    """

    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )

    with app.test_client() as client:
        yield client


# ============================================================
# RESUME PARSER TESTS
# ============================================================

def test_clean_text():

    from app.resume_parser import clean_text

    text = "Hello   World\r\n\r\nPython"

    result = clean_text(
        text
    )

    assert result == "Hello World\nPython"


def test_extract_name():

    from app.resume_parser import extract_name

    result = extract_name(
        SAMPLE_RESUME
    )

    assert result == "ALEX JOHNSON"


def test_extract_email():

    from app.resume_parser import extract_email

    text = "Contact: example@gmail.com"

    assert (
        extract_email(text)
        == "example@gmail.com"
    )


def test_parse_sections():

    from app.resume_parser import parse_sections

    sections = parse_sections(
        SAMPLE_RESUME
    )

    assert (
        "Software developer"
        in sections["summary"]
    )

    assert (
        "Python, Java, SQL"
        in sections["skills"]
    )

    assert (
        "Task Manager"
        in sections["projects"]
    )

    assert (
        "Bachelor of Science"
        in sections["education"]
    )

    assert (
        "Python Programming Certificate"
        in sections["certifications"]
    )

    assert (
        "Completed several programming projects"
        in sections["achievements"]
    )


def test_parse_resume():

    from app.resume_parser import parse_resume

    resume = parse_resume(
        SAMPLE_RESUME
    )

    assert (
        resume["name"]
        == "ALEX JOHNSON"
    )

    assert resume["summary"] != ""

    assert resume["skills"] != ""

    assert resume["projects"] != ""

    assert resume["education"] != ""

    assert resume["certifications"] != ""

    assert resume["achievements"] != ""


# ============================================================
# INPUT SANITIZATION TESTS
# ============================================================

def test_sanitize_text_removes_control_characters():

    value = (
        "Hello\x00World"
        "\x01Python"
    )

    result = sanitize_text(
        value
    )

    assert result == (
        "HelloWorldPython"
    )


def test_sanitize_text_normalizes_line_endings():

    value = (
        "Hello\r\n"
        "World\r"
        "Python"
    )

    result = sanitize_text(
        value
    )

    assert result == (
        "Hello\n"
        "World\n"
        "Python"
    )


def test_sanitize_text_strips_trailing_whitespace():

    value = (
        "Hello   \n"
        "World\t\n"
    )

    result = sanitize_text(
        value
    )

    assert result == (
        "Hello\n"
        "World"
    )


def test_sanitize_text_limits_length():

    value = "A" * 25000

    result = sanitize_text(
        value,
        max_length=20000,
    )

    assert len(result) == 20000


def test_sanitize_text_handles_non_string():

    assert (
        sanitize_text(None)
        == ""
    )

    assert (
        sanitize_text(12345)
        == ""
    )


# ============================================================
# BASIC FLASK ROUTES
# ============================================================

def test_home_route(
    client,
):

    response = client.get(
        "/"
    )

    assert response.status_code == 200

    assert (
        b"AI Resume Analyzer"
        in response.data
    )

    assert (
        b"Analyze Your Resume"
        in response.data
    )


def test_history_route(
    client,
):

    response = client.get(
        "/history"
    )

    assert response.status_code == 200

    assert (
        b"Analysis History"
        in response.data
        or b"History"
        in response.data
    )


def test_privacy_route(
    client,
):

    response = client.get(
        "/privacy"
    )

    assert response.status_code == 200

    assert (
        b"Privacy"
        in response.data
    )


def test_terms_route(
    client,
):

    response = client.get(
        "/terms"
    )

    assert response.status_code == 200

    assert (
        b"Terms"
        in response.data
    )


def test_favicon_route(
    client,
):

    response = client.get(
        "/favicon.ico"
    )

    assert response.status_code in {
        200,
        204,
    }


# ============================================================
# UPLOAD VALIDATION
# ============================================================

def test_upload_without_resume(
    client,
):

    response = client.post(

        "/",

        data={
            "job_description": "",
        },
    )

    assert response.status_code == 200

    assert (
        b"Please upload a PDF resume."
        in response.data
    )


def test_upload_empty_filename(
    client,
):

    response = client.post(

        "/",

        data={
            "resume": (
                io.BytesIO(b""),
                "",
            ),
        },

        content_type="multipart/form-data",
    )

    assert response.status_code == 200

    assert (
        b"Please upload a PDF resume."
        in response.data
    )


def test_upload_unsupported_file(
    client,
):

    response = client.post(

        "/",

        data={
            "resume": (
                io.BytesIO(
                    b"not a pdf"
                ),
                "resume.txt",
            ),
        },

        content_type="multipart/form-data",
    )

    assert response.status_code == 200

    assert (
        b"Only PDF resume files are supported."
        in response.data
    )


def test_upload_invalid_pdf(
    client,
):

    response = client.post(

        "/",

        data={
            "resume": (
                io.BytesIO(
                    b"This is not a valid PDF"
                ),
                "resume.pdf",
            ),
        },

        content_type="multipart/form-data",
    )

    assert response.status_code == 200

    assert (
        b"Unable to process the PDF file."
        in response.data

        or

        b"does not contain readable text"
        in response.data
    )


def test_empty_pdf(
    client,
):

    response = client.post(

        "/",

        data={
            "resume": (
                io.BytesIO(b""),
                "empty.pdf",
            ),
        },

        content_type="multipart/form-data",
    )

    assert response.status_code == 200

    assert (
        b"Unable to process the PDF file."
        in response.data

        or

        b"does not contain readable text"
        in response.data

        or

        b"Please upload a PDF resume."
        in response.data
    )


# ============================================================
# JOB DESCRIPTION
# ============================================================

def test_missing_job_description(
    client,
):

    response = client.get(
        "/"
    )

    assert response.status_code == 200

    assert (
        b"Job Description"
        in response.data
    )

    assert (
        b"optional"
        in response.data.lower()
    )


def test_job_description_form_rendering(
    client,
):

    response = client.get(
        "/"
    )

    assert response.status_code == 200

    assert (
        b'name="job_description"'
        in response.data
    )


# ============================================================
# THEME-INDEPENDENT RENDERING
# ============================================================

def test_light_theme_rendering(
    client,
):

    response = client.get(
        "/"
    )

    assert response.status_code == 200

    assert (
        b"themeToggle"
        in response.data
    )

    assert (
        b"resume-analyzer-theme"
        in response.data
    )


def test_dark_theme_script_present(
    client,
):

    response = client.get(
        "/"
    )

    assert response.status_code == 200

    assert (
        b"data-theme"
        in response.data
        or b"dark"
        in response.data
    )


# ============================================================
# HISTORY ROUTE SAFETY
# ============================================================

def test_missing_history_analysis(
    client,
):

    response = client.get(
        "/history/999999999"
    )

    assert response.status_code == 404

    assert (
        b"Analysis not found."
        in response.data
    )


def test_delete_missing_history_analysis(
    client,
):

    response = client.post(

        "/history/999999999/delete",

        follow_redirects=False,
    )

    assert response.status_code in {
        302,
        303,
        404,
    }

    if response.status_code in {
        302,
        303,
    }:

        assert (
            "/history"
            in response.headers["Location"]
        )


# ============================================================
# REPORT ROUTE VALIDATION
# ============================================================

def test_report_without_resume(
    client,
):

    response = client.post(

        "/download-report",

        data={
            "job_description": "",
        },
    )

    assert response.status_code == 200

    assert (
        b"Please upload a PDF resume."
        in response.data
    )


def test_report_with_unsupported_file(
    client,
):

    response = client.post(

        "/download-report",

        data={

            "resume": (
                io.BytesIO(
                    b"not a pdf"
                ),
                "resume.txt",
            ),

            "job_description": "",
        },

        content_type="multipart/form-data",
    )

    assert response.status_code == 200

    assert (
        b"Only PDF resume files are supported."
        in response.data
    )


def test_report_with_invalid_pdf(
    client,
):

    response = client.post(

        "/download-report",

        data={

            "resume": (
                io.BytesIO(
                    b"invalid pdf data"
                ),
                "resume.pdf",
            ),

            "job_description": "",
        },

        content_type="multipart/form-data",
    )

    assert response.status_code == 200

    assert (
        b"Unable to generate the PDF report."
        in response.data

        or

        b"Unable to process the PDF file."
        in response.data

        or

        b"does not contain readable text"
        in response.data
    )


# ============================================================
# CONTENT / TEMPLATE TESTS
# ============================================================

def test_homepage_contains_footer_links(
    client,
):

    response = client.get(
        "/"
    )

    assert response.status_code == 200

    assert (
        b"GitHub"
        in response.data
    )

    assert (
        b"LinkedIn"
        in response.data
    )

    assert (
        b"Privacy"
        in response.data
    )

    assert (
        b"Terms"
        in response.data
    )


def test_homepage_contains_history_navigation(
    client,
):

    response = client.get(
        "/"
    )

    assert response.status_code == 200

    assert (
        b"history"
        in response.data.lower()
    )


def test_homepage_contains_dark_mode_controls(
    client,
):

    response = client.get(
        "/"
    )

    assert response.status_code == 200

    assert (
        b"themeToggle"
        in response.data
    )


# ============================================================
# HTTP METHOD SAFETY
# ============================================================

def test_history_does_not_accept_post(
    client,
):

    response = client.post(
        "/history"
    )

    assert response.status_code == 405


def test_privacy_does_not_accept_post(
    client,
):

    response = client.post(
        "/privacy"
    )

    assert response.status_code == 405


def test_terms_does_not_accept_post(
    client,
):

    response = client.post(
        "/terms"
    )

    assert response.status_code == 405

# ============================================================
# CSRF PROTECTION TESTS
# ============================================================

def test_homepage_contains_csrf_token(client):
    """
    The homepage should render a CSRF token for POST forms.
    """

    response = client.get("/")

    assert response.status_code == 200

    assert (
        b'name="csrf_token"'
        in response.data
    )


def test_history_contains_csrf_token(client):
    """
    The history page should render a CSRF token for
    the delete POST form.
    """

    response = client.get("/history")

    assert response.status_code == 200

    assert (
        b'name="csrf_token"'
        in response.data
    )


def test_csrf_rejects_missing_token():
    """
    CSRF protection should reject a POST request without
    a valid CSRF token.
    """

    app.config.update(
        TESTING=False,
        WTF_CSRF_ENABLED=True,
    )

    try:
        with app.test_client() as test_client:

            response = test_client.post(
                "/",
                data={
                    "job_description": "",
                },
            )

            assert response.status_code == 400

    finally:

        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
        )