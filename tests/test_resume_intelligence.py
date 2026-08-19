from app.resume_intelligence import (
    analyze_resume_intelligence,
    calculate_intelligence_score,
)


SECTION_INTELLIGENCE = {
    "score": 90,
    "section_count": 7,
    "total_sections": 7,
    "coverage_score": 100,
    "average_section_score": 88,
    "sections": {
        "summary": {
            "label": "Professional Summary",
            "score": 90,
            "max_score": 100,
            "status": "strong",
        },
        "skills": {
            "label": "Skills",
            "score": 92,
            "max_score": 100,
            "status": "strong",
        },
    },
}


BULLET_INTELLIGENCE = {
    "average_score": 88,
    "total_bullets": 8,
    "strong_bullets": 6,
    "needs_attention_bullets": 2,
    "sections": {
        "experience": {
            "total": 5,
            "average_score": 90,
        },
        "projects": {
            "total": 3,
            "average_score": 84,
        },
    },
}


ACHIEVEMENT_INTELLIGENCE = {
    "average_score": 92,
    "total": 3,
    "strong_count": 2,
    "needs_attention_count": 1,
    "measurable_count": 3,
    "ranking_count": 1,
    "achievements": [
        {
            "text": "Improved performance by 35%.",
            "score": 90,
            "status": "strong",
        },
        {
            "text": "Supported 500+ users.",
            "score": 88,
            "status": "strong",
        },
        {
            "text": "Completed several projects.",
            "score": 55,
            "status": "needs_attention",
        },
    ],
}


def test_calculate_intelligence_score():

    result = calculate_intelligence_score(
        90,
        80,
        90,
    )

    assert result == 86


def test_calculate_intelligence_score_is_bounded():

    assert (
        calculate_intelligence_score(
            100,
            100,
            100,
        )
        == 100
    )

    assert (
        calculate_intelligence_score(
            0,
            0,
            0,
        )
        == 0
    )


def test_analyze_resume_intelligence():

    result = analyze_resume_intelligence(
        section_intelligence=SECTION_INTELLIGENCE,
        bullet_intelligence=BULLET_INTELLIGENCE,
        achievement_intelligence=ACHIEVEMENT_INTELLIGENCE,
    )

    assert result["score"] > 0
    assert result["max_score"] == 100

    assert result["status"] in {
        "strong",
        "good",
        "needs_attention",
        "weak",
    }


def test_intelligence_contains_components():

    result = analyze_resume_intelligence(
        section_intelligence=SECTION_INTELLIGENCE,
        bullet_intelligence=BULLET_INTELLIGENCE,
        achievement_intelligence=ACHIEVEMENT_INTELLIGENCE,
    )

    assert "components" in result

    assert (
        "sections"
        in result["components"]
    )

    assert (
        "bullets"
        in result["components"]
    )

    assert (
        "achievements"
        in result["components"]
    )


def test_component_scores_are_preserved():

    result = analyze_resume_intelligence(
        section_intelligence=SECTION_INTELLIGENCE,
        bullet_intelligence=BULLET_INTELLIGENCE,
        achievement_intelligence=ACHIEVEMENT_INTELLIGENCE,
    )

    assert (
        result[
            "components"
        ][
            "sections"
        ][
            "score"
        ]
        == 90
    )

    assert (
        result[
            "components"
        ][
            "bullets"
        ][
            "score"
        ]
        == 88
    )

    assert (
        result[
            "components"
        ][
            "achievements"
        ][
            "score"
        ]
        == 92
    )


def test_strengths_are_detected():

    result = analyze_resume_intelligence(
        section_intelligence=SECTION_INTELLIGENCE,
        bullet_intelligence=BULLET_INTELLIGENCE,
        achievement_intelligence=ACHIEVEMENT_INTELLIGENCE,
    )

    assert result["strengths"]

    labels = {
        item["label"]
        for item in result["strengths"]
    }

    assert (
        "Resume Structure"
        in labels
        or "Section Coverage"
        in labels
    )

    assert (
        "Bullet Quality"
        in labels
        or "Bullet Usage"
        in labels
    )

    assert (
        "Achievement Quality"
        in labels
        or "Measurable Achievements"
        in labels
    )


def test_attention_areas_are_detected():

    result = analyze_resume_intelligence(
        section_intelligence=SECTION_INTELLIGENCE,
        bullet_intelligence=BULLET_INTELLIGENCE,
        achievement_intelligence=ACHIEVEMENT_INTELLIGENCE,
    )

    assert result["attention_areas"]

    text = " ".join(
        item["message"]
        for item in result[
            "attention_areas"
        ]
    ).lower()

    assert (
        "bullet"
        in text
        or "achievement"
        in text
    )


def test_summary_is_generated():

    result = analyze_resume_intelligence(
        section_intelligence=SECTION_INTELLIGENCE,
        bullet_intelligence=BULLET_INTELLIGENCE,
        achievement_intelligence=ACHIEVEMENT_INTELLIGENCE,
    )

    assert result["summary"]

    assert isinstance(
        result["summary"],
        str,
    )


def test_empty_intelligence_is_safe():

    result = analyze_resume_intelligence()

    assert result["score"] == 0
    assert result["max_score"] == 100
    assert result["status"] == "weak"

    assert result["components"]["sections"]["score"] == 0
    assert result["components"]["bullets"]["score"] == 0
    assert result["components"]["achievements"]["score"] == 0

    assert result["attention_areas"]


def test_partial_intelligence_is_safe():

    result = analyze_resume_intelligence(
        bullet_intelligence={
            "average_score": 75,
            "total_bullets": 4,
            "strong_bullets": 2,
            "needs_attention_bullets": 2,
        }
    )

    assert result["score"] > 0

    assert (
        result[
            "components"
        ][
            "bullets"
        ][
            "total_bullets"
        ]
        == 4
    )

    assert (
        result[
            "components"
        ][
            "sections"
        ][
            "score"
        ]
        == 0
    )


def test_strengths_are_sorted():

    result = analyze_resume_intelligence(
        section_intelligence=SECTION_INTELLIGENCE,
        bullet_intelligence=BULLET_INTELLIGENCE,
        achievement_intelligence=ACHIEVEMENT_INTELLIGENCE,
    )

    scores = [
        item["score"]
        for item in result["strengths"]
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_attention_areas_are_sorted():

    result = analyze_resume_intelligence(
        section_intelligence={
            "score": 60,
            "section_count": 4,
            "total_sections": 7,
            "coverage_score": 57,
            "average_section_score": 60,
            "sections": {},
        },
        bullet_intelligence={
            "average_score": 50,
            "total_bullets": 5,
            "strong_bullets": 1,
            "needs_attention_bullets": 4,
            "sections": {},
        },
        achievement_intelligence={
            "average_score": 40,
            "total": 2,
            "strong_count": 0,
            "needs_attention_count": 2,
            "measurable_count": 0,
            "ranking_count": 0,
            "achievements": [],
        },
    )

    scores = [
        item["score"]
        for item in result[
            "attention_areas"
        ]
    ]

    assert scores == sorted(
        scores
    )