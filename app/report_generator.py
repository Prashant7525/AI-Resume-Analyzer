"""
PDF report generator for the AI Resume Analyzer.

V3.2
- Professional PDF report
- Unified dashboard summary
- ATS analysis
- Resume quality
- Improvement readiness
- Job compatibility
- Keyword intelligence
- Analytics
- Recommendations
- Section intelligence
- Bullet intelligence
- Achievement intelligence
- Resume intelligence summary
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
    KeepTogether,
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

        if not isinstance(
            value,
            dict,
        ):
            return None

        value = value.get(key)

    if isinstance(
        value,
        (int, float),
    ):
        return value

    return None


def _safe_int(
    value,
    default: int = 0,
) -> int:
    """Return an integer when possible."""

    if isinstance(
        value,
        bool,
    ):
        return default

    if isinstance(
        value,
        (int, float),
    ):
        return int(round(value))

    return default


def _safe_list(
    value,
) -> list:
    """Return a list when the supplied value is list-like."""

    if isinstance(
        value,
        list,
    ):
        return value

    if isinstance(
        value,
        tuple,
    ):
        return list(value)

    return []


def _safe_dict(
    value,
) -> dict:
    """Return a dictionary or an empty dictionary."""

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


def _safe_text(
    value,
) -> str:
    """Convert a value into XML-safe PDF text."""

    if value is None:
        return ""

    return escape(
        str(value)
    )


def _display_score(
    value,
    suffix: str = "/100",
) -> str:
    """Return a human-readable score string."""

    if value is None:
        return "—"

    if isinstance(
        value,
        (int, float),
    ):
        return f"{int(round(value))}{suffix}"

    return _safe_text(
        value
    )


def _first_value(
    mapping: dict,
    *keys: str,
    default=None,
):
    """Return the first existing value from a dictionary."""

    for key in keys:

        if key in mapping:

            return mapping.get(
                key
            )

    return default


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
        "metric_label": ParagraphStyle(
            "ReportMetricLabel",
            parent=styles["BodyText"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#475569"),
        ),
        "callout": ParagraphStyle(
            "ReportCallout",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#3730a3"),
            spaceBefore=4,
            spaceAfter=6,
        ),
    }


# ============================================================
# TABLE HELPERS
# ============================================================


def _score_table(
    rows,
    styles,
):
    """Create a formatted score table."""

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
            else f"{int(round(score))}/100"
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


def _percentage_table(
    rows,
    styles,
):
    """Create a percentage-based metric table."""

    table_data = [
        [
            Paragraph(
                "<b>Metric</b>",
                styles["body"],
            ),
            Paragraph(
                "<b>Percentage</b>",
                styles["body"],
            ),
        ]
    ]

    for metric, value in rows:

        display_value = (
            "—"
            if value is None
            else f"{int(round(value))}%"
        )

        table_data.append(
            [
                Paragraph(
                    _safe_text(metric),
                    styles["body"],
                ),
                Paragraph(
                    display_value,
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


def _overview_table(
    resume: dict,
    styles,
):
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
    """Convert strings into PDF bullet paragraphs."""

    elements = []

    for item in _safe_list(items):

        if isinstance(
            item,
            dict,
        ):
            text = _first_value(
                item,
                "message",
                "recommendation",
                "reason",
                "action",
                "text",
                "content",
                default="",
            )
        else:
            text = item

        text = _safe_text(
            text
        )

        if not text:
            continue

        elements.append(
            Paragraph(
                f"• {text}",
                styles["body"],
            )
        )

    return elements


def _strength_messages(
    values,
):
    """Extract printable strength messages."""

    messages = []

    for item in _safe_list(
        values
    ):

        if isinstance(
            item,
            dict,
        ):
            value = _first_value(
                item,
                "message",
                "recommendation",
                "text",
                "label",
                default="",
            )
        else:
            value = item

        if value:
            messages.append(
                str(value)
            )

    return messages


def _recommendation_messages(
    values,
):
    """Extract printable recommendation messages."""

    messages = []

    for item in _safe_list(
        values
    ):

        if isinstance(
            item,
            dict,
        ):
            value = _first_value(
                item,
                "recommendation",
                "action",
                "reason",
                "message",
                "text",
                default="",
            )
        else:
            value = item

        if value:
            messages.append(
                str(value)
            )

    return messages


# ============================================================
# V3.2 INTELLIGENCE TABLE HELPERS
# ============================================================


def _intelligence_component_table(
    components: dict,
    styles,
):
    """Build the V3.2 component summary table."""

    rows = []

    labels = {
        "sections": "Section Intelligence",
        "bullets": "Bullet Intelligence",
        "achievements": "Achievement Intelligence",
    }

    for key, label in labels.items():

        component = _safe_dict(
            components.get(
                key
            )
        )

        score = _first_value(
            component,
            "score",
            "average_score",
            default=None,
        )

        rows.append(
            (
                label,
                score,
            )
        )

    return _score_table(
        rows,
        styles,
    )


def _section_intelligence_table(
    section_intelligence: dict,
    styles,
):
    """Build a compact section intelligence table."""

    sections = _safe_dict(
        section_intelligence.get(
            "sections"
        )
    )

    rows = []

    for section_name, section in sections.items():

        if not isinstance(
            section,
            dict,
        ):
            continue

        score = _first_value(
            section,
            "score",
            "intelligence_score",
            default=None,
        )

        status = _first_value(
            section,
            "status",
            default="",
        )

        label = (
            str(section_name)
            .replace(
                "_",
                " ",
            )
            .title()
        )

        if status:
            label = (
                f"{label} "
                f"({str(status).replace('_', ' ').title()})"
            )

        rows.append(
            (
                label,
                score,
            )
        )

    return (
        _score_table(
            rows,
            styles,
        )
        if rows
        else None
    )


def _achievement_summary_table(
    achievement_intelligence: dict,
    styles,
):
    """Build a compact achievement intelligence table."""

    rows = [
        (
            "Average Achievement Score",
            _first_value(
                achievement_intelligence,
                "average_score",
                "score",
                default=None,
            ),
        ),
        (
            "Achievements Analyzed",
            _first_value(
                achievement_intelligence,
                "total",
                "total_achievements",
                default=None,
            ),
        ),
        (
            "Measurable Achievements",
            _first_value(
                achievement_intelligence,
                "measurable_count",
                default=None,
            ),
        ),
        (
            "Ranking Signals",
            _first_value(
                achievement_intelligence,
                "ranking_count",
                default=None,
            ),
        ),
        (
            "Strong Achievements",
            _first_value(
                achievement_intelligence,
                "strong_count",
                default=None,
            ),
        ),
        (
            "Needs Attention",
            _first_value(
                achievement_intelligence,
                "needs_attention_count",
                default=None,
            ),
        ),
    ]

    table_data = [
        [
            Paragraph(
                "<b>Metric</b>",
                styles["body"],
            ),
            Paragraph(
                "<b>Value</b>",
                styles["body"],
            ),
        ]
    ]

    for metric, value in rows:

        if value is None:
            display = "—"
        elif metric in {
            "Average Achievement Score",
        }:
            display = _display_score(
                value
            )
        else:
            display = str(
                value
            )

        table_data.append(
            [
                Paragraph(
                    _safe_text(
                        metric
                    ),
                    styles["body"],
                ),
                Paragraph(
                    _safe_text(
                        display
                    ),
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
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e2e8f0"),
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT",
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


def _bullet_summary_table(
    bullet_intelligence: dict,
    styles,
):
    """Build a compact bullet intelligence table."""

    rows = [
        (
            "Average Bullet Score",
            _first_value(
                bullet_intelligence,
                "average_score",
                default=None,
            ),
        ),
        (
            "Bullets Analyzed",
            _first_value(
                bullet_intelligence,
                "total_bullets",
                default=None,
            ),
        ),
        (
            "Strong Bullets",
            _first_value(
                bullet_intelligence,
                "strong_bullets",
                default=None,
            ),
        ),
        (
            "Needs Attention",
            _first_value(
                bullet_intelligence,
                "needs_attention_bullets",
                default=None,
            ),
        ),
    ]

    table_data = [
        [
            Paragraph(
                "<b>Metric</b>",
                styles["body"],
            ),
            Paragraph(
                "<b>Value</b>",
                styles["body"],
            ),
        ]
    ]

    for metric, value in rows:

        if value is None:
            display = "—"
        elif metric == "Average Bullet Score":
            display = _display_score(
                value
            )
        else:
            display = str(
                value
            )

        table_data.append(
            [
                Paragraph(
                    _safe_text(metric),
                    styles["body"],
                ),
                Paragraph(
                    _safe_text(display),
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
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e2e8f0"),
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT",
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
# V3.2 INTELLIGENCE DETAILS
# ============================================================


def _append_section_intelligence(
    story,
    quality_result,
    styles,
):
    """Append V3.2 section intelligence."""

    intelligence = _safe_dict(
        quality_result.get(
            "section_intelligence"
        )
    )

    if not intelligence:
        return

    story.append(
        Paragraph(
            "V3.2 Section Intelligence",
            styles["heading"],
        )
    )

    sections = _safe_dict(
        intelligence.get(
            "sections"
        )
    )

    section_scores = []

    for section in sections.values():

        if not isinstance(
            section,
            dict,
        ):
            continue

        score = _first_value(
            section,
            "score",
            "intelligence_score",
            default=None,
        )

        if isinstance(
            score,
            (int, float),
        ):
            section_scores.append(
                float(score)
            )

    calculated_average = (
        round(
            sum(section_scores)
            / len(section_scores)
        )
        if section_scores
        else None
    )

    section_rows = [
        (
            "Section Intelligence",
            _first_value(
                intelligence,
                "score",
                "intelligence_score",
                default=None,
            ),
        ),
        (
            "Sections Present",
            _first_value(
                intelligence,
                "section_count",
                "present_count",
                default=None,
            ),
        ),
        (
            "Total Sections",
            _first_value(
                intelligence,
                "total_sections",
                default=None,
            ),
        ),
        (
            "Coverage",
            _first_value(
                intelligence,
                "coverage_score",
                default=None,
            ),
        ),
        (
            "Average Section Score",
            _first_value(
                intelligence,
                "average_score",
                default=calculated_average,
            ),
        ),
    ]

    table_data = [
        [
            Paragraph(
                "<b>Metric</b>",
                styles["body"],
            ),
            Paragraph(
                "<b>Value</b>",
                styles["body"],
            ),
        ]
    ]

    for metric, value in section_rows:

        if value is None:
            display = "—"
        elif metric in {
            "Section Intelligence",
            "Coverage",
            "Average Section Score",
        }:
            display = _display_score(
                value
            )
        else:
            display = str(
                value
            )

        table_data.append(
            [
                Paragraph(
                    _safe_text(metric),
                    styles["body"],
                ),
                Paragraph(
                    _safe_text(display),
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
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e2e8f0"),
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT",
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

    story.append(
        table
    )

    section_table = (
        _section_intelligence_table(
            intelligence,
            styles,
        )
    )

    if section_table:

        story.append(
            Paragraph(
                "Section Scores",
                styles["subheading"],
            )
        )

        story.append(
            section_table
        )

    strengths = _strength_messages(
        intelligence.get(
            "strengths"
        )
    )

    if strengths:

        story.append(
            Paragraph(
                "Section Strengths",
                styles["subheading"],
            )
        )

        story.extend(
            _bullet_paragraphs(
                strengths,
                styles,
            )
        )

    recommendations = _recommendation_messages(
        intelligence.get(
            "recommendations"
        )
        or intelligence.get(
            "improvements"
        )
        or intelligence.get(
            "needs_attention"
        )
    )

    if recommendations:

        story.append(
            Paragraph(
                "Section Recommendations",
                styles["subheading"],
            )
        )

        story.extend(
            _bullet_paragraphs(
                recommendations,
                styles,
            )
        )


def _append_bullet_intelligence(
    story,
    quality_result,
    styles,
):
    """Append V3.2 bullet intelligence."""

    intelligence = _safe_dict(
        quality_result.get(
            "bullet_intelligence"
        )
    )

    if not intelligence:
        return

    story.append(
        Paragraph(
            "V3.2 Bullet Intelligence",
            styles["heading"],
        )
    )

    story.append(
        _bullet_summary_table(
            intelligence,
            styles,
        )
    )

    sections = _safe_dict(
        intelligence.get(
            "sections"
        )
    )

    for section_name, section in sections.items():

        if not isinstance(
            section,
            dict,
        ):
            continue

        label = (
            section_name
            .replace(
                "_",
                " ",
            )
            .title()
        )

        story.append(
            Paragraph(
                label,
                styles["subheading"],
            )
        )

        summary_rows = [
            (
                "Average Score",
                _first_value(
                    section,
                    "average_score",
                    default=None,
                ),
            ),
            (
                "Bullets",
                _first_value(
                    section,
                    "total",
                    default=None,
                ),
            ),
            (
                "Strong Bullets",
                _first_value(
                    section,
                    "strong_count",
                    default=None,
                ),
            ),
            (
                "Needs Attention",
                _first_value(
                    section,
                    "needs_attention_count",
                    default=None,
                ),
            ),
        ]

        table_data = [
            [
                Paragraph(
                    "<b>Metric</b>",
                    styles["body"],
                ),
                Paragraph(
                    "<b>Value</b>",
                    styles["body"],
                ),
            ]
        ]

        for metric, value in summary_rows:

            if value is None:
                display = "—"
            elif metric == "Average Score":
                display = _display_score(
                    value
                )
            else:
                display = str(
                    value
                )

            table_data.append(
                [
                    Paragraph(
                        _safe_text(metric),
                        styles["body"],
                    ),
                    Paragraph(
                        _safe_text(display),
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
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#f8fafc"),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#e2e8f0"),
                    ),
                    (
                        "ALIGN",
                        (1, 0),
                        (1, -1),
                        "RIGHT",
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
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(
            table
        )

        bullets = _safe_list(
            section.get(
                "bullets"
            )
        )

        for index, bullet in enumerate(
            bullets,
            start=1,
        ):

            if not isinstance(
                bullet,
                dict,
            ):
                continue

            text = _first_value(
                bullet,
                "text",
                "content",
                "bullet",
                "value",
                default="",
            )

            score = _first_value(
                bullet,
                "score",
                "bullet_score",
                default=None,
            )

            status = _first_value(
                bullet,
                "status",
                default="",
            )

            label = (
                f"Bullet {index}"
            )

            if status:
                label += (
                    " · "
                    + str(status)
                    .replace(
                        "_",
                        " ",
                    )
                    .title()
                )

            story.append(
                Paragraph(
                    f"<b>{_safe_text(label)}</b>",
                    styles["body"],
                )
            )

            if text:

                story.append(
                    Paragraph(
                        _safe_text(
                            text
                        ),
                        styles["body"],
                    )
                )

            if score is not None:

                story.append(
                    Paragraph(
                        f"Score: "
                        f"{_safe_text(_display_score(score))}",
                        styles["score"],
                    )
                )

            strengths = _strength_messages(
                bullet.get(
                    "strengths"
                )
            )

            if strengths:

                story.extend(
                    _bullet_paragraphs(
                        strengths,
                        styles,
                    )
                )

            improvements = _recommendation_messages(
                bullet.get(
                    "improvements"
                )
                or bullet.get(
                    "recommendations"
                )
            )

            if improvements:

                story.extend(
                    _bullet_paragraphs(
                        improvements,
                        styles,
                    )
                )


def _append_achievement_intelligence(
    story,
    quality_result,
    styles,
):
    """Append V3.2 achievement intelligence."""

    intelligence = _safe_dict(
        quality_result.get(
            "achievement_intelligence"
        )
    )

    if not intelligence:
        return

    story.append(
        Paragraph(
            "V3.2 Achievement Intelligence",
            styles["heading"],
        )
    )

    story.append(
        _achievement_summary_table(
            intelligence,
            styles,
        )
    )

    achievements = _safe_list(
        intelligence.get(
            "achievements"
        )
    )

    for index, achievement in enumerate(
        achievements,
        start=1,
    ):

        if not isinstance(
            achievement,
            dict,
        ):
            continue

        text = _first_value(
            achievement,
            "text",
            "content",
            "achievement",
            "value",
            default="",
        )

        score = _first_value(
            achievement,
            "score",
            "achievement_score",
            default=None,
        )

        status = _first_value(
            achievement,
            "status",
            default="",
        )

        heading = (
            f"Achievement {index}"
        )

        if status:
            heading += (
                " · "
                + str(status)
                .replace(
                    "_",
                    " ",
                )
                .title()
            )

        story.append(
            Paragraph(
                f"<b>{_safe_text(heading)}</b>",
                styles["body"],
            )
        )

        if text:

            story.append(
                Paragraph(
                    _safe_text(
                        text
                    ),
                    styles["body"],
                )
            )

        if score is not None:

            story.append(
                Paragraph(
                    f"Score: "
                    f"{_safe_text(_display_score(score))}",
                    styles["score"],
                )
            )

        strengths = _strength_messages(
            achievement.get(
                "strengths"
            )
        )

        if strengths:

            story.append(
                Paragraph(
                    "Strengths",
                    styles["subheading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    strengths,
                    styles,
                )
            )

        improvements = _recommendation_messages(
            achievement.get(
                "improvements"
            )
            or achievement.get(
                "recommendations"
            )
        )

        if improvements:

            story.append(
                Paragraph(
                    "Improvements",
                    styles["subheading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    improvements,
                    styles,
                )
            )

        metrics = _safe_dict(
            achievement.get(
                "metrics"
            )
        )

        metric_values = _safe_list(
            metrics.get(
                "values"
            )
        )

        if metric_values:

            story.append(
                Paragraph(
                    "Detected Metrics",
                    styles["subheading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    metric_values,
                    styles,
                )
            )

        classification = _safe_dict(
            achievement.get(
                "classification"
            )
        )

        classification_items = _safe_list(
            classification.get(
                "items"
            )
        )

        if classification_items:

            story.append(
                Paragraph(
                    "Metric Types",
                    styles["subheading"],
                )
            )

            classification_text = []

            for item in classification_items:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                value = item.get(
                    "value",
                    "",
                )

                item_type = item.get(
                    "type",
                    "",
                )

                if value:

                    if item_type:
                        classification_text.append(
                            f"{value} · "
                            f"{str(item_type).title()}"
                        )
                    else:
                        classification_text.append(
                            str(value)
                        )

            story.extend(
                _bullet_paragraphs(
                    classification_text,
                    styles,
                )
            )


def _append_intelligence_summary(
    story,
    quality_result,
    styles,
):
    """Append the overall V3.2 intelligence summary."""

    intelligence = _safe_dict(
        quality_result.get(
            "intelligence_summary"
        )
    )

    if not intelligence:
        return

    story.append(
        Paragraph(
            "V3.2 Resume Intelligence Summary",
            styles["heading"],
        )
    )

    overall_score = _first_value(
        intelligence,
        "score",
        "intelligence_score",
        default=None,
    )

    max_score = _first_value(
        intelligence,
        "max_score",
        default=100,
    )

    score_display = (
        "—"
        if overall_score is None
        else (
            f"{int(round(overall_score))}/"
            f"{int(round(max_score))}"
        )
    )

    story.append(
        Paragraph(
            f"<b>Overall Intelligence Score:</b> "
            f"{_safe_text(score_display)}",
            styles["callout"],
        )
    )

    components = _safe_dict(
        intelligence.get(
            "components"
        )
    )

    if components:

        story.append(
            _intelligence_component_table(
                components,
                styles,
            )
        )

    summary = _first_value(
        intelligence,
        "summary",
        "message",
        "overview",
        default="",
    )

    if summary:

        story.append(
            Paragraph(
                "Intelligence Summary",
                styles["subheading"],
            )
        )

        story.append(
            Paragraph(
                _safe_text(summary),
                styles["body"],
            )
        )

    strengths = _strength_messages(
        intelligence.get(
            "strengths"
        )
    )

    if strengths:

        story.append(
            Paragraph(
                "Top Strengths",
                styles["subheading"],
            )
        )

        story.extend(
            _bullet_paragraphs(
                strengths,
                styles,
            )
        )

    recommendations = _recommendation_messages(
        intelligence.get(
            "recommendations"
        )
        or intelligence.get(
            "improvements"
        )
        or intelligence.get(
            "next_steps"
        )
    )

    if recommendations:

        story.append(
            Paragraph(
                "Recommended Actions",
                styles["subheading"],
            )
        )

        story.extend(
            _bullet_paragraphs(
                recommendations,
                styles,
            )
        )


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
    Generate the complete V3.2 PDF report.

    Existing V2.x/V3.1 report sections are preserved while
    V3.2 intelligence sections are added when available.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=(
            "AI Resume Analyzer - V3.2 Report"
        ),
        author="AI Resume Analyzer",
        subject=(
            "AI Resume Analyzer V3.2 "
            "Professional Resume Analysis"
        ),
    )

    styles = _build_styles()

    story = []

    resume = resume or {}

    # ========================================================
    # HEADER
    # ========================================================

    story.append(
        Paragraph(
            "AI Resume Analyzer",
            styles["title"],
        )
    )

    story.append(
        Paragraph(
            "Professional Resume Analysis Report · V3.2",
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
        Spacer(
            1,
            8,
        )
    )

    # ========================================================
    # DASHBOARD
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
                dashboard_rows,
                styles,
            )
        )

        quick_summary = _safe_dict(
            dashboard_result.get(
                "quick_summary"
            )
        )

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
            Spacer(
                1,
                8,
            )
        )

    # ========================================================
    # V3.2 INTELLIGENCE SUMMARY
    # ========================================================

    if quality_result:

        _append_intelligence_summary(
            story,
            quality_result,
            styles,
        )

    # ========================================================
    # ATS
    # ========================================================

    if ats_result:

        story.append(
            Paragraph(
                "ATS Analysis",
                styles["heading"],
            )
        )

        story.append(
            _score_table(
                [
                    (
                        "ATS Score",
                        _safe_score(
                            ats_result,
                            "ats_score",
                            "score",
                        ),
                    ),
                    (
                        "Completeness",
                        _safe_score(
                            ats_result,
                            "ats_score",
                            "completeness",
                            "score",
                        ),
                    ),
                    (
                        "Content Quality",
                        _safe_score(
                            ats_result,
                            "ats_score",
                            "content_quality",
                            "score",
                        ),
                    ),
                ],
                styles,
            )
        )

        story.append(
            Spacer(
                1,
                8,
            )
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

        story.append(
            _score_table(
                [
                    (
                        "Resume Quality",
                        _safe_score(
                            quality_result,
                            "score",
                        ),
                    ),
                ],
                styles,
            )
        )

        breakdown = _safe_dict(
            quality_result.get(
                "breakdown"
            )
        )

        breakdown_rows = []

        breakdown_maximums = {
            "length": 15,
            "sections": 15,
            "bullets": 10,
            "achievements": 10,
            "contact": 10,
            "structure": 10,
        }

        for label, key in [
            (
                "Length",
                "length",
            ),
            (
                "Sections",
                "sections",
            ),
            (
                "Bullets",
                "bullets",
            ),
            (
                "Achievements",
                "achievements",
            ),
            (
                "Contact",
                "contact",
            ),
            (
                "Structure",
                "structure",
            ),
        ]:

            value = breakdown.get(
                key
            )

            maximum = breakdown_maximums.get(
                key
            )

            if value is not None:

                breakdown_rows.append(
                    (
                        label,
                        f"{int(round(value))}/{maximum}",
                    )
                )

        if breakdown_rows:

            story.append(
                Paragraph(
                    "Quality Breakdown",
                    styles["subheading"],
                )
            )

            breakdown_table_data = [
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

            for metric, value in breakdown_rows:

                breakdown_table_data.append(
                    [
                        Paragraph(
                            _safe_text(metric),
                            styles["body"],
                        ),
                        Paragraph(
                            _safe_text(value),
                            styles["score"],
                        ),
                    ]
                )

            breakdown_table = Table(
                breakdown_table_data,
                colWidths=[
                    125 * mm,
                    35 * mm,
                ],
                repeatRows=1,
            )

            breakdown_table.setStyle(
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

            story.append(
                breakdown_table
            )

        story.append(
            Spacer(
                1,
                8,
            )
        )

    # ========================================================
    # V3.2 SECTION INTELLIGENCE
    # ========================================================

    if quality_result:

        _append_section_intelligence(
            story,
            quality_result,
            styles,
        )

    # ========================================================
    # V3.2 BULLET INTELLIGENCE
    # ========================================================

    if quality_result:

        _append_bullet_intelligence(
            story,
            quality_result,
            styles,
        )

    # ========================================================
    # V3.2 ACHIEVEMENT INTELLIGENCE
    # ========================================================

    if quality_result:

        _append_achievement_intelligence(
            story,
            quality_result,
            styles,
        )

    # ========================================================
    # IMPROVEMENTS
    # ========================================================

    if improvement_result:

        story.append(
            Paragraph(
                "Improvement Readiness",
                styles["heading"],
            )
        )

        story.append(
            _score_table(
                [
                    (
                        "Improvement Readiness",
                        _safe_score(
                            improvement_result,
                            "score",
                        ),
                    ),
                ],
                styles,
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

        priority_improvements = (
            improvement_result.get(
                "priority_improvements",
                [],
            )
        )

        if priority_improvements:

            story.append(
                Paragraph(
                    "Priority Recommendations",
                    styles["subheading"],
                )
            )

            story.extend(
                _bullet_paragraphs(
                    priority_improvements,
                    styles,
                )
            )

    # ========================================================
    # JOB MATCH
    # ========================================================

    if job_result:

        story.append(
            Paragraph(
                "Job Compatibility",
                styles["heading"],
            )
        )

        story.append(
            _score_table(
                [
                    (
                        "Job Match",
                        _safe_score(
                            job_result,
                            "score",
                        ),
                    ),
                ],
                styles,
            )
        )

        keyword_coverage = _safe_score(
            job_result,
            "keyword_coverage",
        )

        story.append(
            _percentage_table(
                [
                    (
                        "Keyword Coverage",
                        keyword_coverage,
                    ),
                ],
                styles,
            )
        )

        matched_skills = job_result.get(
            "matched_skills",
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

        missing_skills = job_result.get(
            "missing_skills",
            [],
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
    # DASHBOARD RECOMMENDATIONS
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

        story.append(
            _score_table(
                [
                    (
                        "Average Analysis Score",
                        _safe_score(
                            analytics_result,
                            "summary",
                            "average_score",
                        ),
                    ),
                ],
                styles,
            )
        )

        metrics = analytics_result.get(
            "metrics",
            [],
        )

        metric_rows = []

        for metric in _safe_list(
            metrics
        ):

            if not isinstance(
                metric,
                dict,
            ):
                continue

            metric_rows.append(
                (
                    metric.get(
                        "name",
                        "Metric",
                    ),
                    metric.get(
                        "score"
                    ),
                )
            )

        if metric_rows:

            story.append(
                Paragraph(
                    "Analysis Metrics",
                    styles["subheading"],
                )
            )

            story.append(
                _score_table(
                    metric_rows,
                    styles,
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
        Spacer(
            1,
            18,
        )
    )

    story.append(
        Paragraph(
            "Generated by AI Resume Analyzer · V3.2",
            styles["small"],
        )
    )

    document.build(
        story
    )

    return buffer.getvalue()