"""
SQLite database layer for the AI Resume Analyzer.

V2.4
- Analysis history storage
- SQLite database
- Save analysis results
- Retrieve analysis history
- Retrieve individual analyses
- Delete analyses
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

APP_DIR = Path(__file__).resolve().parent

INSTANCE_DIR = APP_DIR / "instance"

DATABASE_PATH = INSTANCE_DIR / "resume_analyzer.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================


def get_connection() -> sqlite3.Connection:
    """
    Create and return a SQLite database connection.

    The row factory allows database rows to be accessed using
    column names.
    """

    INSTANCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================


def init_database() -> None:
    """
    Create the database tables if they do not already exist.
    """

    with get_connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                resume_name TEXT,
                resume_email TEXT,
                resume_phone TEXT,
                job_description TEXT,
                overall_score REAL,
                ats_score REAL,
                quality_score REAL,
                improvement_score REAL,
                job_match_score REAL,
                keyword_coverage REAL,
                has_job_match INTEGER NOT NULL DEFAULT 0,
                results_json TEXT NOT NULL
            )
            """
        )

        connection.commit()


# ============================================================
# VALUE HELPERS
# ============================================================


def _numeric_value(
    value: Any,
) -> float | None:
    """Return a numeric value or None."""

    if isinstance(value, bool):
        return None

    if isinstance(
        value,
        (int, float),
    ):
        return float(value)

    return None


def _nested_score(
    result: dict | None,
    *keys: str,
) -> float | None:
    """Safely retrieve a numeric nested value."""

    value = result

    for key in keys:

        if not isinstance(
            value,
            dict,
        ):
            return None

        value = value.get(key)

    return _numeric_value(value)


# ============================================================
# SAVE ANALYSIS
# ============================================================


def save_analysis(
    *,
    resume: dict | None,
    ats_result: dict | None = None,
    quality_result: dict | None = None,
    improvement_result: dict | None = None,
    job_result: dict | None = None,
    dashboard_result: dict | None = None,
    analytics_result: dict | None = None,
    job_description: str = "",
) -> int:
    """
    Save a complete resume analysis.

    Returns:
        The database ID of the newly saved analysis.
    """

    init_database()

    resume = resume or {}

    ats_score = _nested_score(
        ats_result,
        "ats_score",
        "score",
    )

    quality_score = _nested_score(
        quality_result,
        "score",
    )

    improvement_score = _nested_score(
        improvement_result,
        "score",
    )

    job_match_score = _nested_score(
        job_result,
        "score",
    )

    keyword_coverage = _nested_score(
        job_result,
        "keyword_coverage",
    )

    overall_score = _nested_score(
        dashboard_result,
        "overall_score",
    )

    has_job_match = bool(
        job_result
    )

    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    results = {
        "resume": resume,
        "ats_result": ats_result,
        "quality_result": quality_result,
        "improvement_result": improvement_result,
        "job_result": job_result,
        "dashboard_result": dashboard_result,
        "analytics_result": analytics_result,
        "job_description": job_description,
    }

    results_json = json.dumps(
        results,
        ensure_ascii=False,
        default=str,
    )

    with get_connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO analyses (
                created_at,
                resume_name,
                resume_email,
                resume_phone,
                job_description,
                overall_score,
                ats_score,
                quality_score,
                improvement_score,
                job_match_score,
                keyword_coverage,
                has_job_match,
                results_json
            )
            VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                created_at,
                resume.get("name"),
                resume.get("email"),
                resume.get("phone"),
                job_description,
                overall_score,
                ats_score,
                quality_score,
                improvement_score,
                job_match_score,
                keyword_coverage,
                int(has_job_match),
                results_json,
            ),
        )

        connection.commit()

        return int(
            cursor.lastrowid
        )


# ============================================================
# HISTORY
# ============================================================


def get_analysis_history(
    limit: int = 50,
) -> list[dict]:
    """
    Return recent analyses.

    Results are ordered from newest to oldest.
    """

    init_database()

    limit = max(
        1,
        min(
            int(limit),
            500,
        ),
    )

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                id,
                created_at,
                resume_name,
                resume_email,
                resume_phone,
                overall_score,
                ats_score,
                quality_score,
                improvement_score,
                job_match_score,
                keyword_coverage,
                has_job_match
            FROM analyses
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# SINGLE ANALYSIS
# ============================================================


def get_analysis(
    analysis_id: int,
) -> dict | None:
    """
    Return a complete saved analysis by ID.

    Returns:
        Analysis dictionary or None when not found.
    """

    init_database()

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM analyses
            WHERE id = ?
            """,
            (analysis_id,),
        ).fetchone()

    if row is None:
        return None

    result = dict(row)

    try:
        saved_results = json.loads(
            result["results_json"]
        )
    except (
        TypeError,
        json.JSONDecodeError,
    ):
        saved_results = {}

    result.update(
        saved_results
    )

    result.pop(
        "results_json",
        None,
    )

    return result


# ============================================================
# DELETE ANALYSIS
# ============================================================


def delete_analysis(
    analysis_id: int,
) -> bool:
    """
    Delete an analysis by ID.

    Returns:
        True when an analysis was deleted.
        False when no matching analysis existed.
    """

    init_database()

    with get_connection() as connection:

        cursor = connection.execute(
            """
            DELETE FROM analyses
            WHERE id = ?
            """,
            (analysis_id,),
        )

        connection.commit()

        return cursor.rowcount > 0


# ============================================================
# DATABASE PATH
# ============================================================


def get_database_path() -> Path:
    """Return the current SQLite database path."""

    return DATABASE_PATH