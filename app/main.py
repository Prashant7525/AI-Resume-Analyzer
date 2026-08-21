"""
Main Flask application for the AI Resume Analyzer.

V3.1
- Resume analysis
- ATS analysis
- Resume quality analysis
- Resume improvement analysis
- Job matching
- Keyword intelligence
- Dashboard
- Score explanations
- Analytics
- PDF report download
- Analysis history
- Saved analysis viewing
- Analysis deletion
- Privacy page
- Terms page
- Favicon support
- Secure upload validation
- Input sanitization
- CSRF protection
- Production configuration
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pymupdf

from flask import (
    Flask,
    render_template,
    request,
    send_file,
    send_from_directory,
    redirect,
    url_for,
)

from flask_wtf.csrf import CSRFProtect


from app.analytics import build_analytics
from app.ats_analyzer import analyze_resume
from app.dashboard import build_dashboard_result
from app.database import (
    delete_analysis,
    get_analysis,
    get_analysis_history,
    init_database,
    save_analysis,
)
from app.job_matcher import match_resume_to_job
from app.report_generator import generate_resume_report
from app.resume_improvements import (
    analyze_resume_improvements,
)
from app.resume_parser import (
    extract_text_from_pdf,
    parse_resume,
)
from app.resume_quality import analyze_resume_quality
from app.score_explanation import build_score_explanations

from app.ai.prompts import (
    BULLET_REWRITE_SYSTEM_PROMPT,
    EXPERIENCE_REWRITE_SYSTEM_PROMPT,
    PROJECT_REWRITE_SYSTEM_PROMPT,
    SUMMARY_REWRITE_SYSTEM_PROMPT,
    build_bullet_rewrite_prompt,
    build_experience_rewrite_prompt,
    build_project_rewrite_prompt,
    build_summary_rewrite_prompt,
)
from app.ai.provider import (
    AIProviderError,
    generate_text,
    is_ai_configured,
)

# ============================================================
# APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# ENVIRONMENT HELPERS
# ============================================================

def _env_bool(
    name: str,
    default: bool = False,
) -> bool:
    """
    Read a boolean environment variable safely.

    Accepted true values:
        1, true, yes, on

    Accepted false values:
        0, false, no, off
    """

    value = os.environ.get(
        name
    )

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _env_int(
    name: str,
    default: int,
) -> int:
    """
    Read an integer environment variable safely.
    """

    value = os.environ.get(
        name
    )

    if value is None:
        return default

    try:
        return int(value)

    except ValueError:

        return default


# ============================================================
# ENVIRONMENT / PRODUCTION CONFIGURATION
# ============================================================

APP_ENV = os.environ.get(
    "APP_ENV",
    "development",
).strip().lower()


IS_PRODUCTION = (
    APP_ENV == "production"
)


# ------------------------------------------------------------
# SECRET KEY
# ------------------------------------------------------------

SECRET_KEY = os.environ.get(
    "SECRET_KEY"
)

if IS_PRODUCTION and not SECRET_KEY:

    raise RuntimeError(
        "SECRET_KEY must be configured "
        "when APP_ENV=production."
    )


if not SECRET_KEY:

    SECRET_KEY = (
        "dev-only-change-this-secret-key"
    )


app.config["SECRET_KEY"] = (
    SECRET_KEY
)


# ------------------------------------------------------------
# File upload limit
# ------------------------------------------------------------

app.config["MAX_CONTENT_LENGTH"] = (
    5 * 1024 * 1024
)


# ------------------------------------------------------------
# CSRF
# ------------------------------------------------------------

app.config["WTF_CSRF_ENABLED"] = True

app.config["WTF_CSRF_TIME_LIMIT"] = 3600


# ------------------------------------------------------------
# Session cookie security
# ------------------------------------------------------------

app.config["SESSION_COOKIE_HTTPONLY"] = True

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["SESSION_COOKIE_SECURE"] = (
    IS_PRODUCTION
)


# ------------------------------------------------------------
# Debug / testing
# ------------------------------------------------------------

app.config["DEBUG"] = _env_bool(
    "FLASK_DEBUG",
    default=not IS_PRODUCTION,
)

app.config["TESTING"] = _env_bool(
    "FLASK_TESTING",
    default=False,
)


# ------------------------------------------------------------
# Host / port
# ------------------------------------------------------------

APP_HOST = os.environ.get(
    "APP_HOST",
    "127.0.0.1",
)

APP_PORT = _env_int(
    "APP_PORT",
    5000,
)


# ------------------------------------------------------------
# Application limits
# ------------------------------------------------------------

ALLOWED_EXTENSIONS = {
    "pdf"
}

MAX_JOB_DESCRIPTION_LENGTH = 20000


# ============================================================
# CSRF INITIALIZATION
# ============================================================

csrf = CSRFProtect(
    app
)

# ============================================================
# GLOBAL HTTP ERROR HANDLERS
# ============================================================

@app.errorhandler(400)
def handle_bad_request(error):
    """Return a safe response for malformed requests."""

    return render_template(
        "error.html",
        error_message=(
            "The request could not be processed."
        ),
    ), 400


@app.errorhandler(403)
def handle_forbidden(error):
    """Return a safe response for forbidden requests."""

    return render_template(
        "error.html",
        error_message=(
            "You do not have permission to access this page."
        ),
    ), 403


@app.errorhandler(404)
def handle_not_found(error):
    """Return a safe response for missing pages."""

    return render_template(
        "error.html",
        error_message=(
            "The page you requested was not found."
        ),
    ), 404


@app.errorhandler(413)
def handle_file_too_large(error):
    """Return a safe response when an upload exceeds the limit."""

    return render_template(
        "error.html",
        error_message=(
            "The uploaded file is too large. "
            "Please upload a PDF smaller than 5 MB."
        ),
    ), 413


@app.errorhandler(500)
def handle_internal_error(error):
    """Return a generic response for unexpected server errors."""

    app.logger.exception(
        "Unhandled internal server error."
    )

    return render_template(
        "error.html",
        error_message=(
            "Something went wrong while processing your request."
        ),
    ), 500

# ============================================================
# DATABASE INITIALIZATION
# ============================================================

init_database()


# ============================================================
# TEMPLATE FILTERS
# ============================================================

@app.template_filter(
    "format_history_date"
)
def format_history_date(value):
    """
    Format an ISO timestamp for the analysis history page.
    """

    if not value:

        return "Unknown date"

    try:

        timestamp = datetime.fromisoformat(
            str(value).replace(
                "Z",
                "+00:00",
            )
        )

        return timestamp.strftime(
            "%d %b %Y · %I:%M %p"
        )

    except (
        ValueError,
        TypeError,
    ):

        return str(value)


# ============================================================
# INPUT SANITIZATION
# ============================================================

def sanitize_text(
    value: str,
    max_length: int = 20000,
) -> str:
    """
    Normalize user-provided text without changing its meaning.

    The sanitizer:

    - Rejects non-string values.
    - Removes null/control characters.
    - Normalizes line endings.
    - Removes trailing whitespace from individual lines.
    - Removes surrounding whitespace.
    - Limits the final length.
    """

    if not isinstance(
        value,
        str,
    ):

        return ""

    # Remove the null character explicitly.
    value = value.replace(
        "\x00",
        "",
    )

    # Normalize line endings.
    value = value.replace(
        "\r\n",
        "\n",
    )

    value = value.replace(
        "\r",
        "\n",
    )

    # Remove control characters while preserving
    # tabs and newlines.
    value = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]",
        "",
        value,
    )

    # Remove trailing whitespace from every line.
    lines = [
        line.rstrip()
        for line in value.split("\n")
    ]

    value = "\n".join(
        lines
    ).strip()

    # Enforce the maximum length.
    return value[:max_length]


# ============================================================
# FILE VALIDATION
# ============================================================

def allowed_file(
    filename: str,
) -> bool:
    """
    Return True when the uploaded file is an allowed PDF.
    """

    if not filename:

        return False

    return (
        "."
        in filename
        and filename.rsplit(
            ".",
            1,
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


def is_valid_pdf(
    file,
) -> bool:
    """
    Validate that the uploaded file is an actual readable PDF.

    The filename extension alone is not trusted.
    """

    if file is None:

        return False

    try:

        file.stream.seek(
            0
        )

        pdf_bytes = file.stream.read()

        file.stream.seek(
            0
        )

        # Empty upload.
        if not pdf_bytes:

            return False

        # PDF signature check.
        if not pdf_bytes.startswith(
            b"%PDF-"
        ):

            return False

        # Structural PDF validation.
        document = pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf",
        )

        try:

            return document.page_count > 0

        finally:

            document.close()

    except Exception as exc:

        app.logger.warning(
            "PDF validation failed: %s",
            exc,
        )

        return False

    finally:

        try:

            file.stream.seek(
                0
            )

        except Exception:

            pass


# ============================================================
# RESUME ANALYSIS
# ============================================================

def _analyze_uploaded_resume(
    file,
    job_description: str = "",
) -> dict:
    """
    Run the complete resume analysis pipeline.

    Returns:
        Dictionary containing all analysis results.
    """

    # --------------------------------------------------------
    # Extract PDF text
    # --------------------------------------------------------

    try:

        extracted_text = extract_text_from_pdf(
            file
        )

    except Exception as exc:

        app.logger.exception(
            "PDF text extraction failed: %s",
            exc,
        )

        raise ValueError(
            "Unable to process the PDF file."
        ) from exc

    if (
        not extracted_text
        or not extracted_text.strip()
    ):

        raise ValueError(
            "The PDF does not contain readable text."
        )

    # --------------------------------------------------------
    # Resume parsing
    # --------------------------------------------------------

    try:

        resume = parse_resume(
            extracted_text
        )

    except Exception as exc:

        app.logger.exception(
            "Resume parsing failed: %s",
            exc,
        )

        raise ValueError(
            "Unable to process the PDF file."
        ) from exc

    # --------------------------------------------------------
    # ATS analysis
    # --------------------------------------------------------

    ats_result = analyze_resume(
        resume
    )

    # --------------------------------------------------------
    # Resume quality
    # --------------------------------------------------------

    quality_result = analyze_resume_quality(
        resume
    )

    # --------------------------------------------------------
    # Resume improvement analysis
    # --------------------------------------------------------

    improvement_result = (
        analyze_resume_improvements(
            resume
        )
    )

    # --------------------------------------------------------
    # Job matching
    # --------------------------------------------------------

    job_result = None

    if job_description:

        job_result = match_resume_to_job(
            resume,
            job_description,
        )

    # --------------------------------------------------------
    # Unified dashboard
    # --------------------------------------------------------

    dashboard_result = build_dashboard_result(
        resume,
        ats_result,
        quality_result,
        job_result,
        improvement_result,
    )

    # --------------------------------------------------------
    # V3.1 score explanations
    # --------------------------------------------------------

    score_explanations = (
        build_score_explanations(

            dashboard_result,

            ats_result,

            quality_result,

            job_result,

            improvement_result,
        )
    )

    # --------------------------------------------------------
    # Analytics
    # --------------------------------------------------------

    analytics_result = build_analytics(
        ats_result,
        quality_result,
        improvement_result,
        job_result,
    )

    return {

        "resume": resume,

        "ats_result": ats_result,

        "quality_result": quality_result,

        "improvement_result":
            improvement_result,

        "job_result": job_result,

        "dashboard_result":
            dashboard_result,

        "score_explanations":
            score_explanations,

        "analytics_result":
            analytics_result,

        "extracted_text":
            extracted_text,
    }


# ============================================================
# SAVE ANALYSIS
# ============================================================

def _save_analysis_results(
    results: dict,
    job_description: str,
) -> int:
    """
    Save completed analysis results to SQLite.

    Returns:
        Newly created analysis ID.
    """

    return save_analysis(

        resume=results.get(
            "resume"
        ),

        ats_result=results.get(
            "ats_result"
        ),

        quality_result=results.get(
            "quality_result"
        ),

        improvement_result=results.get(
            "improvement_result"
        ),

        job_result=results.get(
            "job_result"
        ),

        dashboard_result=results.get(
            "dashboard_result"
        ),

        analytics_result=results.get(
            "analytics_result"
        ),

        job_description=job_description,
    )


# ============================================================
# COMMON ERROR RENDERING
# ============================================================

def _render_index_error(
    error: str,
    job_description: str = "",
):
    """
    Render the main page with a user-facing error message.
    """

    return render_template(

        "index.html",

        resume=None,

        ats_result=None,

        quality_result=None,

        improvement_result=None,

        job_result=None,

        dashboard_result=None,

        score_explanations=None,

        analytics_result=None,

        extracted_text=None,

        error=error,

        job_description=job_description,

        history_view=False,

        analysis_id=None,
    )


# ============================================================
# MAIN PAGE
# ============================================================

@app.route(
    "/",
    methods=["GET", "POST"],
)
def index():
    """
    Render the main resume analyzer page.
    """

    resume = None

    ats_result = None

    quality_result = None

    improvement_result = None

    job_result = None

    dashboard_result = None

    score_explanations = None

    analytics_result = None

    extracted_text = None

    error = None

    job_description = ""

    if request.method == "POST":

        file = request.files.get(
            "resume"
        )

        # ----------------------------------------------------
        # Sanitize job description.
        # ----------------------------------------------------

        job_description = sanitize_text(

            request.form.get(
                "job_description",
                "",
            ),

            max_length=
                MAX_JOB_DESCRIPTION_LENGTH,
        )

        try:

            # ------------------------------------------------
            # Validate upload existence.
            # ------------------------------------------------

            if (
                file is None
                or not file.filename
            ):

                raise ValueError(
                    "Please upload a PDF resume."
                )

            # ------------------------------------------------
            # Validate extension.
            # ------------------------------------------------

            if not allowed_file(
                file.filename
            ):

                raise ValueError(
                    "Only PDF resume files are supported."
                )

            # ------------------------------------------------
            # Validate actual PDF contents.
            # ------------------------------------------------

            if not is_valid_pdf(
                file
            ):

                raise ValueError(
                    "Unable to process the PDF file."
                )

            # ------------------------------------------------
            # Analyze resume.
            # ------------------------------------------------

            results = _analyze_uploaded_resume(
                file,
                job_description,
            )

            resume = results[
                "resume"
            ]

            ats_result = results[
                "ats_result"
            ]

            quality_result = results[
                "quality_result"
            ]

            improvement_result = results[
                "improvement_result"
            ]

            job_result = results[
                "job_result"
            ]

            dashboard_result = results[
                "dashboard_result"
            ]

            score_explanations = results[
                "score_explanations"
            ]

            analytics_result = results[
                "analytics_result"
            ]

            extracted_text = results[
                "extracted_text"
            ]

            # ------------------------------------------------
            # Save analysis.
            # ------------------------------------------------

            _save_analysis_results(
                results,
                job_description,
            )

        except ValueError as exc:

            error = str(
                exc
            )

        except Exception as exc:

            app.logger.exception(
                "Unable to process resume: %s",
                exc,
            )

            error = (
                "Unable to process the PDF file. "
                "Please make sure it is a valid "
                "text-based PDF."
            )

    return render_template(

        "index.html",

        resume=resume,

        ats_result=ats_result,

        quality_result=quality_result,

        improvement_result=
            improvement_result,

        job_result=job_result,

        dashboard_result=
            dashboard_result,

        score_explanations=
            score_explanations,

        analytics_result=
            analytics_result,

        extracted_text=
            extracted_text,

        error=error,

        job_description=
            job_description,

        history_view=False,

        analysis_id=None,
    )


# ============================================================
# HISTORY PAGE
# ============================================================

@app.route(
    "/history",
    methods=["GET"],
)
def history():
    """
    Display saved resume analyses.
    """

    analyses = get_analysis_history(
        limit=50
    )

    return render_template(

        "history.html",

        analyses=analyses,
    )


# ============================================================
# VIEW SAVED ANALYSIS
# ============================================================

@app.route(
    "/history/<int:analysis_id>",
    methods=["GET"],
)
def view_history(
    analysis_id: int,
):
    """
    Display one saved analysis.

    Score explanations are generated dynamically so
    older saved analyses also receive the V3.1 score
    explanation system.
    """

    analysis = get_analysis(
        analysis_id
    )

    if analysis is None:

        return render_template(

            "history.html",

            analyses=
                get_analysis_history(
                    limit=50
                ),

            error=
                "Analysis not found.",

        ), 404

    score_explanations = (
        build_score_explanations(

            analysis.get(
                "dashboard_result"
            ),

            analysis.get(
                "ats_result"
            ),

            analysis.get(
                "quality_result"
            ),

            analysis.get(
                "job_result"
            ),

            analysis.get(
                "improvement_result"
            ),
        )
    )

    return render_template(

        "index.html",

        resume=analysis.get(
            "resume"
        ),

        ats_result=analysis.get(
            "ats_result"
        ),

        quality_result=analysis.get(
            "quality_result"
        ),

        improvement_result=
            analysis.get(
                "improvement_result"
            ),

        job_result=analysis.get(
            "job_result"
        ),

        dashboard_result=
            analysis.get(
                "dashboard_result"
            ),

        score_explanations=
            score_explanations,

        analytics_result=
            analysis.get(
                "analytics_result"
            ),

        extracted_text=None,

        error=None,

        job_description=
            analysis.get(
                "job_description",
                "",
            ),

        history_view=True,

        analysis_id=analysis_id,
    )


# ============================================================
# DELETE SAVED ANALYSIS
# ============================================================

@app.route(
    "/history/<int:analysis_id>/delete",
    methods=["POST"],
)
def delete_history(
    analysis_id: int,
):
    """
    Delete a saved analysis and return to history.
    """

    delete_analysis(
        analysis_id
    )

    return redirect(
        url_for(
            "history"
        )
    )


# ============================================================
# PDF REPORT DOWNLOAD
# ============================================================

@app.route(
    "/download-report",
    methods=["POST"],
)
def download_report():
    """
    Generate and download a PDF resume analysis report.
    """

    file = request.files.get(
        "resume"
    )

    job_description = sanitize_text(

        request.form.get(
            "job_description",
            "",
        ),

        max_length=
            MAX_JOB_DESCRIPTION_LENGTH,
    )

    try:

        # ----------------------------------------------------
        # Validate upload.
        # ----------------------------------------------------

        if (
            file is None
            or not file.filename
        ):

            raise ValueError(
                "Please upload a PDF resume."
            )

        # ----------------------------------------------------
        # Validate extension.
        # ----------------------------------------------------

        if not allowed_file(
            file.filename
        ):

            raise ValueError(
                "Only PDF resume files are supported."
            )

        # ----------------------------------------------------
        # Validate actual PDF.
        # ----------------------------------------------------

        if not is_valid_pdf(
            file
        ):

            raise ValueError(
                "Unable to generate the PDF report."
            )

        # ----------------------------------------------------
        # Analyze resume.
        # ----------------------------------------------------

        results = _analyze_uploaded_resume(

            file,

            job_description,
        )

        # ----------------------------------------------------
        # Generate PDF report.
        # ----------------------------------------------------

        pdf_bytes = generate_resume_report(

            resume=results[
                "resume"
            ],

            ats_result=results[
                "ats_result"
            ],

            quality_result=results[
                "quality_result"
            ],

            improvement_result=
                results[
                    "improvement_result"
                ],

            job_result=results[
                "job_result"
            ],

            dashboard_result=
                results[
                    "dashboard_result"
                ],

            analytics_result=
                results[
                    "analytics_result"
                ],
        )

        # ----------------------------------------------------
        # Send PDF to browser.
        # ----------------------------------------------------

        return send_file(

            BytesIO(
                pdf_bytes
            ),

            mimetype=
                "application/pdf",

            as_attachment=True,

            download_name=(
                "AI_Resume_Analyzer_V3.2_Report.pdf"
            ),
        )

    except ValueError as exc:

        return _render_index_error(

            str(exc),

            job_description,
        )

    except Exception as exc:

        app.logger.exception(
            "Unable to generate PDF report: %s",
            exc,
        )

        return _render_index_error(

            "Unable to generate the PDF report. "
            "Please try again.",

            job_description,
        )

# ============================================================
# V3.3 AI WRITING ASSISTANT
# ============================================================

def _ai_error_response(message: str):
    """
    Return a safe JSON response for AI writing errors.
    """

    return {
        "success": False,
        "error": message,
    }, 400


def _validate_ai_input(
    value: str,
    field_name: str,
    max_length: int = 5000,
) -> str:
    """
    Validate and sanitize AI writing input.
    """

    if not isinstance(value, str):
        raise ValueError(
            f"{field_name} must be text."
        )

    value = sanitize_text(
        value,
        max_length=max_length,
    )

    if not value:
        raise ValueError(
            f"{field_name} cannot be empty."
        )

    return value


def _generate_ai_writing(
    *,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """
    Generate AI-written resume content through the
    centralized provider abstraction.
    """

    if not is_ai_configured():
        raise AIProviderError(
            "AI writing is not configured."
        )

    result = generate_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    result = sanitize_text(
        result,
        max_length=5000,
    )

    if not result:
        raise AIProviderError(
            "AI provider returned empty content."
        )

    return result


@app.route(
    "/api/ai/rewrite-bullet",
    methods=["POST"],
)
def ai_rewrite_bullet():
    """
    Rewrite one resume bullet using AI.
    """

    try:

        bullet = _validate_ai_input(
            request.form.get(
                "bullet",
                "",
            ),
            "Bullet",
            max_length=3000,
        )

        rewritten = _generate_ai_writing(

            system_prompt=
                BULLET_REWRITE_SYSTEM_PROMPT,

            user_prompt=
                build_bullet_rewrite_prompt(
                    bullet
                ),
        )

        return {
            "success": True,
            "type": "bullet",
            "original": bullet,
            "rewritten": rewritten,
        }

    except ValueError as exc:

        return _ai_error_response(
            str(exc)
        )

    except AIProviderError as exc:

        app.logger.warning(
            "AI bullet rewrite failed: %s",
            exc,
        )

        return _ai_error_response(
            str(exc)
        )

    except Exception as exc:

        app.logger.exception(
            "Unexpected AI bullet rewrite error: %s",
            exc,
        )

        return _ai_error_response(
            "Unable to rewrite the bullet."
        )


@app.route(
    "/api/ai/rewrite-summary",
    methods=["POST"],
)
def ai_rewrite_summary():
    """
    Improve a professional summary using AI.
    """

    try:

        summary = _validate_ai_input(
            request.form.get(
                "summary",
                "",
            ),
            "Summary",
            max_length=5000,
        )

        rewritten = _generate_ai_writing(

            system_prompt=
                SUMMARY_REWRITE_SYSTEM_PROMPT,

            user_prompt=
                build_summary_rewrite_prompt(
                    summary
                ),
        )

        return {
            "success": True,
            "type": "summary",
            "original": summary,
            "rewritten": rewritten,
        }

    except ValueError as exc:

        return _ai_error_response(
            str(exc)
        )

    except AIProviderError as exc:

        app.logger.warning(
            "AI summary rewrite failed: %s",
            exc,
        )

        return _ai_error_response(
            str(exc)
        )

    except Exception as exc:

        app.logger.exception(
            "Unexpected AI summary rewrite error: %s",
            exc,
        )

        return _ai_error_response(
            "Unable to rewrite the summary."
        )


@app.route(
    "/api/ai/rewrite-project",
    methods=["POST"],
)
def ai_rewrite_project():
    """
    Improve a project description using AI.
    """

    try:

        project = _validate_ai_input(
            request.form.get(
                "project",
                "",
            ),
            "Project description",
            max_length=5000,
        )

        rewritten = _generate_ai_writing(

            system_prompt=
                PROJECT_REWRITE_SYSTEM_PROMPT,

            user_prompt=
                build_project_rewrite_prompt(
                    project
                ),
        )

        return {
            "success": True,
            "type": "project",
            "original": project,
            "rewritten": rewritten,
        }

    except ValueError as exc:

        return _ai_error_response(
            str(exc)
        )

    except AIProviderError as exc:

        app.logger.warning(
            "AI project rewrite failed: %s",
            exc,
        )

        return _ai_error_response(
            str(exc)
        )

    except Exception as exc:

        app.logger.exception(
            "Unexpected AI project rewrite error: %s",
            exc,
        )

        return _ai_error_response(
            "Unable to rewrite the project description."
        )


@app.route(
    "/api/ai/rewrite-experience",
    methods=["POST"],
)
def ai_rewrite_experience():
    """
    Improve an experience bullet using AI.
    """

    try:

        bullet = _validate_ai_input(
            request.form.get(
                "bullet",
                "",
            ),
            "Experience bullet",
            max_length=3000,
        )

        rewritten = _generate_ai_writing(

            system_prompt=
                EXPERIENCE_REWRITE_SYSTEM_PROMPT,

            user_prompt=
                build_experience_rewrite_prompt(
                    bullet
                ),
        )

        return {
            "success": True,
            "type": "experience",
            "original": bullet,
            "rewritten": rewritten,
        }

    except ValueError as exc:

        return _ai_error_response(
            str(exc)
        )

    except AIProviderError as exc:

        app.logger.warning(
            "AI experience rewrite failed: %s",
            exc,
        )

        return _ai_error_response(
            str(exc)
        )

    except Exception as exc:

        app.logger.exception(
            "Unexpected AI experience rewrite error: %s",
            exc,
        )

        return _ai_error_response(
            "Unable to rewrite the experience bullet."
        )

# ============================================================
# V3.4 AI JOB TAILORING
# ============================================================

from app.ai.tailoring.service import (
    AITailoringError,
    tailor_resume_to_job,
)


@app.route(
    "/api/ai/tailor-job",
    methods=["POST"],
)
def ai_tailor_job():

    try:

        resume_text = sanitize_text(
            request.form.get(
                "resume_text",
                "",
            ),
            max_length=50000,
        )

        job_description = sanitize_text(
            request.form.get(
                "job_description",
                "",
            ),
            max_length=MAX_JOB_DESCRIPTION_LENGTH,
        )

        result = tailor_resume_to_job(
            resume_text=resume_text,
            job_description=job_description,
        )

        return {
            "success": True,
            "result": result,
        }

    except ValueError as exc:

        return {
            "success": False,
            "error": str(exc),
        }, 400

    except AITailoringError as exc:

        app.logger.warning(
            "AI job tailoring failed: %s",
            exc,
        )

        return {
            "success": False,
            "error": str(exc),
        }, 400

    except Exception as exc:

        app.logger.exception(
            "Unexpected AI job tailoring error: %s",
            exc,
        )

        return {
            "success": False,
            "error": (
                "Unable to generate job-tailoring "
                "recommendations."
            ),
        }, 500

# ============================================================
# AI PROVIDER STATUS
# ============================================================

@app.route(
    "/api/ai/status",
    methods=["GET"],
)
def ai_status():
    """
    Return non-sensitive AI provider status.
    """

    return {
        "success": True,
        "configured": is_ai_configured(),
    }

# ============================================================
# PRIVACY PAGE
# ============================================================

@app.route(
    "/privacy",
    methods=["GET"],
)
def privacy():
    """
    Display the application's privacy information.
    """

    return render_template(
        "privacy.html"
    )


# ============================================================
# TERMS PAGE
# ============================================================

@app.route(
    "/terms",
    methods=["GET"],
)
def terms():
    """
    Display the application's terms of use.
    """

    return render_template(
        "terms.html"
    )


# ============================================================
# FAVICON
# ============================================================

@app.route(
    "/favicon.ico"
)
def favicon():
    """
    Serve the favicon.svg when browsers request /favicon.ico.
    """

    static_folder = Path(
        app.static_folder
    )

    favicon_path = (
        static_folder
        / "favicon.svg"
    )

    if favicon_path.exists():

        return send_from_directory(

            static_folder,

            "favicon.svg",

            mimetype="image/svg+xml",
        )

    return "", 204


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    app.run(

        host=APP_HOST,

        port=APP_PORT,

        debug=app.config[
            "DEBUG"
        ],
    )