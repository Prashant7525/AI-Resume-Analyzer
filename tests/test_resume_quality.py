from app.resume_quality import (
    analyze_achievements,
    analyze_bullet_usage,
    analyze_contact,
    analyze_resume_length,
    analyze_resume_quality,
    analyze_section_lengths,
    analyze_structure,
    calculate_quality_score,
    count_bullets,
    count_quantifiable_achievements,
    count_words,
    generate_quality_suggestions,
)


RESUME = {
    "name": "Alex Johnson",
    "email": "alex@example.com",
    "phone": "+1 555 123 4567",

    "summary": (
        "Software developer with experience building "
        "web applications and backend services."
    ),

    "skills": (
        "Python, Java, SQL, JavaScript, Git, Docker"
    ),

    "experience": (
        "• Developed web applications using Python.\n"
        "• Improved application response time by 30%.\n"
        "• Worked with SQL databases and REST APIs."
    ),

    "projects": (
        "• Built a task management application.\n"
        "• Created a weather dashboard."
    ),

    "education": (
        "Bachelor of Science in Computer Science"
    ),

    "certifications": (
        "Python Programming Certificate"
    ),

    "achievements": (
        "• Increased project performance by 25%.\n"
        "• Completed 5 software projects."
    ),

    "other": "",
}


EMPTY_RESUME = {
    "name": "",
    "email": "",
    "phone": "",
    "summary": "",
    "skills": "",
    "experience": "",
    "projects": "",
    "education": "",
    "certifications": "",
    "achievements": "",
    "other": "",
}


def test_count_words():
    assert count_words("Python developer with experience") == 4


def test_count_words_empty_text():
    assert count_words("") == 0


def test_count_bullets():
    text = """
    • First achievement
    • Second achievement
    """

    assert count_bullets(text) == 2


def test_count_quantifiable_achievements():
    text = """
    Increased performance by 30%.
    Managed 5 projects.
    """

    assert count_quantifiable_achievements(text) == 2


def test_analyze_resume_length():
    result = analyze_resume_length(RESUME)

    assert result["word_count"] > 0
    assert result["rating"] in {
        "short",
        "good",
        "long",
    }


def test_analyze_section_lengths():
    result = analyze_section_lengths(RESUME)

    assert result["summary"]["has_content"] is True
    assert result["skills"]["has_content"] is True
    assert result["projects"]["has_content"] is True
    assert result["education"]["has_content"] is True


def test_analyze_bullet_usage():
    result = analyze_bullet_usage(RESUME)

    assert result["total"] > 0
    assert result["has_bullets"] is True
    assert result["by_section"]["experience"] == 3


def test_analyze_achievements():
    result = analyze_achievements(RESUME)

    assert result["has_achievements"] is True
    assert result["has_quantifiable"] is True
    assert result["quantifiable"] == 2


def test_analyze_contact():
    result = analyze_contact(RESUME)

    assert result["name"] is True
    assert result["email"] is True
    assert result["phone"] is True
    assert result["passed"] == 3
    assert result["total"] == 3


def test_analyze_structure():
    result = analyze_structure(RESUME)

    assert result["present_count"] == 7
    assert result["total_sections"] == 7
    assert result["missing_sections"] == []


def test_calculate_quality_score():
    length = {
        "word_count": 200,
        "rating": "good",
    }

    sections = analyze_section_lengths(RESUME)
    bullets = analyze_bullet_usage(RESUME)
    achievements = analyze_achievements(RESUME)
    contact = analyze_contact(RESUME)
    structure = analyze_structure(RESUME)

    result = calculate_quality_score(
        length,
        sections,
        bullets,
        achievements,
        contact,
        structure,
    )

    assert result["score"] == 70
    assert result["max_score"] == 70


def test_generate_quality_suggestions_for_empty_resume():
    length = {
        "word_count": 0,
        "rating": "empty",
    }

    sections = analyze_section_lengths(EMPTY_RESUME)
    bullets = analyze_bullet_usage(EMPTY_RESUME)
    achievements = analyze_achievements(EMPTY_RESUME)
    contact = analyze_contact(EMPTY_RESUME)
    structure = analyze_structure(EMPTY_RESUME)

    suggestions = generate_quality_suggestions(
        length,
        sections,
        bullets,
        achievements,
        contact,
        structure,
    )

    assert len(suggestions) > 0
    assert "full name" in " ".join(suggestions).lower()
    assert "email" in " ".join(suggestions).lower()


def test_analyze_resume_quality():
    result = analyze_resume_quality(RESUME)

    assert result["score"] == 63
    assert result["max_score"] == 70

    assert result["length"]["rating"] in {
        "short",
        "good",
        "long",
    }

    assert result["bullets"]["has_bullets"] is True
    assert result["achievements"]["has_quantifiable"] is True
    assert result["contact"]["passed"] == 3
    assert result["structure"]["present_count"] == 7

def test_analyze_bullet_intelligence():
    result = analyze_resume_quality(
        RESUME
    )

    assert "bullet_intelligence" in result

    intelligence = result[
        "bullet_intelligence"
    ]

    assert "experience" in intelligence[
        "sections"
    ]

    assert "projects" in intelligence[
        "sections"
    ]

    assert "achievements" in intelligence[
        "sections"
    ]

    assert (
        intelligence["total_bullets"]
        > 0
    )


def test_bullet_intelligence_analyzes_experience_bullets():
    result = analyze_resume_quality(
        RESUME
    )

    experience = result[
        "bullet_intelligence"
    ][
        "sections"
    ][
        "experience"
    ]

    assert experience[
        "total"
    ] == 3

    assert (
        experience["average_score"]
        > 0
    )

    assert (
        len(
            experience["bullets"]
        )
        == 3
    )


def test_bullet_intelligence_does_not_change_quality_score():
    result = analyze_resume_quality(
        RESUME
    )

    # Existing V3.0/V3.1 score must remain unchanged.
    assert result["score"] == 63
    assert result["max_score"] == 70

def test_analyze_achievement_intelligence():
    result = analyze_resume_quality(
        RESUME
    )

    assert (
        "achievement_intelligence"
        in result
    )

    intelligence = result[
        "achievement_intelligence"
    ]

    assert intelligence[
        "total"
    ] == 2

    assert (
        intelligence["average_score"]
        > 0
    )


def test_achievement_intelligence_detects_metrics():
    result = analyze_resume_quality(
        RESUME
    )

    intelligence = result[
        "achievement_intelligence"
    ]

    assert (
        intelligence[
            "measurable_count"
        ] == 2
    )

    assert (
        len(
            intelligence[
                "achievements"
            ]
        ) == 2
    )


def test_achievement_intelligence_does_not_change_quality_score():
    result = analyze_resume_quality(
        RESUME
    )

    # Existing V3.0/V3.1 score must remain unchanged.
    assert result["score"] == 63
    assert result["max_score"] == 70

def test_resume_intelligence_summary_is_present():
    result = analyze_resume_quality(
        RESUME
    )

    assert (
        "intelligence_summary"
        in result
    )

    summary = result[
        "intelligence_summary"
    ]

    assert summary[
        "max_score"
    ] == 100

    assert (
        summary["score"]
        >= 0
    )

    assert (
        summary["score"]
        <= 100
    )


def test_resume_intelligence_summary_contains_components():
    result = analyze_resume_quality(
        RESUME
    )

    components = result[
        "intelligence_summary"
    ][
        "components"
    ]

    assert "sections" in components
    assert "bullets" in components
    assert "achievements" in components


def test_resume_intelligence_summary_preserves_component_scores():
    result = analyze_resume_quality(
        RESUME
    )

    summary = result[
        "intelligence_summary"
    ]

    assert (
        summary[
            "components"
        ][
            "sections"
        ][
            "score"
        ]
        == result[
            "section_intelligence"
        ][
            "score"
        ]
    )

    assert (
        summary[
            "components"
        ][
            "bullets"
        ][
            "score"
        ]
        == result[
            "bullet_intelligence"
        ][
            "average_score"
        ]
    )

    assert (
        summary[
            "components"
        ][
            "achievements"
        ][
            "score"
        ]
        == result[
            "achievement_intelligence"
        ][
            "average_score"
        ]
    )


def test_resume_intelligence_summary_has_summary_text():
    result = analyze_resume_quality(
        RESUME
    )

    summary = result[
        "intelligence_summary"
    ]

    assert summary[
        "summary"
    ]

    assert isinstance(
        summary["summary"],
        str,
    )


def test_resume_intelligence_summary_does_not_change_quality_score():
    result = analyze_resume_quality(
        RESUME
    )

    # Existing V3.0/V3.1 score remains unchanged.
    assert result["score"] == 63
    assert result["max_score"] == 70