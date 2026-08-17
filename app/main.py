from flask import Flask, render_template, request

from app.resume_parser import extract_text_from_pdf


app = Flask(__name__)

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/", methods=["GET", "POST"])
def index():
    extracted_text = None
    error = None

    if request.method == "POST":
        file = request.files.get("resume")

        if file is None or file.filename == "":
            error = "Please select a PDF resume."

        elif not allowed_file(file.filename):
            error = "Only PDF files are supported."

        else:
            try:
                extracted_text = extract_text_from_pdf(file)
            except Exception:
                error = "Unable to read the PDF file."

    return render_template(
        "index.html",
        extracted_text=extracted_text,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)