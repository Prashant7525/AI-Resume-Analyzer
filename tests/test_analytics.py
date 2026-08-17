from app.analytics import (
    build_analytics_result,
    build_attention_areas,
    build_score_metrics,
    build_score_summary,
    build_strengths,
)


ATS_RESULT = {
    "ats_score": {
        "score": 90,
    },
}

QUALITY_RESULT = {
    "score": 80,
}

IMPROVEMENT_RESULT = {
    "score": 70,
}

JOB_RESULT = {
    "score": 60,
}


def test_build_score_metrics_without_job():
    metrics = build_score_metrics(
        ATS_RESULT,
        QUALITY_RESULT,
        IMPROVEMENT_RESULT,
    )

    assert len(metrics) == 4

    assert metrics[0]["name"] == "ATS Readiness"
    assert metrics[0]["score"] == 90
    assert metrics[0]["label"] == "Excellent"

    assert metrics[1]["name"] == "Resume Quality"
    assert metrics[1]["score"] == 80
    assert metrics[1]["status"] == "good"

    assert metrics[2]["name"] == "Improvement Readiness"
    assert metrics[2]["score"] == 70

    assert metrics[3]["name"] == "Job Match"
    assert metrics[3]["score"] is None


def test_build_score_metrics_with_job():
    metrics = build_score_metrics(
        ATS_RESULT,
        QUALITY_RESULT,
        IMPROVEMENT_RESULT,
        JOB_RESULT,
    )

    assert metrics[3]["name"] == "Job Match"
    assert metrics[3]["score"] == 60
    assert metrics[3]["label"] == "Needs Improvement"


def test_build_score_metrics_handles_missing_results():
    metrics = build_score_metrics(
        None,
        None,
        None,
        None,
    )

    assert len(metrics) == 4

    for metric in metrics:
        assert metric["score"] is None
        assert metric["label"] == "Not available"
        assert metric["status"] == "unavailable"


def test_build_score_summary():
    result = build_score_summary(
        ATS_RESULT,
        QUALITY_RESULT,
        IMPROVEMENT_RESULT,
    )

    assert result["average_score"] == 80
    assert result["available_metrics"] == 3
    assert result["total_metrics"] == 4


def test_build_score_summary_with_job():
    result = build_score_summary(
        ATS_RESULT,
        QUALITY_RESULT,
        IMPROVEMENT_RESULT,
        JOB_RESULT,
    )

    assert result["average_score"] == 75
    assert result["available_metrics"] == 4


def test_build_strengths():
    strengths = build_strengths(
        ATS_RESULT,
        QUALITY_RESULT,
        IMPROVEMENT_RESULT,
    )

    assert len(strengths) == 3
    assert "ATS Readiness is excellent" in strengths[0]
    assert "Resume Quality is performing well" in strengths[1]


def test_build_attention_areas():
    areas = build_attention_areas(
        ATS_RESULT,
        QUALITY_RESULT,
        IMPROVEMENT_RESULT,
        JOB_RESULT,
    )

    assert len(areas) == 1
    assert "Job Match needs attention" in areas[0]


def test_build_attention_areas_without_problems():
    result = build_attention_areas(
        {
            "ats_score": {
                "score": 90,
            },
        },
        {
            "score": 85,
        },
        {
            "score": 95,
        },
    )

    assert result == []


def test_build_analytics_result():
    result = build_analytics_result(
        ATS_RESULT,
        QUALITY_RESULT,
        IMPROVEMENT_RESULT,
        JOB_RESULT,
    )

    assert "summary" in result
    assert "metrics" in result
    assert "strengths" in result
    assert "attention_areas" in result

    assert result["summary"]["average_score"] == 75
    assert len(result["metrics"]) == 4
    assert len(result["strengths"]) == 3
    assert len(result["attention_areas"]) == 1