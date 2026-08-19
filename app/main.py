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
"""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    send_file,
    send_from_directory,
    redirect,
    url_for,
)

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


# ============================================================
# APPLICATION
# ============================================================

app = Flask(__name__)

ALLOWED_EXTENSIONS = {"pdf"}


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

init_database()


# ============================================================
# TEMPLATE FILTERS
# ============================================================

@app.template_filter("format_history_date")
def format_history_date(value):
    """
    Format an ISO timestamp for the analysis history page.
    """

    if not value:
        return "Unknown date"

    try:
        timestamp = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
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
# FILE VALIDATION
# ============================================================

def allowed_file(filename: str) -> bool:
    """
    Return True when the uploaded file is an allowed PDF.
    """

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

    # --------------------------------------------------------
    # Extract PDF text
    # --------------------------------------------------------

    extracted_text = extract_text_from_pdf(
        file
    )

    if not extracted_text:
        raise ValueError(
            "The PDF does not contain readable text."
        )

    # --------------------------------------------------------
    # Resume parsing
    # --------------------------------------------------------

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

    score_explanations = build_score_explanations(
        dashboard_result,
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
        "score_explanations": score_explanations,
        "analytics_result": analytics_result,
        "extracted_text": extracted_text,
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

        job_description = request.form.get(
            "job_description",
            "",
        ).strip()

        # ----------------------------------------------------
        # Validate uploaded file
        # ----------------------------------------------------

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

                # ------------------------------------------------
                # Analyze resume
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
                # Save analysis to history
                # ------------------------------------------------

                _save_analysis_results(
                    results,
                    job_description,
                )

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
        score_explanations=score_explanations,
        analytics_result=analytics_result,

        extracted_text=extracted_text,

        error=error,

        job_description=job_description,

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

            analyses=get_analysis_history(
                limit=50
            ),

            error="Analysis not found.",
        ), 404

    # --------------------------------------------------------
    # Generate V3.1 score explanations dynamically.
    # This keeps old saved analyses compatible.
    # --------------------------------------------------------

    score_explanations = build_score_explanations(
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

        improvement_result=analysis.get(
            "improvement_result"
        ),

        job_result=analysis.get(
            "job_result"
        ),

        dashboard_result=analysis.get(
            "dashboard_result"
        ),

        score_explanations=score_explanations,

        analytics_result=analysis.get(
            "analytics_result"
        ),

        extracted_text=None,

        error=None,

        job_description=analysis.get(
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
        url_for("history")
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

    Invalid or missing uploads are handled gracefully
    and return the main page with HTTP 200.
    """

    # --------------------------------------------------------
    # Safely obtain uploaded file and job description
    # --------------------------------------------------------

    file = request.files.get(
        "resume"
    )

    job_description = request.form.get(
        "job_description",
        "",
    ).strip()

    # --------------------------------------------------------
    # Validate missing file
    # --------------------------------------------------------

    if (
        file is None
        or not file.filename
    ):

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

            error="Please upload a PDF resume.",

            job_description=job_description,

            history_view=False,
            analysis_id=None,
        ), 200

    # --------------------------------------------------------
    # Validate file extension
    # --------------------------------------------------------

    if not allowed_file(
        file.filename
    ):

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

            error=(
                "Only PDF resume files are supported."
            ),

            job_description=job_description,

            history_view=False,
            analysis_id=None,
        ), 200

    # --------------------------------------------------------
    # Analyze resume
    # --------------------------------------------------------

    try:

        results = _analyze_uploaded_resume(
            file,
            job_description,
        )

        # ----------------------------------------------------
        # Generate PDF report
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

        # ----------------------------------------------------
        # Send PDF to browser
        # ----------------------------------------------------

        return send_file(

            BytesIO(
                pdf_bytes
            ),

            mimetype="application/pdf",

            as_attachment=True,

            download_name=(
                "AI_Resume_Analyzer_V3.1_Report.pdf"
            ),
        )

    except ValueError as exc:

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

            error=str(exc),

            job_description=job_description,

            history_view=False,
            analysis_id=None,
        ), 200

    except Exception as exc:

        app.logger.exception(
            "Unable to generate PDF report: %s",
            exc,
        )

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

            error=(
                "Unable to process the PDF file. "
                "Please make sure it is a valid "
                "text-based PDF."
            ),

            job_description=job_description,

            history_view=False,
            analysis_id=None,
        ), 200


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
    Serve the favicon.svg when browsers request
    /favicon.ico.
    """

    static_folder = Path(
        app.static_folder
    )

    favicon_path = (
        static_folder / "favicon.svg"
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
        debug=True
    )