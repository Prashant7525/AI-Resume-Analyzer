from app.dashboard import (
    build_dashboard_result,
    build_score_breakdown,
    calculate_overall_score,
    collect_recommendations,
)


ATS_RESULT = {
    "ats_score": {
        "score": 80,
    },
    "suggestions": [
        "Add a professional summary.",
    ],
}


QUALITY_RESULT = {
    "score": 70,
    "suggestions": [
        "Add more measurable achievements.",
    ],
}


JOB_RESULT = {
    "score": 60,
    "suggestions": [
        "Review missing job skills.",
    ],
    "keyword_suggestions": [
        "Add relevant job keywords.",
    ],
}


IMPROVEMENT_RESULT = {
    "score": 75,
    "improvements": [
        "Strengthen the professional summary.",
    ],
}


RESUME = {
    "name": "Alex Johnson",
}


def test_calculate_overall_score_without_job():
    score = calculate_overall_score(
        ATS_RESULT,
        QUALITY_RESULT,
        improvement_result=IMPROVEMENT_RESULT,
    )

    assert score == 76


def test_calculate_overall_score_with_job():
    score = calculate_overall_score(
        ATS_RESULT,
        QUALITY_RESULT,
        JOB_RESULT,
        IMPROVEMENT_RESULT,
    )

    assert score == 72


def test_calculate_overall_score_handles_missing_results():
    score = calculate_overall_score(
        None,
        None,
    )

    assert score == 0


def test_score_is_clamped_to_100():
    ats_result = {
        "ats_score": {
            "score": 150,
        },
    }

    quality_result = {
        "score": 150,
    }

    score = calculate_overall_score(
        ats_result,
        quality_result,
    )

    assert score == 100


def test_build_score_breakdown_without_job():
    breakdown = build_score_breakdown(
        ATS_RESULT,
        QUALITY_RESULT,
        improvement_result=IMPROVEMENT_RESULT,
    )

    assert breakdown["ats"] == 80
    assert breakdown["quality"] == 70
    assert breakdown["job_match"] is None
    assert breakdown["improvements"] == 75


def test_build_score_breakdown_with_job():
    breakdown = build_score_breakdown(
        ATS_RESULT,
        QUALITY_RESULT,
        JOB_RESULT,
        IMPROVEMENT_RESULT,
    )

    assert breakdown["ats"] == 80
    assert breakdown["quality"] == 70
    assert breakdown["job_match"] == 60
    assert breakdown["improvements"] == 75


def test_collect_recommendations():
    recommendations = collect_recommendations(
        ATS_RESULT,
        QUALITY_RESULT,
        JOB_RESULT,
        IMPROVEMENT_RESULT,
    )

    assert len(recommendations) == 5

    assert (
        "Strengthen the professional summary."
        in recommendations
    )

    assert (
        "Add more measurable achievements."
        in recommendations
    )


def test_collect_recommendations_removes_duplicates():
    ats = {
        "suggestions": [
            "Add a professional summary.",
        ],
    }

    quality = {
        "suggestions": [
            "Add a professional summary.",
        ],
    }

    recommendations = collect_recommendations(
        ats,
        quality,
    )

    assert recommendations == [
        "Add a professional summary.",
    ]


def test_collect_recommendations_without_optional_results():
    recommendations = collect_recommendations(
        ATS_RESULT,
        QUALITY_RESULT,
    )

    assert len(recommendations) == 2


def test_build_dashboard_result():
    result = build_dashboard_result(
        RESUME,
        ATS_RESULT,
        QUALITY_RESULT,
        JOB_RESULT,
        IMPROVEMENT_RESULT,
    )

    assert result["overall_score"] == 72

    assert result["breakdown"]["ats"] == 80
    assert result["breakdown"]["quality"] == 70
    assert result["breakdown"]["job_match"] == 60
    assert result["breakdown"]["improvements"] == 75

    assert result["has_job_match"] is True
    assert result["resume_name"] == "Alex Johnson"

    assert result["recommendation_count"] == 5
    assert len(result["recommendations"]) == 5