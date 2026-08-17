from flask import Flask, render_template, request

from app.ats_analyzer import analyze_resume
from app.dashboard import build_dashboard_result
from app.job_matcher import match_resume_to_job
from app.resume_improvements import analyze_resume_improvements
from app.resume_parser import extract_text_from_pdf, parse_resume
from app.resume_quality import analyze_resume_quality
from app.analytics import build_analytics


app = Flask(__name__)

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    """Return True when the uploaded file is an allowed PDF."""

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/", methods=["GET", "POST"])
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

        file = request.files.get("resume")

        job_description = request.form.get(
            "job_description",
            "",
        ).strip()

        if file is None or file.filename == "":
            error = "Please upload a PDF resume."

        elif not allowed_file(file.filename):
            error = "Only PDF resume files are supported."

        else:

            try:

                extracted_text = extract_text_from_pdf(
                    file
                )

                if not extracted_text:

                    error = (
                        "The PDF does not contain readable text."
                    )

                else:

                    # -----------------------------------------
                    # RESUME PARSING
                    # -----------------------------------------

                    resume = parse_resume(
                        extracted_text
                    )

                    # -----------------------------------------
                    # ATS ANALYSIS
                    # -----------------------------------------

                    ats_result = analyze_resume(
                        resume
                    )

                    # -----------------------------------------
                    # RESUME QUALITY
                    # -----------------------------------------

                    quality_result = analyze_resume_quality(
                        resume
                    )

                    # -----------------------------------------
                    # IMPROVEMENT ANALYSIS
                    # -----------------------------------------

                    improvement_result = (
                        analyze_resume_improvements(
                            resume
                        )
                    )

                    # -----------------------------------------
                    # JOB MATCHING
                    # -----------------------------------------

                    if job_description:

                        job_result = match_resume_to_job(
                            resume,
                            job_description,
                        )

                    # -----------------------------------------
                    # V2.2 DASHBOARD
                    # -----------------------------------------

                    dashboard_result = build_dashboard_result(
                        resume,
                        ats_result,
                        quality_result,
                        job_result,
                        improvement_result,
                    )

                    # -----------------------------------------
                    # V2.2 ANALYTICS
                    # -----------------------------------------

                    analytics_result = build_analytics(
                        ats_result,
                        quality_result,
                        improvement_result,
                        job_result,
                    )

            except Exception as exc:

                app.logger.exception(
                    "Unable to process resume: %s",
                    exc,
                )

                error = (
                    "Unable to process the PDF file. "
                    "Please make sure it is a valid text-based PDF."
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
    app.run(
        debug=True
    )