"""
Resume achievement intelligence engine.

V3.2.3
- Achievement extraction
- Metric detection
- Metric classification
- Impact-signal detection
- Ranking detection
- Currency detection
- Scale detection
- Time-saving detection
- Achievement strength scoring
- Deterministic recommendations
"""

from __future__ import annotations

import re
from typing import Any


# ============================================================
# CONFIGURATION
# ============================================================

MAX_ACHIEVEMENT_SCORE = 100


# ============================================================
# METRIC TYPES
# ============================================================

METRIC_TYPE_PERCENTAGE = "percentage"
METRIC_TYPE_COUNT = "count"
METRIC_TYPE_SCALE = "scale"
METRIC_TYPE_MULTIPLIER = "multiplier"
METRIC_TYPE_CURRENCY = "currency"
METRIC_TYPE_RANKING = "ranking"
METRIC_TYPE_TIME = "time"
METRIC_TYPE_UNKNOWN = "other"


# ============================================================
# TEXT HELPERS
# ============================================================

def _text(
    value: Any,
) -> str:
    """Convert a value into normalized text."""

    if value is None:
        return ""

    if isinstance(
        value,
        (list, tuple, set),
    ):
        return " ".join(
            str(item)
            for item in value
        ).strip()

    return str(value).strip()


def _normalize_spaces(
    text: str,
) -> str:
    """Normalize repeated whitespace."""

    return " ".join(
        text.split()
    ).strip()


def _clean_bullet_prefix(
    text: str,
) -> str:
    """Remove common bullet prefixes."""

    return re.sub(
        r"^\s*[•●▪◦\-*]\s+",
        "",
        text,
    ).strip()


def _word_count(
    text: str,
) -> int:
    """Count words."""

    if not text:
        return 0

    return len(
        re.findall(
            r"\b[\w+#.-]+\b",
            text,
        )
    )


# ============================================================
# ACHIEVEMENT EXTRACTION
# ============================================================

def extract_achievements(
    text: str,
) -> list[str]:
    """
    Extract achievement lines.

    Common bullet-prefixed lines are extracted first.
    If no bullets exist, non-empty lines are treated as
    achievement candidates.
    """

    text = _text(
        text
    )

    if not text:
        return []

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    bullet_lines = [
        _clean_bullet_prefix(
            _normalize_spaces(
                line
            )
        )
        for line in lines
        if re.match(
            r"^\s*[•●▪◦\-*]\s+",
            line,
        )
    ]

    bullet_lines = [
        line
        for line in bullet_lines
        if line
    ]

    if bullet_lines:
        return bullet_lines

    return [
        _normalize_spaces(
            line
        )
        for line in lines
    ]


# ============================================================
# METRIC EXTRACTION
# ============================================================

def extract_metrics(
    achievement: str,
) -> list[str]:
    """
    Extract measurable values from an achievement.

    Supports percentages, counts, scale, currency,
    multipliers, and time measurements.
    """

    if not achievement:
        return []

    patterns = [

        # Currency
        r"[$₹€£]\s*\d+(?:\.\d+)?\s*[kKmMbBlL]?\+?",

        # Percentage
        r"\d+(?:\.\d+)?\s*(?:%|percent)",

        # Time
        r"\d+(?:\.\d+)?"
        r"\s+"
        r"(?:hours?|hrs?|days?|weeks?|months?)"
        r"(?:\s*/\s*(?:day|week|month|year))?",

        # Multiplier
        r"\d+(?:\.\d+)?\s*[xX]",

        # Scaled number
        r"\d+(?:\.\d+)?\s*[kKmMbB]\+?",

        # Number + optional plus sign followed by a word.
        #
        # Examples:
        #   5 projects
        #   500 users
        #   20 applications
        #
        r"\b\d+(?:\.\d+)?\+?"
        r"(?=\s+[A-Za-z])",

        # Standalone count with +
        r"\b\d+(?:\.\d+)?\+",
    ]

    found: list[str] = []

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            achievement,
            flags=re.IGNORECASE,
        ):

            value = match.group(0).strip()

            value = re.sub(
                r"[ \t]+",
                " ",
                value,
            )

            if value not in found:
                found.append(value)

    return found

# ============================================================
# METRIC CLASSIFICATION
# ============================================================

def classify_metric(
    metric: str,
) -> str:
    """
    Classify one metric.
    """

    value = metric.strip()

    if re.search(
        r"[$₹€£]",
        value,
    ):
        return METRIC_TYPE_CURRENCY

    if re.search(
        r"%(?!\w)|percent\b",
        value,
        re.IGNORECASE,
    ):
        return METRIC_TYPE_PERCENTAGE

    if re.search(
        r"(?:hours?|hrs?|days?|weeks?|months?)"
        r"(?:/day|/week|/month|/year)?$",
        value,
        re.IGNORECASE,
    ):
        return METRIC_TYPE_TIME

    if re.search(
        r"[xX]$",
        value,
    ):
        return METRIC_TYPE_MULTIPLIER

    if re.search(
        r"[kKmMbB]\+?$",
        value,
    ):
        return METRIC_TYPE_SCALE

    if value.endswith(
        "+"
    ):
        return METRIC_TYPE_COUNT

    if re.fullmatch(
        r"\d+(?:\.\d+)?",
        value,
    ):
        return METRIC_TYPE_COUNT

    return METRIC_TYPE_UNKNOWN


def classify_metrics(
    metrics: list[str],
) -> dict:
    """
    Classify every detected metric.
    """

    classified = []

    for metric in metrics:

        classified.append(
            {
                "value": metric,
                "type": classify_metric(
                    metric
                ),
            }
        )

    type_counts: dict[str, int] = {}

    for item in classified:

        metric_type = item[
            "type"
        ]

        type_counts[
            metric_type
        ] = (
            type_counts.get(
                metric_type,
                0,
            )
            + 1
        )

    return {
        "items": classified,
        "type_counts": type_counts,
    }


# ============================================================
# RANKING DETECTION
# ============================================================

def detect_rankings(
    achievement: str,
) -> list[str]:
    """
    Detect ranking-related achievement signals.

    Examples:

        top 10%
        top 5
        ranked 1st
        ranked first
        #1
        first place
    """

    if not achievement:
        return []

    patterns = [

        # Top percentages / positions.
        r"\btop\s+\d+(?:\.\d+)?%?",

        # Ranked ordinal / numeric position.
        r"\branked\s+#?\d+(?:st|nd|rd|th)\b",

        # Ranked plain number.
        r"\branked\s+#?\d+\b",

        # Ranked words.
        r"\branked\s+(?:first|second|third)\b",

        # Generic ordinal place.
        r"\b\d+(?:st|nd|rd|th)\s+place\b",

        # Word-based place.
        r"\bfirst\s+place\b",
        r"\bsecond\s+place\b",
        r"\bthird\s+place\b",

        # #1, #2, etc.
        r"(?<!\w)#\d+\b",
    ]

    found: list[str] = []

    for pattern in patterns:

        matches = re.finditer(
            pattern,
            achievement,
            flags=re.IGNORECASE,
        )

        for match in matches:

            value = _normalize_spaces(
                match.group(
                    0
                )
            )

            if value not in found:

                found.append(
                    value
                )

    return found


# ============================================================
# IMPACT SIGNALS
# ============================================================

IMPACT_TERMS = {
    "achieved",
    "accelerated",
    "boosted",
    "decreased",
    "delivered",
    "generated",
    "grew",
    "improved",
    "increased",
    "optimized",
    "reduced",
    "saved",
    "scaled",
    "streamlined",
}


def detect_impact_signals(
    achievement: str,
) -> list[str]:
    """
    Detect common impact-oriented language.
    """

    lower_text = achievement.lower()

    found: list[str] = []

    for term in IMPACT_TERMS:

        if re.search(
            rf"\b{re.escape(term)}\b",
            lower_text,
        ):

            found.append(
                term
            )

    return sorted(
        found
    )


# ============================================================
# TIME-SAVING DETECTION
# ============================================================

def detect_time_savings(
    achievement: str,
) -> list[str]:
    """
    Detect time-saving signals.

    Examples:

        saved 10 hours
        saved 2 days
        reduced processing time by 30%
    """

    if not achievement:
        return []

    patterns = [

        r"\bsaved\s+\d+(?:\.\d+)?\s*"
        r"(?:hours?|hrs?|days?|weeks?|months?)",

        r"\breduced\s+.*?time\s+by\s+"
        r"\d+(?:\.\d+)?\s*%",

    ]

    found: list[str] = []

    for pattern in patterns:

        matches = re.finditer(
            pattern,
            achievement,
            flags=re.IGNORECASE,
        )

        for match in matches:

            value = _normalize_spaces(
                match.group(
                    0
                )
            )

            if value not in found:

                found.append(
                    value
                )

    return found


# ============================================================
# ACHIEVEMENT STRENGTH
# ============================================================

def _has_strong_metric_type(
    classifications: dict,
) -> bool:
    """
    Return True when a meaningful achievement metric
    has been detected.
    """

    counts = classifications.get(
        "type_counts",
        {},
    )

    strong_types = {
        METRIC_TYPE_PERCENTAGE,
        METRIC_TYPE_SCALE,
        METRIC_TYPE_MULTIPLIER,
        METRIC_TYPE_CURRENCY,
        METRIC_TYPE_RANKING,
        METRIC_TYPE_TIME,
    }

    return any(
        counts.get(
            metric_type,
            0,
        ) > 0
        for metric_type
        in strong_types
    )


def calculate_achievement_score(
    achievement: str,
    metrics: dict,
    classifications: dict,
    rankings: list[str],
    impact_signals: list[str],
    time_savings: list[str],
) -> dict:
    """
    Calculate a deterministic achievement score out of 100.

    Components:

        Meaningful content    20
        Metric presence       30
        Metric quality        20
        Impact signal         20
        Ranking/time signal   10
    """

    breakdown = {}

    # --------------------------------------------------------
    # Meaningful content: 20 points
    # --------------------------------------------------------

    words = _word_count(
        achievement
    )

    if words >= 9:

        breakdown["content"] = 20

    elif words >= 6:

        breakdown["content"] = 14

    elif words > 0:

        breakdown["content"] = 7

    else:

        breakdown["content"] = 0

    # --------------------------------------------------------
    # Metric presence: 30 points
    # --------------------------------------------------------

    metric_count = metrics.get(
        "count",
        0,
    )

    if metric_count >= 2:

        breakdown["metrics"] = 30

    elif metric_count == 1:

        breakdown["metrics"] = 24

    else:

        breakdown["metrics"] = 0

    # --------------------------------------------------------
    # Metric quality: 20 points
    # --------------------------------------------------------

    has_strong_metrics = _has_strong_metric_type(
        classifications
    )

    if has_strong_metrics:

        breakdown["metric_quality"] = 20

    elif metric_count > 0:

        breakdown["metric_quality"] = 12

    else:

        breakdown["metric_quality"] = 0

    # --------------------------------------------------------
    # Impact: 20 points
    # --------------------------------------------------------

    if impact_signals:

        breakdown["impact"] = 20

    else:

        breakdown["impact"] = 5

    # --------------------------------------------------------
    # Ranking / time signal: 10 points
    # --------------------------------------------------------

    if rankings or time_savings:

        breakdown["additional_signal"] = 10

    else:

        breakdown["additional_signal"] = 0

    score = sum(
        breakdown.values()
    )

    # --------------------------------------------------------
    # Top-tier achievement recognition
    #
    # Multiple metrics + strong metric types + clear impact
    # + ranking/time evidence represents a highly measurable
    # achievement. Cap it at the full 100.
    # --------------------------------------------------------

    if (
        metric_count >= 2
        and has_strong_metrics
        and impact_signals
        and (rankings or time_savings)
    ):

        score = 100

    score = max(
        0,
        min(
            MAX_ACHIEVEMENT_SCORE,
            score,
        ),
    )

    return {
        "score": score,
        "max_score": MAX_ACHIEVEMENT_SCORE,
        "breakdown": breakdown,
    }


# ============================================================
# STATUS
# ============================================================

def achievement_status(
    score: int,
) -> str:
    """
    Convert a score to a readable status.
    """

    if score >= 85:
        return "strong"

    if score >= 70:
        return "good"

    if score >= 50:
        return "needs_attention"

    return "weak"


# ============================================================
# RECOMMENDATIONS
# ============================================================

def generate_achievement_recommendations(
    achievement: str,
    metrics: dict,
    classifications: dict,
    rankings: list[str],
    impact_signals: list[str],
    time_savings: list[str],
) -> tuple[list[str], list[str]]:
    """
    Generate achievement strengths and recommendations.
    """

    strengths: list[str] = []
    improvements: list[str] = []

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    if metrics.get(
        "count",
        0,
    ) > 0:

        strengths.append(
            "Contains measurable information."
        )

    else:

        improvements.append(
            "Add a measurable result such as a percentage, "
            "count, scale, ranking, or time saved."
        )

    # --------------------------------------------------------
    # Metric classification
    # --------------------------------------------------------

    if _has_strong_metric_type(
        classifications
    ):

        strengths.append(
            "Uses a meaningful achievement metric."
        )

    # --------------------------------------------------------
    # Impact
    # --------------------------------------------------------

    if impact_signals:

        strengths.append(
            "Communicates measurable impact or outcome."
        )

    else:

        improvements.append(
            "Explain the impact or outcome of the achievement."
        )

    # --------------------------------------------------------
    # Ranking
    # --------------------------------------------------------

    if rankings:

        strengths.append(
            "Contains ranking or competitive evidence."
        )

    # --------------------------------------------------------
    # Time savings
    # --------------------------------------------------------

    if time_savings:

        strengths.append(
            "Demonstrates time-saving or efficiency impact."
        )

    # --------------------------------------------------------
    # Specificity
    # --------------------------------------------------------

    words = _word_count(
        achievement
    )

    if words < 6:

        improvements.append(
            "Add enough context to explain what was achieved "
            "and why it mattered."
        )

    elif words < 9:

        improvements.append(
            "Add more context about the accomplishment, "
            "scope, or result."
        )

    # --------------------------------------------------------
    # Multiple metrics
    # --------------------------------------------------------

    if metrics.get(
        "count",
        0,
    ) >= 2:

        strengths.append(
            "Provides multiple measurable signals."
        )

    return (
        strengths,
        improvements,
    )


# ============================================================
# SINGLE ACHIEVEMENT ANALYSIS
# ============================================================

def analyze_achievement(
    achievement: str,
) -> dict:
    """
    Analyze one achievement completely.
    """

    cleaned = _clean_bullet_prefix(
        _normalize_spaces(
            _text(
                achievement
            )
        )
    )

    if not cleaned:

        return {
            "text": "",
            "score": 0,
            "max_score":
                MAX_ACHIEVEMENT_SCORE,
            "status": "weak",
            "metrics": {
                "count": 0,
                "values": [],
            },
            "classification": {
                "items": [],
                "type_counts": {},
            },
            "rankings": [],
            "impact_signals": [],
            "time_savings": [],
            "breakdown": {},
            "strengths": [],
            "improvements": [
                "Add meaningful achievement content."
            ],
        }

    metric_values = extract_metrics(
        cleaned
    )

    metrics = {
        "count": len(
            metric_values
        ),
        "values": metric_values,
    }

    classifications = classify_metrics(
        metric_values
    )

    rankings = detect_rankings(
        cleaned
    )

    impact_signals = (
        detect_impact_signals(
            cleaned
        )
    )

    time_savings = (
        detect_time_savings(
            cleaned
        )
    )

    score_result = (
        calculate_achievement_score(
            cleaned,
            metrics,
            classifications,
            rankings,
            impact_signals,
            time_savings,
        )
    )

    strengths, improvements = (
        generate_achievement_recommendations(
            cleaned,
            metrics,
            classifications,
            rankings,
            impact_signals,
            time_savings,
        )
    )

    return {
        "text": cleaned,

        "score": score_result[
            "score"
        ],

        "max_score": score_result[
            "max_score"
        ],

        "status": achievement_status(
            score_result[
                "score"
            ]
        ),

        "metrics": metrics,

        "classification":
            classifications,

        "rankings": rankings,

        "impact_signals":
            impact_signals,

        "time_savings":
            time_savings,

        "breakdown":
            score_result[
                "breakdown"
            ],

        "strengths": strengths,

        "improvements":
            improvements,
    }


# ============================================================
# COMPLETE ACHIEVEMENT SECTION ANALYSIS
# ============================================================

def analyze_achievement_section(
    text: str,
) -> dict:
    """
    Analyze every achievement in an achievements section.
    """

    achievements = extract_achievements(
        text
    )

    analyses = [
        analyze_achievement(
            achievement
        )
        for achievement in achievements
    ]

    scores = [
        item[
            "score"
        ]
        for item in analyses
    ]

    average_score = (
        round(
            sum(scores)
            / len(scores)
        )
        if scores
        else 0
    )

    strong_count = sum(
        1
        for item in analyses
        if item[
            "status"
        ] == "strong"
    )

    needs_attention_count = sum(
        1
        for item in analyses
        if item[
            "status"
        ]
        in {
            "needs_attention",
            "weak",
        }
    )

    measurable_count = sum(
        1
        for item in analyses
        if item[
            "metrics"
        ][
            "count"
        ] > 0
    )

    ranking_count = sum(
        1
        for item in analyses
        if item[
            "rankings"
        ]
    )

    return {
        "total": len(
            analyses
        ),

        "average_score":
            average_score,

        "strong_count":
            strong_count,

        "needs_attention_count":
            needs_attention_count,

        "measurable_count":
            measurable_count,

        "ranking_count":
            ranking_count,

        "achievements":
            analyses,
    }