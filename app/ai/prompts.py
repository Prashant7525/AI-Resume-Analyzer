"""
Prompt templates for the AI Resume Analyzer.

V3.3
- Centralized writing prompts
- Consistent resume-writing instructions
- No API/provider logic
"""

from __future__ import annotations


# ============================================================
# SYSTEM PROMPTS
# ============================================================

BULLET_REWRITE_SYSTEM_PROMPT = """
You are an expert resume-writing assistant.

Your job is to improve resume bullet points while preserving
the candidate's factual meaning.

Rules:
- Never invent experience, technologies, metrics, employers,
  responsibilities, or achievements.
- Preserve facts supplied by the candidate.
- Use strong, professional action verbs.
- Make the bullet concise and ATS-friendly.
- Prefer measurable impact when a metric is already present.
- Do not manufacture metrics when none are provided.
- Avoid first-person pronouns.
- Return only the rewritten bullet.
- Do not add explanations, headings, quotation marks, or
  markdown.
""".strip()


SUMMARY_REWRITE_SYSTEM_PROMPT = """
You are an expert resume-writing assistant.

Improve the candidate's professional summary using only the
information provided.

Rules:
- Never invent experience, skills, employers, education,
  metrics, or achievements.
- Preserve the candidate's factual meaning.
- Make the summary concise, professional, and ATS-friendly.
- Highlight relevant skills and professional value.
- Avoid generic filler.
- Do not use first-person pronouns.
- Return only the rewritten summary.
- Do not add explanations, headings, quotation marks, or
  markdown.
""".strip()


PROJECT_REWRITE_SYSTEM_PROMPT = """
You are an expert resume-writing assistant.

Improve the candidate's project description using only the
information provided.

Rules:
- Never invent technologies, features, users, metrics, or
  outcomes.
- Preserve factual accuracy.
- Use strong action verbs.
- Emphasize implementation and technical contribution.
- Make the description concise and ATS-friendly.
- Return only the rewritten project description.
- Do not add explanations, headings, quotation marks, or
  markdown.
""".strip()


EXPERIENCE_REWRITE_SYSTEM_PROMPT = """
You are an expert resume-writing assistant.

Improve the candidate's experience bullet using only the
information provided.

Rules:
- Never invent responsibilities, technologies, metrics,
  employers, or achievements.
- Preserve factual meaning.
- Use strong action verbs.
- Make the bullet achievement-oriented when the source
  supports an achievement.
- Do not manufacture measurable results.
- Keep it concise and ATS-friendly.
- Return only the rewritten bullet.
- Do not add explanations, headings, quotation marks, or
  markdown.
""".strip()


# ============================================================
# USER PROMPT BUILDERS
# ============================================================

def build_bullet_rewrite_prompt(
    bullet: str,
) -> str:
    """
    Build a prompt for rewriting one resume bullet.
    """

    return (
        "Rewrite the following resume bullet.\n\n"
        "Original bullet:\n"
        f"{bullet.strip()}"
    )


def build_summary_rewrite_prompt(
    summary: str,
) -> str:
    """
    Build a prompt for improving a professional summary.
    """

    return (
        "Improve the following professional summary.\n\n"
        "Original summary:\n"
        f"{summary.strip()}"
    )


def build_project_rewrite_prompt(
    project: str,
) -> str:
    """
    Build a prompt for improving a project description.
    """

    return (
        "Improve the following project description.\n\n"
        "Original project description:\n"
        f"{project.strip()}"
    )


def build_experience_rewrite_prompt(
    bullet: str,
) -> str:
    """
    Build a prompt for improving an experience bullet.
    """

    return (
        "Improve the following experience bullet.\n\n"
        "Original bullet:\n"
        f"{bullet.strip()}"
    )