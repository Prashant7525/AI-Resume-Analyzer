"""
AI Job Tailoring prompt templates.
"""
from __future__ import annotations


TAILORING_SYSTEM_PROMPT = """
You are an expert ATS resume optimization assistant.

Analyze the candidate resume against the supplied job description.

Rules:
- Never invent skills, experience, technologies, employers,
  metrics, qualifications, or achievements.
- Only recommend changes supported by the candidate's resume.
- Clearly distinguish existing skills from missing skills.
- Do not tell the candidate to falsely claim a skill.
- Prioritize relevant ATS keywords.
- Recommend where an existing skill or experience should be
  emphasized.
- Keep recommendations concise and actionable.
- Return valid JSON only.
""".strip()


def build_tailoring_prompt(
    resume_text: str,
    job_description: str,
) -> str:
    return (
        "Analyze the following resume against the job description.\n\n"
        "Return JSON with exactly these keys:\n"
        "match_summary, missing_skills, important_keywords, "
        "tailored_recommendations\n\n"
        "Resume:\n"
        f"{resume_text.strip()}\n\n"
        "Job Description:\n"
        f"{job_description.strip()}"
    )
