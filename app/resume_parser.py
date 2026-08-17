import re

import pymupdf


SECTION_NAMES = {
    "summary": {
        "professional summary",
        "summary",
        "profile",
        "objective",
    },
    "skills": {
        "technical skills",
        "skills",
        "technical skills & tools",
    },
    "projects": {
        "projects",
        "personal projects",
        "academic projects",
    },
    "education": {
        "education",
        "academic background",
    },
    "certifications": {
        "certifications",
        "certificates",
    },
    "achievements": {
        "achievements",
        "accomplishments",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "internship",
    },
}


def extract_text_from_pdf(file_stream) -> str:
    """Extract text from a PDF file-like object."""

    document = pymupdf.open(
        stream=file_stream.read(),
        filetype="pdf",
    )

    pages = []

    for page in document:
        pages.append(page.get_text())

    document.close()

    return "\n".join(pages).strip()


def clean_text(text: str) -> str:
    """Normalize extracted resume text."""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    lines = []

    for line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


def detect_section(line: str):
    """Return the normalized section name if the line is a known heading."""

    normalized = line.strip().lower().rstrip(":")

    for section, names in SECTION_NAMES.items():
        if normalized in names:
            return section

    return None


def parse_sections(text: str) -> dict:
    """Split resume text into recognized sections."""

    text = clean_text(text)

    sections = {
        "summary": "",
        "skills": "",
        "projects": "",
        "education": "",
        "certifications": "",
        "achievements": "",
        "experience": "",
        "other": "",
    }

    current_section = "other"

    for line in text.splitlines():
        detected = detect_section(line)

        if detected:
            current_section = detected
            continue

        sections[current_section] += line + "\n"

    for section in sections:
        sections[section] = sections[section].strip()

    return sections


def extract_name(text: str) -> str:
    """Use the first meaningful line as a simple name candidate."""

    text = clean_text(text)

    if not text:
        return ""

    first_line = text.splitlines()[0]

    if len(first_line) <= 80:
        return first_line

    return ""


def extract_email(text: str) -> str:
    """Extract the first email address from resume text."""

    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
    )

    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """Extract a likely phone number from resume text."""

    match = re.search(
        r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)",
        text,
    )

    return match.group(0).strip() if match else ""


def parse_resume(text: str) -> dict:
    """Convert raw resume text into structured information."""

    text = clean_text(text)
    sections = parse_sections(text)

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "summary": sections["summary"],
        "skills": sections["skills"],
        "projects": sections["projects"],
        "education": sections["education"],
        "certifications": sections["certifications"],
        "achievements": sections["achievements"],
        "experience": sections["experience"],
        "other": sections["other"],
    }