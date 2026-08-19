"""
Resume bullet quality analyzer.

V3.2.2
- Individual bullet extraction
- Action verb analysis
- Specificity analysis
- Technical detail detection
- Metric detection
- Impact/outcome detection
- Weak/generic phrase detection
- Bullet scoring
- Deterministic recommendations
"""

from __future__ import annotations

import re
from typing import Any


# ============================================================
# CONFIGURATION
# ============================================================

MAX_BULLET_SCORE = 100


# Strong action verbs commonly used in professional resumes.
STRONG_ACTION_VERBS = {
    "achieved",
    "analyzed",
    "architected",
    "automated",
    "built",
    "created",
    "designed",
    "developed",
    "deployed",
    "engineered",
    "implemented",
    "improved",
    "increased",
    "integrated",
    "launched",
    "led",
    "optimized",
    "reduced",
    "refactored",
    "resolved",
    "scaled",
    "streamlined",
    "tested",
}


# Generic / weak opening verbs.
WEAK_ACTION_VERBS = {
    "did",
    "helped",
    "handled",
    "involved",
    "participated",
    "responsible",
    "worked",
    "worked-on",
}


# Generic phrases that often produce weak resume bullets.
WEAK_PHRASES = {
    "worked on",
    "helped with",
    "responsible for",
    "involved in",
    "participated in",
    "did work on",
    "was responsible for",
    "assisted with",
}


# Common technology / technical detail signals.
TECHNICAL_KEYWORDS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "flask",
    "django",
    "fastapi",
    "react",
    "angular",
    "vue",
    "node",
    "node.js",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "git",
    "github",
    "linux",
    "api",
    "rest",
    "restful",
    "graphql",
    "html",
    "css",
    "tensorflow",
    "pytorch",
    "pandas",
    "numpy",
}


# Outcome / impact verbs and phrases.
IMPACT_TERMS = {
    "increased",
    "decreased",
    "reduced",
    "improved",
    "saved",
    "generated",
    "grew",
    "accelerated",
    "optimized",
    "streamlined",
    "boosted",
    "delivered",
    "achieved",
    "enabled",
}


# ============================================================
# TEXT HELPERS
# ============================================================

def _text(value: Any) -> str:
    """
    Convert a value to normalized text.
    """

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


def _normalize_spaces(text: str) -> str:
    """
    Normalize repeated whitespace.
    """

    return " ".join(
        text.split()
    ).strip()


def _clean_bullet_prefix(text: str) -> str:
    """
    Remove common resume bullet prefixes.
    """

    return re.sub(
        r"^\s*[•●▪◦\-*]\s+",
        "",
        text,
    ).strip()


def _word_count(text: str) -> int:
    """
    Count words in a bullet.
    """

    if not text:
        return 0

    return len(
        re.findall(
            r"\b[\w+#.-]+\b",
            text,
        )
    )


def _tokenize(text: str) -> list[str]:
    """
    Return lowercase word tokens.
    """

    return re.findall(
        r"[A-Za-z][A-Za-z0-9+#.-]*",
        text.lower(),
    )


# ============================================================
# BULLET EXTRACTION
# ============================================================

def extract_bullets(
    text: str,
) -> list[str]:
    """
    Extract bullet-point lines from section text.

    Only lines using common bullet markers are returned.
    """

    text = _text(text)

    if not text:
        return []

    bullets: list[str] = []

    for line in text.splitlines():

        stripped = line.strip()

        if not stripped:
            continue

        if re.match(
            r"^[•●▪◦\-*]\s+",
            stripped,
        ):

            cleaned = _clean_bullet_prefix(
                stripped
            )

            cleaned = _normalize_spaces(
                cleaned
            )

            if cleaned:
                bullets.append(
                    cleaned
                )

    return bullets


# ============================================================
# ACTION VERB ANALYSIS
# ============================================================

def get_first_word(
    bullet: str,
) -> str:
    """
    Return the first meaningful word of a bullet.
    """

    tokens = _tokenize(
        bullet
    )

    return (
        tokens[0]
        if tokens
        else ""
    )


def analyze_action_verb(
    bullet: str,
) -> dict:
    """
    Analyze the opening action verb.
    """

    first_word = get_first_word(
        bullet
    )

    if not first_word:

        return {
            "first_word": "",
            "quality": "missing",
            "is_strong": False,
            "is_weak": False,
        }

    normalized = first_word.lower()

    if normalized in STRONG_ACTION_VERBS:

        return {
            "first_word": first_word,
            "quality": "strong",
            "is_strong": True,
            "is_weak": False,
        }

    if normalized in WEAK_ACTION_VERBS:

        return {
            "first_word": first_word,
            "quality": "weak",
            "is_strong": False,
            "is_weak": True,
        }

    return {
        "first_word": first_word,
        "quality": "neutral",
        "is_strong": False,
        "is_weak": False,
    }


# ============================================================
# SPECIFICITY ANALYSIS
# ============================================================

def analyze_specificity(
    bullet: str,
) -> dict:
    """
    Analyze how specific the bullet is.

    Signals include:

    - technical details
    - numbers
    - named systems/tools
    - longer descriptive content
    """

    text = _normalize_spaces(
        bullet
    )

    words = _word_count(
        text
    )

    has_number = bool(
        re.search(
            r"\b\d+(?:\.\d+)?\s*"
            r"(?:%|percent|x|k|m|b)?\b",
            text,
            re.IGNORECASE,
        )
    )

    technical_matches = []

    lower_text = text.lower()

    for keyword in TECHNICAL_KEYWORDS:

        if re.search(
            rf"(?<!\w){re.escape(keyword)}(?!\w)",
            lower_text,
        ):
            technical_matches.append(
                keyword
            )

    if words >= 12:
        detail_level = "high"

    elif words >= 7:
        detail_level = "medium"

    else:
        detail_level = "low"

    return {
        "word_count": words,
        "has_number": has_number,
        "technical_keywords": sorted(
            technical_matches
        ),
        "technical_detail": bool(
            technical_matches
        ),
        "detail_level": detail_level,
    }


# ============================================================
# METRIC ANALYSIS
# ============================================================

def extract_metrics(
    bullet: str,
) -> list[str]:
    """
    Extract common measurable values from a bullet.

    Supported examples:

        35%
        12.5%
        20 percent
        500+
        1000+
        2x
        2.5x
        50K
        2.5M
        $50K
        ₹10L
        €20M
        £5B
    """

    if not bullet:
        return []

    patterns = [
        # ----------------------------------------------------
        # Currency values
        # ----------------------------------------------------
        #
        # $50K
        # ₹10L
        # €20M
        # £5B
        #
        r"[$₹€£]\s*\d+(?:\.\d+)?\s*[kKmMbBlL]?\+?",

        # ----------------------------------------------------
        # Percentages
        # ----------------------------------------------------
        #
        # 35%
        # 12.5%
        # 20 percent
        #
        r"\d+(?:\.\d+)?\s*(?:%|percent)",

        # ----------------------------------------------------
        # Multipliers
        # ----------------------------------------------------
        #
        # 2x
        # 3.5x
        #
        r"\d+(?:\.\d+)?\s*[xX]",

        # ----------------------------------------------------
        # Scaled numbers
        # ----------------------------------------------------
        #
        # 50K
        # 2.5M
        # 10B
        # 500K+
        #
        r"\d+(?:\.\d+)?\s*[kKmMbB]\+?",

        # ----------------------------------------------------
        # Plain measurable counts with +
        # ----------------------------------------------------
        #
        # 500+
        # 1000+
        #
        r"\d+(?:\.\d+)?\+",
    ]

    found: list[str] = []

    for pattern in patterns:

        matches = re.finditer(
            pattern,
            bullet,
            flags=re.IGNORECASE,
        )

        for match in matches:

            value = match.group(
                0
            ).strip()

            # Remove spaces inside values:
            #
            # "$ 50K" -> "$50K"
            # "12.5 %" -> "12.5%"
            #
            value = re.sub(
                r"\s+",
                "",
                value,
            )

            if value not in found:

                found.append(
                    value
                )

    return found


def analyze_metrics(
    bullet: str,
) -> dict:
    """
    Analyze measurable information.
    """

    metrics = extract_metrics(
        bullet
    )

    return {
        "has_metrics": bool(
            metrics
        ),
        "metrics": metrics,
        "count": len(metrics),
    }


# ============================================================
# IMPACT ANALYSIS
# ============================================================

def analyze_impact(
    bullet: str,
) -> dict:
    """
    Analyze whether the bullet communicates impact or outcome.
    """

    lower_text = bullet.lower()

    impact_terms_found = []

    for term in IMPACT_TERMS:

        if re.search(
            rf"\b{re.escape(term)}\b",
            lower_text,
        ):

            impact_terms_found.append(
                term
            )

    # Metrics are also a useful impact signal.
    has_metrics = bool(
        extract_metrics(
            bullet
        )
    )

    has_impact = bool(
        impact_terms_found
    ) or has_metrics

    return {
        "has_impact": has_impact,
        "impact_terms": sorted(
            impact_terms_found
        ),
        "has_metrics": has_metrics,
    }


# ============================================================
# WEAK PHRASE ANALYSIS
# ============================================================

def analyze_weak_phrasing(
    bullet: str,
) -> dict:
    """
    Detect generic or weak phrasing.
    """

    lower_text = bullet.lower()

    matched_phrases = []

    for phrase in WEAK_PHRASES:

        if phrase in lower_text:

            matched_phrases.append(
                phrase
            )

    return {
        "has_weak_phrase": bool(
            matched_phrases
        ),
        "phrases": sorted(
            matched_phrases
        ),
    }


# ============================================================
# BULLET SCORE
# ============================================================

def calculate_bullet_score(
    action: dict,
    specificity: dict,
    metrics: dict,
    impact: dict,
    weak_phrasing: dict,
) -> dict:
    """
    Calculate a deterministic bullet quality score out of 100.

    Components:

        Action verb       25
        Specificity       20
        Technical detail  15
        Metrics           20
        Impact/outcome    20
    """

    breakdown = {}

    # --------------------------------------------------------
    # Action verb: 25 points
    # --------------------------------------------------------

    if action["is_strong"]:

        breakdown["action_verb"] = 25

    elif action["is_weak"]:

        breakdown["action_verb"] = 5

    else:

        breakdown["action_verb"] = 15

    # --------------------------------------------------------
    # Specificity: 20 points
    # --------------------------------------------------------

    if specificity["detail_level"] == "high":

        breakdown["specificity"] = 20

    elif specificity["detail_level"] == "medium":

        breakdown["specificity"] = 14

    else:

        breakdown["specificity"] = 6

    # --------------------------------------------------------
    # Technical detail: 15 points
    # --------------------------------------------------------

    if specificity["technical_detail"]:

        breakdown["technical_detail"] = 15

    else:

        breakdown["technical_detail"] = 7

    # --------------------------------------------------------
    # Metrics: 20 points
    # --------------------------------------------------------

    if metrics["has_metrics"]:

        breakdown["metrics"] = 20

    else:

        breakdown["metrics"] = 0

    # --------------------------------------------------------
    # Impact: 20 points
    # --------------------------------------------------------

    if impact["has_impact"]:

        breakdown["impact"] = 20

    else:

        breakdown["impact"] = 5

    # --------------------------------------------------------
    # Weak phrasing penalty
    # --------------------------------------------------------

    penalty = (
        10
        if weak_phrasing["has_weak_phrase"]
        else 0
    )

    raw_score = (
        sum(
            breakdown.values()
        )
        - penalty
    )

    score = max(
        0,
        min(
            MAX_BULLET_SCORE,
            raw_score,
        ),
    )

    return {
        "score": score,
        "max_score": MAX_BULLET_SCORE,
        "breakdown": breakdown,
        "penalty": penalty,
    }


# ============================================================
# STATUS
# ============================================================

def _score_status(
    score: int,
) -> str:
    """
    Convert a numeric score to a readable status.
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

def generate_bullet_recommendations(
    action: dict,
    specificity: dict,
    metrics: dict,
    impact: dict,
    weak_phrasing: dict,
) -> tuple[list[str], list[str]]:
    """
    Generate deterministic bullet strengths and improvements.
    """

    strengths: list[str] = []
    improvements: list[str] = []

    # --------------------------------------------------------
    # Action verb
    # --------------------------------------------------------

    if action["is_strong"]:

        strengths.append(
            "Uses a strong action verb."
        )

    elif action["is_weak"]:

        improvements.append(
            "Replace the generic opening with a stronger "
            "action verb."
        )

    else:

        improvements.append(
            "Consider starting with a stronger action verb."
        )

    # --------------------------------------------------------
    # Specificity
    # --------------------------------------------------------

    if specificity["detail_level"] == "high":

        strengths.append(
            "Provides useful detail."
        )

    elif specificity["detail_level"] == "medium":

        improvements.append(
            "Add more specific details about the work performed."
        )

    else:

        improvements.append(
            "The bullet is too generic; explain what was built, "
            "changed, or delivered."
        )

    # --------------------------------------------------------
    # Technical detail
    # --------------------------------------------------------

    if specificity["technical_detail"]:

        strengths.append(
            "Includes technical or tool-specific detail."
        )

    else:

        improvements.append(
            "Mention relevant technologies, tools, systems, "
            "or methods when appropriate."
        )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    if metrics["has_metrics"]:

        strengths.append(
            "Includes measurable information."
        )

    else:

        improvements.append(
            "Add measurable results such as percentages, "
            "counts, time saved, scale, or performance changes."
        )

    # --------------------------------------------------------
    # Impact
    # --------------------------------------------------------

    if impact["has_impact"]:

        strengths.append(
            "Communicates impact or an outcome."
        )

    else:

        improvements.append(
            "Explain the result or impact of the work."
        )

    # --------------------------------------------------------
    # Weak phrasing
    # --------------------------------------------------------

    if weak_phrasing["has_weak_phrase"]:

        improvements.append(
            "Avoid generic phrases such as "
            + ", ".join(
                weak_phrasing["phrases"]
            )
            + "."
        )

    return (
        strengths,
        improvements,
    )


# ============================================================
# SINGLE BULLET ANALYSIS
# ============================================================

def analyze_bullet(
    bullet: str,
) -> dict:
    """
    Analyze one resume bullet completely.
    """

    cleaned = _clean_bullet_prefix(
        _normalize_spaces(
            _text(
                bullet
            )
        )
    )

    if not cleaned:

        return {
            "text": "",
            "score": 0,
            "max_score": 100,
            "status": "weak",
            "action_verb": {
                "first_word": "",
                "quality": "missing",
                "is_strong": False,
                "is_weak": False,
            },
            "specificity": {
                "word_count": 0,
                "has_number": False,
                "technical_keywords": [],
                "technical_detail": False,
                "detail_level": "low",
            },
            "metrics": {
                "has_metrics": False,
                "metrics": [],
                "count": 0,
            },
            "impact": {
                "has_impact": False,
                "impact_terms": [],
                "has_metrics": False,
            },
            "weak_phrasing": {
                "has_weak_phrase": False,
                "phrases": [],
            },
            "breakdown": {},
            "penalty": 0,
            "strengths": [],
            "improvements": [
                "Add meaningful bullet content."
            ],
        }

    action = analyze_action_verb(
        cleaned
    )

    specificity = analyze_specificity(
        cleaned
    )

    metrics = analyze_metrics(
        cleaned
    )

    impact = analyze_impact(
        cleaned
    )

    weak_phrasing = analyze_weak_phrasing(
        cleaned
    )

    score_result = calculate_bullet_score(
        action,
        specificity,
        metrics,
        impact,
        weak_phrasing,
    )

    strengths, improvements = (
        generate_bullet_recommendations(
            action,
            specificity,
            metrics,
            impact,
            weak_phrasing,
        )
    )

    return {
        "text": cleaned,
        "score": score_result["score"],
        "max_score": score_result["max_score"],
        "status": _score_status(
            score_result["score"]
        ),
        "action_verb": action,
        "specificity": specificity,
        "metrics": metrics,
        "impact": impact,
        "weak_phrasing": weak_phrasing,
        "breakdown": score_result[
            "breakdown"
        ],
        "penalty": score_result[
            "penalty"
        ],
        "strengths": strengths,
        "improvements": improvements,
    }


# ============================================================
# SECTION BULLET ANALYSIS
# ============================================================

def analyze_section_bullets(
    text: str,
) -> dict:
    """
    Analyze all bullets in a resume section.
    """

    bullets = extract_bullets(
        text
    )

    analyses = [
        analyze_bullet(
            bullet
        )
        for bullet in bullets
    ]

    scores = [
        item["score"]
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
        if item["status"] == "strong"
    )

    needs_attention_count = sum(
        1
        for item in analyses
        if item["status"]
        in {
            "needs_attention",
            "weak",
        }
    )

    return {
        "total": len(
            analyses
        ),
        "average_score": average_score,
        "strong_count": strong_count,
        "needs_attention_count":
            needs_attention_count,
        "bullets": analyses,
    }