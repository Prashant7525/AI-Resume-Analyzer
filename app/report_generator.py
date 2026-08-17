from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _safe_score(result: dict | None, *keys: str):
    """Safely retrieve a nested score from an analysis result."""

    value = result

    for key in keys:
        if not isinstance(value, dict):
            return None

        value = value.get(key)

    if isinstance(value, (int, float)):
        return value

    return None


def _safe_list(value):
    """Return a list when the supplied value is list-like."""

    if isinstance(value, list):
        return value

    return []


def _build_styles():
    """Create PDF styles used by the report."""

    styles = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=27,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=18,
        ),
        "heading": ParagraphStyle(
            "ReportHeading",
            parent=styles["Heading2"],
            fontSize=15,
            leading=19,
            spaceBefore=10,
            spaceAfter=8,
            textColor=colors.HexColor("#172554"),
        ),
        "body": ParagraphStyle(
            "ReportBody",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=14,
            spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "ReportSmall",
            parent=styles["BodyText"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748b"),
        ),
    }


def _score_table(rows):
    """Create a formatted score table."""

    table_data = [["Metric", "Score"]]

    for metric, score in rows:
        display_score = "—" if score is None else f"{score}/100"
        table_data.append([metric, display_score])

    table = Table(
        table_data,
        colWidths=[125 * mm, 35 * mm],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#eef2ff"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#3730a3"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica",
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e2e8f0"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    return table


def _bullet_paragraphs(items, styles):
    """Convert recommendation strings into PDF bullet paragraphs."""

    elements = []

    for item in _safe_list(items):
        elements.append(
            Paragraph(
                f"• {item}",
                styles["body"],
            )
        )

    return elements


def generate_resume_report(
    resume: dict | None,
    ats_result: dict | None = None,
    quality_result: dict | None = None,
    improvement_result: dict | None = None,
    job_result: dict | None = None,
    dashboard_result: dict | None = None,
    analytics_result: dict | None = None,
) -> bytes:
    """
    Generate a complete PDF resume analysis report.

    Returns:
        PDF document contents as bytes.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="AI Resume Analyzer Report",
        author="AI Resume Analyzer",
    )

    styles = _build_styles()
    story = []

    resume = resume or {}

    # Report header.
    story.append(
        Paragraph(
            "AI Resume Analyzer",
            styles["title"],
        )
    )

    story.append(
        Paragraph(
            "Resume Analysis Report",
            styles["subtitle"],
        )
    )

    # Resume overview.
    story.append(
        Paragraph(
            "Resume Overview",
            styles["heading"],
        )
    )

    overview_rows = [
        [
            Paragraph("<b>Name</b>", styles["body"]),
            Paragraph(
                str(resume.get("name") or "Not detected"),
                styles["body"],
            ),
        ],
        [
            Paragraph("<b>Email</b>", styles["body"]),
            Paragraph(
                str(resume.get("email") or "Not detected"),
                styles["body"],
            ),
        ],
        [
            Paragraph("<b>Phone</b>", styles["body"]),
            Paragraph(
                str(resume.get("phone") or "Not detected"),
                styles["body"],
            ),
        ],
    ]

    overview_table = Table(
        overview_rows,
        colWidths=[40 * mm, 120 * mm],
    )

    overview_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e2e8f0"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(overview_table)
    story.append(Spacer(1, 8))

    # Unified dashboard.
    if dashboard_result:
        story.append(
            Paragraph(
                "Overall Dashboard",
                styles["heading"],
            )
        )

        dashboard_rows = [
            (
                "Overall Resume Score",
                _safe_score(dashboard_result, "overall_score"),
            ),
            (
                "ATS Readiness",
                _safe_score(
                    dashboard_result,
                    "breakdown",
                    "ats",
                ),
            ),
            (
                "Resume Quality",
                _safe_score(
                    dashboard_result,
                    "breakdown",
                    "quality",
                ),
            ),
            (
                "Improvement Readiness",
                _safe_score(
                    dashboard_result,
                    "breakdown",
                    "improvements",
                ),
            ),
        ]

        if dashboard_result.get("has_job_match"):
            dashboard_rows.append(
                (
                    "Job Match",
                    _safe_score(
                        dashboard_result,
                        "breakdown",
                        "job_match",
                    ),
                )
            )

        story.append(_score_table(dashboard_rows))
        story.append(Spacer(1, 8))

    # ATS analysis.
    if ats_result:
        story.append(
            Paragraph(
                "ATS Analysis",
                styles["heading"],
            )
        )

        ats_score = _safe_score(
            ats_result,
            "ats_score",
            "score",
        )

        completeness = _safe_score(
            ats_result,
            "ats_score",
            "completeness",
            "score",
        )

        content_quality = _safe_score(
            ats_result,
            "ats_score",
            "content_quality",
            "score",
        )

        story.append(
            _score_table(
                [
                    ("ATS Score", ats_score),
                    ("Completeness", completeness),
                    ("Content Quality", content_quality),
                ]
            )
        )

        story.append(Spacer(1, 8))

    # Resume quality.
    if quality_result:
        story.append(
            Paragraph(
                "Resume Quality",
                styles["heading"],
            )
        )

        quality_score = _safe_score(
            quality_result,
            "score",
        )

        story.append(
            _score_table(
                [
                    ("Resume Quality", quality_score),
                ]
            )
        )

        story.append(Spacer(1, 8))

    # Improvement readiness.
    if improvement_result:
        story.append(
            Paragraph(
                "Improvement Readiness",
                styles["heading"],
            )
        )

        improvement_score = _safe_score(
            improvement_result,
            "score",
        )

        story.append(
            _score_table(
                [
                    (
                        "Improvement Readiness",
                        improvement_score,
                    ),
                ]
            )
        )

        improvements = improvement_result.get(
            "improvements",
            [],
        )

        if improvements:
            story.append(
                Paragraph(
                    "Actionable Improvements",
                    styles["heading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    improvements,
                    styles,
                )
            )

    # Job matching.
    if job_result:
        story.append(
            Paragraph(
                "Job Compatibility",
                styles["heading"],
            )
        )

        job_score = _safe_score(
            job_result,
            "score",
        )

        keyword_coverage = _safe_score(
            job_result,
            "keyword_coverage",
        )

        story.append(
            _score_table(
                [
                    ("Job Match", job_score),
                    (
                        "Keyword Coverage",
                        keyword_coverage,
                    ),
                ]
            )
        )

        matched_skills = job_result.get(
            "matched_skills",
            [],
        )

        missing_skills = job_result.get(
            "missing_skills",
            [],
        )

        if matched_skills:
            story.append(
                Paragraph(
                    "Matched Skills",
                    styles["heading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    matched_skills,
                    styles,
                )
            )

        if missing_skills:
            story.append(
                Paragraph(
                    "Missing Skills",
                    styles["heading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    missing_skills,
                    styles,
                )
            )

    # Dashboard recommendations.
    if dashboard_result:
        recommendations = dashboard_result.get(
            "recommendations",
            [],
        )

        if recommendations:
            story.append(
                Paragraph(
                    "Priority Recommendations",
                    styles["heading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    recommendations,
                    styles,
                )
            )

    # Analytics.
    if analytics_result:
        story.append(
            Paragraph(
                "Analytics Summary",
                styles["heading"],
            )
        )

        average_score = _safe_score(
            analytics_result,
            "summary",
            "average_score",
        )

        story.append(
            _score_table(
                [
                    ("Average Analysis Score", average_score),
                ]
            )
        )

        strengths = analytics_result.get(
            "strengths",
            [],
        )

        attention_areas = analytics_result.get(
            "attention_areas",
            [],
        )

        if strengths:
            story.append(
                Paragraph(
                    "Resume Strengths",
                    styles["heading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    strengths,
                    styles,
                )
            )

        if attention_areas:
            story.append(
                Paragraph(
                    "Areas Needing Attention",
                    styles["heading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    attention_areas,
                    styles,
                )
            )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Generated by AI Resume Analyzer · v2.2",
            styles["small"],
        )
    )

    document.build(story)

    return buffer.getvalue()