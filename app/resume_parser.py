import pymupdf


def extract_text_from_pdf(file_stream) -> str:
    """Extract text from a PDF file-like object."""

    document = pymupdf.open(
        stream=file_stream.read(),
        filetype="pdf"
    )

    pages = []

    for page in document:
        pages.append(page.get_text())

    document.close()

    return "\n".join(pages).strip()