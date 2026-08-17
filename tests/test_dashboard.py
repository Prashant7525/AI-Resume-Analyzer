import pytest

from app.dashboard import (
    build_dashboard_result,
    build_quick_summary,
    build_score_breakdown,
    calculate_overall_score,
    collect_recommendations,
)


def make_ats(score=80):
    return {
        "ats_score": {
            "score": score,
        },
        "suggestions": [],
    }


def make_quality(score=70):
    return {
        "score": score,
        "suggestions": [],
    }


def make_improvement(score=80):
    return {
        "score": score,
        "improvements": [],
    }


def make_job(score=60):
    return {
        "score": score,
        "suggestions": [],
        "keyword_suggestions": [],
    }


def test_calculate_overall_score_without_job():

    result = calculate_overall_score(
        make_ats(80),
        make_quality(70),
        None,
        make_improvement(90),
    )

    expected = round(
        80 * 0.50
        + 70 * 0.30
        + 90 * 0.20
    )

    assert result == expected


def test_calculate_overall_score_with_job():

    result = calculate_overall_score(
        make_ats(80),
        make_quality(70),
        make_job(60),
        make_improvement(90),
    )

    expected = round(
        80 * 0.35
        + 70 * 0.25
        + 60 * 0.20
        + 90 * 0.20
    )

    assert result == expected


def test_calculate_overall_score_handles_missing_results():

    result = calculate_overall_score(
        None,
        None,
        None,
        None,
    )

    assert result == 0


def test_score_is_clamped_to_100():

    result = calculate_overall_score(
        make_ats(150),
        make_quality(150),
        None,
        make_improvement(150),
    )

    assert result == 100


def test_build_score_breakdown_without_job():

    result = build_score_breakdown(
        make_ats(80),
        make_quality(70),
        None,
        make_improvement(90),
    )

    assert result["ats"] == 80
    assert result["quality"] == 70
    assert result["improvements"] == 90
    assert result["job_match"] is None


def test_build_score_breakdown_with_job():

    result = build_score_breakdown(
        make_ats(80),
        make_quality(70),
        make_job(60),
        make_improvement(90),
    )

    assert result["ats"] == 80
    assert result["quality"] == 70
    assert result["job_match"] == 60
    assert result["improvements"] == 90


def test_collect_recommendations():

    ats = make_ats()

    ats["suggestions"] = [
        "Add experience."
    ]

    quality = make_quality()

    quality["suggestions"] = [
        "Improve formatting."
    ]

    improvement = make_improvement()

    improvement["improvements"] = [
        "Add measurable achievements."
    ]

    result = collect_recommendations(
        ats,
        quality,
        None,
        improvement,
    )

    assert result == [
        "Add experience.",
        "Improve formatting.",
        "Add measurable achievements.",
    ]


def test_collect_recommendations_removes_duplicates():

    ats = make_ats()

    ats["suggestions"] = [
        "Add relevant work experience or internships."
    ]

    quality = make_quality()

    quality["suggestions"] = [
        "Add relevant work experience or internships."
    ]

    improvement = make_improvement()

    improvement["improvements"] = [
        "Add relevant work experience, internships, or practical experience."
    ]

    result = collect_recommendations(
        ats,
        quality,
        None,
        improvement,
    )

    assert len(result) == 1


def test_collect_recommendations_without_optional_results():

    result = collect_recommendations(
        make_ats(),
        make_quality(),
        None,
        make_improvement(),
    )

    assert isinstance(result, list)


def test_quick_summary():

    breakdown = {
        "ats": 79,
        "quality": 68,
        "job_match": None,
        "improvements": 83,
    }

    recommendations = [
        "Add relevant experience."
    ]

    result = build_quick_summary(
        breakdown,
        recommendations,
    )

    assert result["strongest_area"]["name"] == (
        "Improvement Readiness"
    )

    assert result["weakest_area"]["name"] == (
        "Resume Quality"
    )

    assert result["recommendation"] == (
        "Add relevant experience."
    )


def test_build_dashboard_result():

    resume = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
    }

    ats = make_ats(79)
    quality = make_quality(68)
    improvement = make_improvement(83)

    ats["suggestions"] = [
        "Add experience."
    ]

    quality["suggestions"] = [
        "Improve formatting."
    ]

    improvement["improvements"] = [
        "Add experience."
    ]

    result = build_dashboard_result(
        resume,
        ats,
        quality,
        None,
        improvement,
    )

    assert result["overall_score"] == 76

    assert result["breakdown"]["ats"] == 79
    assert result["breakdown"]["quality"] == 68
    assert result["breakdown"]["improvements"] == 83
    assert result["breakdown"]["job_match"] is None

    assert result["has_job_match"] is False

    assert result["recommendation_count"] == 2

    assert result["quick_summary"]["strongest_area"][
        "name"
    ] == "Improvement Readiness"

    assert result["quick_summary"]["weakest_area"][
        "name"
    ] == "Resume Quality"