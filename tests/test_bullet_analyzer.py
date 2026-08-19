from app.bullet_analyzer import (
    analyze_action_verb,
    analyze_bullet,
    analyze_impact,
    analyze_metrics,
    analyze_section_bullets,
    analyze_specificity,
    analyze_weak_phrasing,
    calculate_bullet_score,
    extract_bullets,
    extract_metrics,
)


def test_extract_bullets():

    text = """
    • Developed a Python application.
    • Improved performance by 30%.
    """

    result = extract_bullets(
        text
    )

    assert len(result) == 2

    assert (
        result[0]
        == "Developed a Python application."
    )


def test_extract_bullets_ignores_non_bullets():

    text = """
    Developed a Python application.
    Improved performance by 30%.
    """

    result = extract_bullets(
        text
    )

    assert result == []


def test_strong_action_verb():

    result = analyze_action_verb(
        "Developed a Python application."
    )

    assert result["is_strong"] is True
    assert result["is_weak"] is False
    assert result["quality"] == "strong"


def test_weak_action_verb():

    result = analyze_action_verb(
        "Worked on Python applications."
    )

    assert result["is_weak"] is True
    assert result["is_strong"] is False
    assert result["quality"] == "weak"


def test_neutral_action_verb():

    result = analyze_action_verb(
        "Maintained internal systems."
    )

    assert result["quality"] == "neutral"


def test_specificity_detects_technical_detail():

    result = analyze_specificity(
        "Developed Flask APIs using Python and PostgreSQL."
    )

    assert result["technical_detail"] is True

    assert "flask" in (
        result["technical_keywords"]
    )

    assert (
        result["detail_level"]
        in {"medium", "high"}
    )


def test_specificity_low_for_generic_bullet():

    result = analyze_specificity(
        "Worked on applications."
    )

    assert result["technical_detail"] is False
    assert result["detail_level"] == "low"


def test_extract_metrics():

    result = extract_metrics(
        "Improved performance by 35% and supported 500+ users."
    )

    assert "35%" in result

    assert "500+" in result


def test_analyze_metrics():

    result = analyze_metrics(
        "Reduced processing time by 30%."
    )

    assert result["has_metrics"] is True
    assert result["count"] >= 1


def test_analyze_metrics_missing():

    result = analyze_metrics(
        "Built a Python application."
    )

    assert result["has_metrics"] is False
    assert result["count"] == 0


def test_analyze_impact_with_metric():

    result = analyze_impact(
        "Improved processing time by 30%."
    )

    assert result["has_impact"] is True


def test_analyze_impact_without_metric():

    result = analyze_impact(
        "Built a Python application."
    )

    assert result["has_impact"] is False


def test_weak_phrasing():

    result = analyze_weak_phrasing(
        "Worked on Python applications."
    )

    assert result["has_weak_phrase"] is True

    assert (
        "worked on"
        in result["phrases"]
    )


def test_no_weak_phrasing():

    result = analyze_weak_phrasing(
        "Developed Python applications."
    )

    assert result["has_weak_phrase"] is False


def test_bullet_score_strong_bullet():

    bullet = analyze_bullet(
        "Developed a Python automation platform "
        "that reduced processing time by 35%."
    )

    assert bullet["score"] >= 85
    assert bullet["status"] == "strong"
    assert bullet["action_verb"]["is_strong"] is True
    assert bullet["metrics"]["has_metrics"] is True
    assert bullet["impact"]["has_impact"] is True


def test_bullet_score_weak_bullet():

    bullet = analyze_bullet(
        "Worked on Python applications."
    )

    assert bullet["score"] < 70
    assert bullet["status"] in {
        "needs_attention",
        "weak",
    }


def test_weak_bullet_has_recommendations():

    bullet = analyze_bullet(
        "Worked on Python applications."
    )

    assert bullet["improvements"]

    text = " ".join(
        bullet["improvements"]
    ).lower()

    assert (
        "action verb"
        in text
        or "metric"
        in text
        or "impact"
        in text
    )


def test_strong_bullet_has_strengths():

    bullet = analyze_bullet(
        "Developed a Python automation platform "
        "that reduced processing time by 35%."
    )

    assert bullet["strengths"]

    text = " ".join(
        bullet["strengths"]
    ).lower()

    assert (
        "action verb"
        in text
    )


def test_empty_bullet():

    result = analyze_bullet(
        ""
    )

    assert result["score"] == 0
    assert result["status"] == "weak"
    assert result["text"] == ""


def test_calculate_bullet_score():

    action = {
        "is_strong": True,
        "is_weak": False,
    }

    specificity = {
        "detail_level": "high",
        "technical_detail": True,
    }

    metrics = {
        "has_metrics": True,
    }

    impact = {
        "has_impact": True,
    }

    weak_phrasing = {
        "has_weak_phrase": False,
    }

    result = calculate_bullet_score(
        action,
        specificity,
        metrics,
        impact,
        weak_phrasing,
    )

    assert result["score"] == 100
    assert result["max_score"] == 100
    assert result["penalty"] == 0


def test_weak_phrase_penalty():

    action = {
        "is_strong": False,
        "is_weak": True,
    }

    specificity = {
        "detail_level": "medium",
        "technical_detail": True,
    }

    metrics = {
        "has_metrics": True,
    }

    impact = {
        "has_impact": True,
    }

    weak_phrasing = {
        "has_weak_phrase": True,
    }

    result = calculate_bullet_score(
        action,
        specificity,
        metrics,
        impact,
        weak_phrasing,
    )

    assert result["penalty"] == 10
    assert result["score"] < 100


def test_section_bullet_analysis():

    section = """
    • Developed a Python application that improved
      processing time by 30%.
    • Worked on internal tools.
    • Optimized SQL queries and reduced latency by 20%.
    """

    result = analyze_section_bullets(
        section
    )

    assert result["total"] == 3
    assert len(
        result["bullets"]
    ) == 3

    assert (
        result["average_score"]
        > 0
    )

    assert (
        result["strong_count"]
        >= 1
    )