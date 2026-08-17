from flask import Flask, render_template, request

from app.analytics import build_analytics_result
from app.ats_analyzer import analyze_resume
from app.dashboard import build_dashboard_result
from app.job_matcher import match_resume_to_job
from app.resume_improvements import analyze_resume_improvements
from app.resume_parser import extract_text_from_pdf, parse_resume
from app.resume_quality import analyze_resume_quality


app = Flask(__name__)

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    """Return True when the uploaded file is an allowed type."""

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the resume analyzer and process uploaded resumes."""

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
        file = request.files.get("resume")

        job_description = request.form.get(
            "job_description",
            "",
        ).strip()

        # =========================================
        # FILE VALIDATION
        # =========================================

        if file is None or file.filename == "":
            error = "Please select a PDF resume."

        elif not allowed_file(file.filename):
            error = "Only PDF files are supported."

        else:

            try:

                # =========================================
                # PDF TEXT EXTRACTION
                # =========================================

                extracted_text = extract_text_from_pdf(file)

                if not extracted_text:
                    error = (
                        "The PDF does not contain readable text."
                    )

                else:

                    # =========================================
                    # RESUME PARSING
                    # =========================================

                    resume = parse_resume(
                        extracted_text
                    )

                    # =========================================
                    # ATS ANALYSIS
                    # =========================================

                    ats_result = analyze_resume(
                        resume
                    )

                    # =========================================
                    # RESUME QUALITY ANALYSIS
                    # =========================================

                    quality_result = (
                        analyze_resume_quality(
                            resume
                        )
                    )

                    # =========================================
                    # RESUME IMPROVEMENT ANALYSIS
                    # =========================================

                    improvement_result = (
                        analyze_resume_improvements(
                            resume
                        )
                    )

                    # =========================================
                    # JOB MATCHING
                    # =========================================

                    if job_description:

                        job_result = match_resume_to_job(
                            resume,
                            job_description,
                        )

                    # =========================================
                    # V2.0 UNIFIED DASHBOARD
                    # =========================================

                    dashboard_result = (
                        build_dashboard_result(
                            resume,
                            ats_result,
                            quality_result,
                            job_result,
                            improvement_result,
                        )
                    )

                    # =========================================
                    # V2.1 ANALYTICS
                    # =========================================

                    analytics_result = (
                        build_analytics_result(
                            ats_result,
                            quality_result,
                            improvement_result,
                            job_result,
                        )
                    )

            except Exception:
                error = (
                    "Unable to process the PDF file."
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


if __name__ == "__main__":
    app.run(debug=True)