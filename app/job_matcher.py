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


# Important job-related keywords that are useful for ATS analysis.
DEFAULT_KEYWORD_PATTERNS = {
    "api": r"\bapis?\b",
    "backend": r"\bbackend\b|\bback-end\b",
    "frontend": r"\bfrontend\b|\bfront-end\b",
    "full stack": r"\bfull[\s-]?stack\b",
    "software development": r"\bsoftware development\b",
    "web development": r"\bweb development\b",
    "application development": r"\bapplication development\b",
    "data structures": r"\bdata structures?\b",
    "algorithms": r"\balgorithms?\b",
    "object oriented programming": (
        r"\bobject[\s-]?oriented programming\b|\boop\b"
    ),
    "database": r"\bdatabases?\b|\bdatabase management\b",
    "testing": r"\btesting\b|\btest automation\b",
    "debugging": r"\bdebugging\b",
    "deployment": r"\bdeployment\b|\bdeploying\b",
    "cloud": r"\bcloud\b|\bcloud computing\b",
    "agile": r"\bagile\b",
    "scrum": r"\bscrum\b",
    "restful": r"\brestful\b",
    "microservices": r"\bmicroservices?\b",
    "ci/cd": r"\bci\s*/\s*cd\b|\bcontinuous integration\b",
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


def extract_keywords(
    text: str,
    keyword_patterns=None,
) -> set[str]:
    """
    Extract important job-related keywords from text.

    Keywords are intentionally separate from technical skills.
    """

    if not text:
        return set()

    patterns = keyword_patterns or DEFAULT_KEYWORD_PATTERNS
    normalized = normalize_text(text)

    found = set()

    for keyword, pattern in patterns.items():
        if re.search(pattern, normalized, re.IGNORECASE):
            found.add(keyword)

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


def calculate_keyword_coverage(
    resume_keywords: set[str],
    job_keywords: set[str],
) -> int:
    """
    Calculate percentage of job keywords represented in the resume.
    """

    if not job_keywords:
        return 0

    matched = resume_keywords & job_keywords

    return round(
        len(matched) / len(job_keywords) * 100
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


def generate_keyword_suggestions(
    matched_keywords: set[str],
    missing_keywords: set[str],
) -> list[str]:
    """
    Generate suggestions based on job-description keywords.
    """

    suggestions = []

    if missing_keywords:
        missing = ", ".join(sorted(missing_keywords))

        suggestions.append(
            "Consider naturally including relevant job keywords "
            f"such as: {missing}."
        )

    if matched_keywords:
        matched = ", ".join(sorted(matched_keywords))

        suggestions.append(
            "Your resume already includes relevant keywords such as: "
            f"{matched}."
        )

    if not matched_keywords and missing_keywords:
        suggestions.append(
            "Your resume has limited keyword coverage. "
            "Tailor your summary, skills, projects, or experience "
            "to the job description where appropriate."
        )

    return suggestions


def match_resume_to_job(
    resume: dict,
    job_description: str,
) -> dict:
    """Compare a structured resume with a job description."""

    resume_text = resume_to_text(resume)

    # Existing skill analysis.
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    matched_skills = resume_skills & job_skills
    missing_skills = job_skills - resume_skills

    score = calculate_match_score(
        resume_skills,
        job_skills,
    )

    skill_suggestions = generate_job_suggestions(
        matched_skills,
        missing_skills,
    )

    # New keyword analysis.
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)

    matched_keywords = resume_keywords & job_keywords
    missing_keywords = job_keywords - resume_keywords

    keyword_coverage = calculate_keyword_coverage(
        resume_keywords,
        job_keywords,
    )

    keyword_suggestions = generate_keyword_suggestions(
        matched_keywords,
        missing_keywords,
    )

    return {
        # Existing v1.3 fields.
        "score": score,
        "resume_skills": sorted(resume_skills),
        "job_skills": sorted(job_skills),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "suggestions": skill_suggestions,

        # New v1.7 keyword fields.
        "resume_keywords": sorted(resume_keywords),
        "job_keywords": sorted(job_keywords),
        "matched_keywords": sorted(matched_keywords),
        "missing_keywords": sorted(missing_keywords),
        "keyword_coverage": keyword_coverage,
        "keyword_suggestions": keyword_suggestions,
    }