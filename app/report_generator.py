"""
PDF report generator for the AI Resume Analyzer.

V2.3
- Professional PDF report
- Unified dashboard summary
- ATS analysis
- Resume quality
- Improvement readiness
- Job compatibility
- Analytics
- Recommendations
"""

from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ============================================================
# SAFE VALUE HELPERS
# ============================================================


def _safe_score(
    result: dict | None,
    *keys: str,
):
    """Safely retrieve a numeric score from a nested dictionary."""

    value = result

    for key in keys:

        if not isinstance(value, dict):
            return None

        value = value.get(key)

    if isinstance(value, (int, float)):
        return value

    return None


def _safe_list(value):
    """Return a list when the supplied value is a list."""

    if isinstance(value, list):
        return value

    return []


def _safe_text(value) -> str:
    """Convert a value into safe PDF-compatible text."""

    if value is None:
        return ""

    return escape(str(value))


# ============================================================
# PDF STYLES
# ============================================================


def _build_styles():
    """Create PDF styles used throughout the report."""

    styles = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=23,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#172554"),
            spaceAfter=6,
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
            spaceBefore=12,
            spaceAfter=8,
            textColor=colors.HexColor("#172554"),
        ),

        "subheading": ParagraphStyle(
            "ReportSubheading",
            parent=styles["Heading3"],
            fontSize=11,
            leading=14,
            spaceBefore=8,
            spaceAfter=5,
            textColor=colors.HexColor("#334155"),
        ),

        "body": ParagraphStyle(
            "ReportBody",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=14,
            spaceAfter=5,
            textColor=colors.HexColor("#1e293b"),
        ),

        "small": ParagraphStyle(
            "ReportSmall",
            parent=styles["BodyText"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748b"),
        ),

        "score": ParagraphStyle(
            "ReportScore",
            parent=styles["BodyText"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#3730a3"),
        ),
    }


# ============================================================
# TABLE HELPERS
# ============================================================


def _score_table(rows):
    """Create a formatted score table."""

    table_data = [
        [
            Paragraph(
                "<b>Metric</b>",
                _build_styles()["body"],
            ),
            Paragraph(
                "<b>Score</b>",
                _build_styles()["body"],
            ),
        ]
    ]

    styles = _build_styles()

    table_data = [
        [
            Paragraph(
                "<b>Metric</b>",
                styles["body"],
            ),
            Paragraph(
                "<b>Score</b>",
                styles["body"],
            ),
        ]
    ]

    for metric, score in rows:

        display_score = (
            "—"
            if score is None
            else f"{score}/100"
        )

        table_data.append(
            [
                Paragraph(
                    _safe_text(metric),
                    styles["body"],
                ),
                Paragraph(
                    display_score,
                    styles["score"],
                ),
            ]
        )

    table = Table(
        table_data,
        colWidths=[
            125 * mm,
            35 * mm,
        ],
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


def _overview_table(resume: dict, styles: dict):
    """Create the resume contact overview table."""

    rows = [
        [
            Paragraph(
                "<b>Name</b>",
                styles["body"],
            ),
            Paragraph(
                _safe_text(
                    resume.get("name")
                    or "Not detected"
                ),
                styles["body"],
            ),
        ],
        [
            Paragraph(
                "<b>Email</b>",
                styles["body"],
            ),
            Paragraph(
                _safe_text(
                    resume.get("email")
                    or "Not detected"
                ),
                styles["body"],
            ),
        ],
        [
            Paragraph(
                "<b>Phone</b>",
                styles["body"],
            ),
            Paragraph(
                _safe_text(
                    resume.get("phone")
                    or "Not detected"
                ),
                styles["body"],
            ),
        ],
    ]

    table = Table(
        rows,
        colWidths=[
            40 * mm,
            120 * mm,
        ],
    )

    table.setStyle(
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
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#f8fafc"),
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


# ============================================================
# BULLET HELPERS
# ============================================================


def _bullet_paragraphs(
    items,
    styles,
):
    """Convert recommendation strings into PDF bullets."""

    elements = []

    for item in _safe_list(items):

        text = _safe_text(item)

        if not text:
            continue

        elements.append(
            Paragraph(
                f"• {text}",
                styles["body"],
            )
        )

    return elements


# ============================================================
# REPORT GENERATION
# ============================================================


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
    Generate a complete V2.3 PDF resume analysis report.

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
        title="AI Resume Analyzer - V2.3 Report",
        author="AI Resume Analyzer",
    )

    styles = _build_styles()

    story = []

    resume = resume or {}

    # ========================================================
    # REPORT HEADER
    # ========================================================

    story.append(
        Paragraph(
            "AI Resume Analyzer",
            styles["title"],
        )
    )

    story.append(
        Paragraph(
            "Professional Resume Analysis Report · V2.3",
            styles["subtitle"],
        )
    )

    # ========================================================
    # RESUME OVERVIEW
    # ========================================================

    story.append(
        Paragraph(
            "Resume Overview",
            styles["heading"],
        )
    )

    story.append(
        _overview_table(
            resume,
            styles,
        )
    )

    story.append(
        Spacer(1, 8)
    )

    # ========================================================
    # UNIFIED DASHBOARD
    # ========================================================

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
                _safe_score(
                    dashboard_result,
                    "overall_score",
                ),
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

        if dashboard_result.get(
            "has_job_match"
        ):

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

        story.append(
            _score_table(
                dashboard_rows
            )
        )

        quick_summary = dashboard_result.get(
            "quick_summary",
            {},
        )

        if isinstance(
            quick_summary,
            dict,
        ):

            recommendation = quick_summary.get(
                "recommendation"
            )

            if recommendation:

                story.append(
                    Paragraph(
                        "Quick Recommendation",
                        styles["subheading"],
                    )
                )

                story.append(
                    Paragraph(
                        _safe_text(
                            recommendation
                        ),
                        styles["body"],
                    )
                )

        story.append(
            Spacer(1, 8)
        )

    # ========================================================
    # ATS ANALYSIS
    # ========================================================

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
                    (
                        "ATS Score",
                        ats_score,
                    ),
                    (
                        "Completeness",
                        completeness,
                    ),
                    (
                        "Content Quality",
                        content_quality,
                    ),
                ]
            )
        )

        story.append(
            Spacer(1, 8)
        )

    # ========================================================
    # RESUME QUALITY
    # ========================================================

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
                    (
                        "Resume Quality",
                        quality_score,
                    ),
                ]
            )
        )

        story.append(
            Spacer(1, 8)
        )

    # ========================================================
    # IMPROVEMENT READINESS
    # ========================================================

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
                    styles["subheading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    improvements,
                    styles,
                )
            )

    # ========================================================
    # JOB MATCHING
    # ========================================================

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
                    (
                        "Job Match",
                        job_score,
                    ),
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
                    styles["subheading"],
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
                    styles["subheading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    missing_skills,
                    styles,
                )
            )

        keyword_suggestions = job_result.get(
            "keyword_suggestions",
            [],
        )

        if keyword_suggestions:

            story.append(
                Paragraph(
                    "Keyword Suggestions",
                    styles["subheading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    keyword_suggestions,
                    styles,
                )
            )

    # ========================================================
    # PRIORITY RECOMMENDATIONS
    # ========================================================

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

    # ========================================================
    # ANALYTICS
    # ========================================================

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
                    (
                        "Average Analysis Score",
                        average_score,
                    ),
                ]
            )
        )

        metrics = analytics_result.get(
            "metrics",
            [],
        )

        if metrics:

            story.append(
                Paragraph(
                    "Analysis Metrics",
                    styles["subheading"],
                )
            )

            metric_rows = []

            for metric in _safe_list(metrics):

                if not isinstance(
                    metric,
                    dict,
                ):
                    continue

                name = metric.get(
                    "name",
                    "Metric",
                )

                score = metric.get(
                    "score"
                )

                metric_rows.append(
                    (
                        name,
                        score,
                    )
                )

            if metric_rows:

                story.append(
                    _score_table(
                        metric_rows
                    )
                )

        strengths = analytics_result.get(
            "strengths",
            [],
        )

        if strengths:

            story.append(
                Paragraph(
                    "Resume Strengths",
                    styles["subheading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    strengths,
                    styles,
                )
            )

        attention_areas = analytics_result.get(
            "attention_areas",
            [],
        )

        if attention_areas:

            story.append(
                Paragraph(
                    "Areas Needing Attention",
                    styles["subheading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    attention_areas,
                    styles,
                )
            )

    # ========================================================
    # FOOTER
    # ========================================================

    story.append(
        Spacer(1, 18)
    )

    story.append(
        Paragraph(
            "Generated by AI Resume Analyzer · V2.3",
            styles["small"],
        )
    )

    document.build(story)

    return buffer.getvalue()