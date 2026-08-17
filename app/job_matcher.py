import re


DEFAULT_SKILL_PATTERNS = {
    "python": r"\bpython\b",
    "java": r"\bjava\b",
    "c++": r"\bc\+\+\b",
    "javascript": r"\bjavascript\b|\bjs\b",
    "typescript": r"\btypescript\b",
    "sql": r"\bsql\b",
    "html": r"\bhtml\b",
    "css": r"\bcss\b",
    "react": r"\breact(?:\.js)?\b",
    "node.js": r"\bnode(?:\.js)?\b",
    "django": r"\bdjango\b",
    "flask": r"\bflask\b",
    "fastapi": r"\bfastapi\b",
    "git": r"\bgit\b",
    "docker": r"\bdocker\b",
    "kubernetes": r"\bkubernetes\b|\bk8s\b",
    "aws": r"\baws\b|\bamazon web services\b",
    "azure": r"\bazure\b",
    "gcp": r"\bgcp\b|\bgoogle cloud\b",
    "machine learning": r"\bmachine learning\b|\bml\b",
    "deep learning": r"\bdeep learning\b",
    "tensorflow": r"\btensorflow\b",
    "pytorch": r"\bpytorch\b",
    "pandas": r"\bpandas\b",
    "numpy": r"\bnumpy\b",
    "rest api": r"\brest(?:ful)? api(?:s)?\b",
    "graphql": r"\bgraphql\b",
}


def normalize_text(text: str) -> str:
    """Normalize text for matching."""

    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills(text: str, skill_patterns=None) -> set[str]:
    """Extract known skills from a piece of text."""

    if not text:
        return set()

    patterns = skill_patterns or DEFAULT_SKILL_PATTERNS
    normalized = normalize_text(text)

    found = set()

    for skill, pattern in patterns.items():
        if re.search(pattern, normalized, re.IGNORECASE):
            found.add(skill)

    return found


def resume_to_text(resume: dict) -> str:
    """Combine useful resume fields into searchable text."""

    fields = [
        "summary",
        "skills",
        "experience",
        "projects",
        "education",
        "certifications",
        "achievements",
        "other",
    ]

    return " ".join(
        str(resume.get(field, ""))
        for field in fields
    )


def calculate_match_score(
    resume_skills: set[str],
    job_skills: set[str],
) -> int:
    """Calculate percentage of job skills found in the resume."""

    if not job_skills:
        return 0

    matched = resume_skills & job_skills

    return round(
        len(matched) / len(job_skills) * 100
    )


def generate_job_suggestions(
    matched_skills: set[str],
    missing_skills: set[str],
) -> list[str]:
    """Generate suggestions based on the job match."""

    suggestions = []

    if missing_skills:
        missing = ", ".join(sorted(missing_skills))
        suggestions.append(
            f"Review the job description for missing skills: {missing}."
        )

    if matched_skills:
        matched = ", ".join(sorted(matched_skills))
        suggestions.append(
            f"Highlight your experience with: {matched}."
        )

    if not matched_skills:
        suggestions.append(
            "Very few relevant skills were detected. "
            "Review the resume against the job requirements."
        )

    return suggestions


def match_resume_to_job(
    resume: dict,
    job_description: str,
) -> dict:
    """Compare a structured resume with a job description."""

    resume_text = resume_to_text(resume)

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    matched_skills = resume_skills & job_skills
    missing_skills = job_skills - resume_skills

    score = calculate_match_score(
        resume_skills,
        job_skills,
    )

    suggestions = generate_job_suggestions(
        matched_skills,
        missing_skills,
    )

    return {
        "score": score,
        "resume_skills": sorted(resume_skills),
        "job_skills": sorted(job_skills),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "suggestions": suggestions,
    }