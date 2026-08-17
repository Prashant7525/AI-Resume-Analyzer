"""
Main Flask application for the AI Resume Analyzer.

V2.3
- Resume analysis
- Dashboard
- Analytics
- PDF report download
"""

from __future__ import annotations

from io import BytesIO

from flask import (
    Flask,
    render_template,
    request,
    send_file,
)

from app.analytics import build_analytics
from app.ats_analyzer import analyze_resume
from app.dashboard import build_dashboard_result
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


app = Flask(__name__)

ALLOWED_EXTENSIONS = {"pdf"}


# ============================================================
# FILE VALIDATION
# ============================================================


def allowed_file(filename: str) -> bool:
    """Return True when the uploaded file is an allowed PDF."""

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1,
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


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

    extracted_text = extract_text_from_pdf(
        file
    )

    if not extracted_text:

        raise ValueError(
            "The PDF does not contain readable text."
        )

    resume = parse_resume(
        extracted_text
    )

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
    # Improvement analysis
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
        "improvement_result": improvement_result,
        "job_result": job_result,
        "dashboard_result": dashboard_result,
        "analytics_result": analytics_result,
        "extracted_text": extracted_text,
    }


# ============================================================
# MAIN PAGE
# ============================================================


@app.route(
    "/",
    methods=["GET", "POST"],
)
def index():

    resume = None

    ats_result = None
    quality_result = None
    improvement_result = None
    job_result = None
    dashboard_result = None
    analytics_result = None

    extracted_text = None

    error = None

    job_description = ""

    if request.method == "POST":

        file = request.files.get(
            "resume"
        )

        job_description = request.form.get(
            "job_description",
            "",
        ).strip()

        if (
            file is None
            or file.filename == ""
        ):

            error = (
                "Please upload a PDF resume."
            )

        elif not allowed_file(
            file.filename
        ):

            error = (
                "Only PDF resume files are supported."
            )

        else:

            try:

                results = _analyze_uploaded_resume(
                    file,
                    job_description,
                )

                resume = results["resume"]

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

                analytics_result = results[
                    "analytics_result"
                ]

                extracted_text = results[
                    "extracted_text"
                ]

            except ValueError as exc:

                error = str(exc)

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
        improvement_result=improvement_result,
        job_result=job_result,

        dashboard_result=dashboard_result,
        analytics_result=analytics_result,

        extracted_text=extracted_text,

        error=error,

        job_description=job_description,
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
    Generate and download a PDF report.

    The resume is analyzed again using the uploaded PDF so
    the download route does not depend on temporary server state.
    """

    file = request.files.get(
        "resume"
    )

    job_description = request.form.get(
        "job_description",
        "",
    ).strip()

    if (
        file is None
        or file.filename == ""
    ):

        return render_template(
            "index.html",
            error="Please upload a PDF resume.",
            job_description=job_description,
        )

    if not allowed_file(
        file.filename
    ):

        return render_template(
            "index.html",
            error="Only PDF resume files are supported.",
            job_description=job_description,
        )

    try:

        results = _analyze_uploaded_resume(
            file,
            job_description,
        )

        pdf_bytes = generate_resume_report(
            resume=results["resume"],
            ats_result=results[
                "ats_result"
            ],
            quality_result=results[
                "quality_result"
            ],
            improvement_result=results[
                "improvement_result"
            ],
            job_result=results[
                "job_result"
            ],
            dashboard_result=results[
                "dashboard_result"
            ],
            analytics_result=results[
                "analytics_result"
            ],
        )

        return send_file(
            BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=(
                "AI_Resume_Analyzer_V2.3_Report.pdf"
            ),
        )

    except ValueError as exc:

        return render_template(
            "index.html",
            error=str(exc),
            job_description=job_description,
        )

    except Exception as exc:

        app.logger.exception(
            "Unable to generate PDF report: %s",
            exc,
        )

        return render_template(
            "index.html",
            error=(
                "Unable to generate the PDF report. "
                "Please try again."
            ),
            job_description=job_description,
        )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================


if __name__ == "__main__":

    app.run(
        debug=True
    )