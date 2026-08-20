from app.achievement_analyzer import (
    analyze_achievement,
    analyze_achievement_section,
    calculate_achievement_score,
    classify_metric,
    classify_metrics,
    detect_impact_signals,
    detect_rankings,
    detect_time_savings,
    extract_achievements,
    extract_metrics,
)


def test_extract_bullet_achievements():

    text = """
    • Increased project performance by 30%.
    • Supported 500+ users.
    """

    result = extract_achievements(
        text
    )

    assert len(result) == 2

    assert (
        result[0]
        == "Increased project performance by 30%."
    )


def test_extract_non_bullet_achievements():

    text = """
    Increased project performance by 30%.
    Supported 500+ users.
    """

    result = extract_achievements(
        text
    )

    assert len(result) == 2


def test_extract_metrics():

    result = extract_metrics(
        "Improved performance by 35% and supported 500+ users."
    )

    assert "35%" in result
    assert "500+" in result


def test_extract_currency_metric():

    result = extract_metrics(
        "Generated ₹10L in revenue."
    )

    assert "₹10L" in result


def test_extract_multiplier_metric():

    result = extract_metrics(
        "Improved throughput by 2x."
    )

    assert "2x" in result


def test_extract_time_metric():

    result = extract_metrics(
        "Saved 15 hours per week."
    )

    assert any(
        "15 hours"
        in value
        for value in result
    )


def test_classify_percentage():

    assert (
        classify_metric("35%")
        == "percentage"
    )


def test_classify_count():

    assert (
        classify_metric("500+")
        == "count"
    )


def test_classify_scale():

    assert (
        classify_metric("50K")
        == "scale"
    )


def test_classify_multiplier():

    assert (
        classify_metric("2x")
        == "multiplier"
    )


def test_classify_currency():

    assert (
        classify_metric("₹10L")
        == "currency"
    )


def test_classify_metrics():

    result = classify_metrics(
        [
            "35%",
            "500+",
            "2x",
        ]
    )

    assert len(
        result["items"]
    ) == 3

    assert (
        result["type_counts"]["percentage"]
        == 1
    )

    assert (
        result["type_counts"]["count"]
        == 1
    )

    assert (
        result["type_counts"]["multiplier"]
        == 1
    )


def test_detect_rankings():

    result = detect_rankings(
        "Ranked in the top 10% of participants."
    )

    assert result

    assert any(
        "top 10%"
        in value.lower()
        for value in result
    )


def test_detect_numeric_ranking():

    result = detect_rankings(
        "Ranked 1st in the university."
    )

    assert result


def test_detect_impact_signals():

    result = detect_impact_signals(
        "Increased project performance by 30%."
    )

    assert "increased" in result


def test_detect_time_savings():

    result = detect_time_savings(
        "Saved 10 hours per week."
    )

    assert result


def test_detect_reduced_processing_time():

    result = detect_time_savings(
        "Reduced processing time by 30%."
    )

    assert result


def test_strong_achievement():

    result = analyze_achievement(
        "Increased application performance by 35% "
        "while supporting 500+ users."
    )

    assert result["score"] >= 85
    assert result["status"] == "strong"

    assert (
        result["metrics"]["count"]
        >= 2
    )

    assert result[
        "impact_signals"
    ]


def test_currency_achievement():

    result = analyze_achievement(
        "Generated ₹10L in revenue."
    )

    assert (
        result["metrics"]["count"]
        >= 1
    )

    assert (
        result["classification"]["type_counts"]["currency"]
        >= 1
    )


def test_ranking_achievement():

    result = analyze_achievement(
        "Ranked in the top 10% of participants."
    )

    assert result["rankings"]

    assert (
        result["score"]
        >= 70
    )


def test_weak_achievement():

    result = analyze_achievement(
        "Completed projects."
    )

    assert result["score"] < 70

    assert result["status"] in {
        "needs_attention",
        "weak",
    }

    assert result["improvements"]


def test_achievement_without_metrics():

    result = analyze_achievement(
        "Helped improve the development process."
    )

    assert (
        result["metrics"]["count"]
        == 0
    )

    text = " ".join(
        result["improvements"]
    ).lower()

    assert (
        "measurable"
        in text
        or "metric"
        in text
    )


def test_calculate_achievement_score():

    metrics = {
        "count": 2,
        "values": [
            "35%",
            "500+",
        ],
    }

    classifications = {
        "items": [
            {
                "value": "35%",
                "type": "percentage",
            },
            {
                "value": "500+",
                "type": "count",
            },
        ],
        "type_counts": {
            "percentage": 1,
            "count": 1,
        },
    }

    result = calculate_achievement_score(
        "Increased performance by 35% and supported 500+ users.",
        metrics,
        classifications,
        ["top 10%"],
        ["increased"],
        [],
    )

    assert result["score"] == 100
    assert result["max_score"] == 100


def test_analyze_achievement_section():

    text = """
    • Increased performance by 30%.
    • Supported 500+ users.
    • Ranked in the top 10%.
    """

    result = analyze_achievement_section(
        text
    )

    assert result["total"] == 3

    assert len(
        result["achievements"]
    ) == 3

    assert (
        result["average_score"]
        > 0
    )

    assert (
        result["measurable_count"]
        >= 2
    )


def test_empty_achievement_section():

    result = analyze_achievement_section(
        ""
    )

    assert result["total"] == 0
    assert result["average_score"] == 0
    assert result["strong_count"] == 0
    assert result[
        "needs_attention_count"
    ] == 0

def test_extract_comma_separated_metric():
    result = extract_metrics(
        "Solved 700+ problems on GeeksforGeeks and "
        "1,200+ problems on LeetCode."
    )

    assert "700+" in result
    assert "1,200+" in result

def test_extract_multiple_metric_formats():
    result = extract_metrics(
        "Improved performance by 35%, "
        "supported 1,200+ users, "
        "and saved 15 hours per week."
    )

    assert "35%" in result
    assert "1,200+" in result
    assert "15 hours" in result