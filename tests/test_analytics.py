from app.analytics import (
    build_analytics,
)


def ats(score):

    return {
        "ats_score": {
            "score": score,
        }
    }


def quality(score):

    return {
        "score": score,
    }


def improvement(score):

    return {
        "score": score,
    }


def job(score):

    return {
        "score": score,
    }


def test_excellent_score():

    result = build_analytics(
        ats(90),
        quality(88),
        improvement(92),
    )

    statuses = [
        metric["status"]
        for metric in result["metrics"]
    ]

    assert statuses == [
        "excellent",
        "excellent",
        "excellent",
    ]


def test_good_score():

    result = build_analytics(
        ats(79),
        quality(72),
        improvement(83),
    )

    statuses = [
        metric["status"]
        for metric in result["metrics"]
    ]

    assert statuses == [
        "good",
        "good",
        "good",
    ]


def test_attention_score():

    result = build_analytics(
        ats(79),
        quality(68),
        improvement(83),
    )

    statuses = [
        metric["status"]
        for metric in result["metrics"]
    ]

    assert statuses == [
        "good",
        "attention",
        "good",
    ]


def test_attention_area_is_generated():

    result = build_analytics(
        ats(79),
        quality(68),
        improvement(83),
    )

    assert (
        "Resume Quality needs attention at 68/100."
        in result["attention_areas"]
    )


def test_average_score():

    result = build_analytics(
        ats(79),
        quality(68),
        improvement(83),
    )

    assert result["summary"]["average_score"] == 77


def test_job_match_is_included():

    result = build_analytics(
        ats(79),
        quality(68),
        improvement(83),
        job(74),
    )

    assert len(result["metrics"]) == 4

    assert result["metrics"][-1]["name"] == (
        "Job Match"
    )

    assert result["metrics"][-1]["score"] == 74