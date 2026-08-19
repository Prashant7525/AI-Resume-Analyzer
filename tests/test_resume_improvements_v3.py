from app.resume_improvements import (
    generate_action_plan,
    generate_priority_improvements,
    generate_strengths,
)


GOOD_RESUME = {
    "name": "Alex Johnson",
    "email": "alex@example.com",
    "phone": "+1 555 123 4567",
    "summary": (
        "Software developer with experience building web applications "
        "and backend services using Python, SQL, JavaScript, and modern "
        "development tools while delivering reliable and maintainable solutions."
    ),
    "skills": "Python, Java, SQL, JavaScript, Git, Docker",
    "experience": (
        "• Developed web applications using Python.\n"
        "• Improved application response time by 30%.\n"
        "• Worked with SQL databases."
    ),
    "projects": (
        "• Built a task management application.\n"
        "• Created a weather dashboard."
    ),
    "achievements": (
        "• Increased project performance by 25%.\n"
        "• Completed 5 software projects."
    ),
}


INCOMPLETE_RESUME = {
    "name": "",
    "email": "",
    "phone": "",
    "summary": "",
    "skills": "",
    "experience": "",
    "projects": "",
    "achievements": "",
}


def test_priority_improvements_have_structure():
    result = generate_priority_improvements(
        INCOMPLETE_RESUME
    )

    assert result

    first = result[0]

    assert "section" in first
    assert "section_label" in first
    assert "status" in first
    assert "priority" in first
    assert "recommendation" in first


def test_missing_contact_information_is_critical():
    result = generate_priority_improvements(
        INCOMPLETE_RESUME
    )

    contact = next(
        item
        for item in result
        if item["section"] == "contact"
    )

    assert contact["priority"] == "critical"
    assert contact["status"] == "incomplete"


def test_priority_order_places_critical_items_first():
    result = generate_priority_improvements(
        INCOMPLETE_RESUME
    )

    priorities = [
        item["priority"]
        for item in result
    ]

    priority_rank = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    ranks = [
        priority_rank[item]
        for item in priorities
    ]

    assert ranks == sorted(ranks)


def test_good_resume_has_multiple_strengths():
    result = generate_strengths(
        GOOD_RESUME
    )

    sections = {
        item["section"]
        for item in result
    }

    assert "summary" in sections
    assert "experience" in sections
    assert "skills" in sections


def test_good_resume_has_no_priority_improvements():
    result = generate_priority_improvements(
        GOOD_RESUME
    )

    assert result == []


def test_incomplete_resume_has_action_plan():
    result = generate_action_plan(
        INCOMPLETE_RESUME
    )

    assert result

    assert result[0]["number"] == 1

    for item in result:
        assert "section" in item
        assert "priority" in item
        assert "action" in item
        assert "reason" in item


def test_action_plan_numbers_are_sequential():
    result = generate_action_plan(
        INCOMPLETE_RESUME
    )

    numbers = [
        item["number"]
        for item in result
    ]

    assert numbers == list(
        range(
            1,
            len(numbers) + 1,
        )
    )