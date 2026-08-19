"""
SQLite database layer for the AI Resume Analyzer.

V3.1
- Analysis history storage
- SQLite database
- Save analysis results
- Retrieve analysis history
- Retrieve individual analyses
- Delete analyses
- Configurable database location
- Safe parameterized SQL
- SQLite connection hardening
- Input validation
- Transaction safety
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

APP_DIR = Path(__file__).resolve().parent

INSTANCE_DIR = APP_DIR / "instance"

DEFAULT_DATABASE_PATH = (
    INSTANCE_DIR / "resume_analyzer.db"
)

# SQLite connection timeout in seconds.
DATABASE_TIMEOUT = 10.0

# Maximum number of history records that can be requested.
MAX_HISTORY_LIMIT = 500


def _get_database_path() -> Path:
    """
    Return the configured SQLite database path.

    DATABASE_PATH can be supplied through an environment
    variable for production deployments.

    When DATABASE_PATH is not configured, the application
    continues to use the local app/instance directory.
    """

    configured_path = os.getenv(
        "DATABASE_PATH"
    )

    if configured_path:

        configured_path = configured_path.strip()

        if configured_path:

            return Path(
                configured_path
            ).expanduser()

    return DEFAULT_DATABASE_PATH


DATABASE_PATH = _get_database_path()


# ============================================================
# VALIDATION HELPERS
# ============================================================

def _validate_analysis_id(
    analysis_id: int,
) -> int:
    """
    Validate and normalize an analysis ID.
    """

    if isinstance(
        analysis_id,
        bool,
    ):
        raise ValueError(
            "Analysis ID must be an integer."
        )

    try:

        value = int(
            analysis_id
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            "Analysis ID must be an integer."
        ) from exc

    if value <= 0:

        raise ValueError(
            "Analysis ID must be greater than zero."
        )

    return value


def _validate_history_limit(
    limit: int,
) -> int:
    """
    Validate and clamp a history query limit.
    """

    if isinstance(
        limit,
        bool,
    ):
        return 1

    try:

        value = int(
            limit
        )

    except (
        TypeError,
        ValueError,
    ):

        value = 50

    return max(
        1,
        min(
            value,
            MAX_HISTORY_LIMIT,
        ),
    )


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection() -> sqlite3.Connection:
    """
    Create and return a SQLite database connection.

    The parent directory is created automatically when
    necessary.

    The row factory allows database rows to be accessed
    using column names.

    SQLite safety settings are enabled for:

    - foreign key enforcement
    - busy timeout
    """

    database_directory = (
        DATABASE_PATH.parent
    )

    database_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=DATABASE_TIMEOUT,
    )

    connection.row_factory = sqlite3.Row

    # --------------------------------------------------------
    # SQLite safety / reliability settings
    # --------------------------------------------------------

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    connection.execute(
        "PRAGMA busy_timeout = 10000"
    )

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_database() -> None:
    """
    Create the database tables if they do not already exist.
    """

    try:

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

    except sqlite3.Error as exc:

        raise RuntimeError(
            "Unable to initialize the analysis database."
        ) from exc


# ============================================================
# VALUE HELPERS
# ============================================================

def _numeric_value(
    value: Any,
) -> float | None:
    """
    Return a numeric value or None.

    Boolean values are intentionally rejected because
    bool is a subclass of int in Python.
    """

    if isinstance(
        value,
        bool,
    ):
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
    """
    Safely retrieve a numeric nested value.
    """

    value = result

    for key in keys:

        if not isinstance(
            value,
            dict,
        ):
            return None

        value = value.get(
            key
        )

    return _numeric_value(
        value
    )


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

    # --------------------------------------------------------
    # Normalize incoming values.
    # --------------------------------------------------------

    resume = (
        resume
        if isinstance(
            resume,
            dict,
        )
        else {}
    )

    if not isinstance(
        job_description,
        str,
    ):
        job_description = ""

    # --------------------------------------------------------
    # Extract summary scores.
    # --------------------------------------------------------

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
        isinstance(
            job_result,
            dict,
        )
    )

    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    # --------------------------------------------------------
    # Store the complete analysis payload as JSON.
    # --------------------------------------------------------

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

    try:

        results_json = json.dumps(
            results,
            ensure_ascii=False,
            default=str,
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            "Unable to serialize analysis results."
        ) from exc

    # --------------------------------------------------------
    # Database transaction.
    # --------------------------------------------------------

    connection = None

    try:

        connection = get_connection()

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
                resume.get(
                    "name"
                ),
                resume.get(
                    "email"
                ),
                resume.get(
                    "phone"
                ),
                job_description,
                overall_score,
                ats_score,
                quality_score,
                improvement_score,
                job_match_score,
                keyword_coverage,
                int(
                    has_job_match
                ),
                results_json,
            ),
        )

        connection.commit()

        if cursor.lastrowid is None:
            raise RuntimeError(
                "Unable to determine saved analysis ID."
            )

        return int(
            cursor.lastrowid
        )

    except sqlite3.Error as exc:

        if connection is not None:

            try:
                connection.rollback()
            except sqlite3.Error:
                pass

        raise RuntimeError(
            "Unable to save the analysis."
        ) from exc

    finally:

        if connection is not None:

            connection.close()


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

    safe_limit = _validate_history_limit(
        limit
    )

    try:

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
                (
                    safe_limit,
                ),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    except sqlite3.Error as exc:

        raise RuntimeError(
            "Unable to retrieve analysis history."
        ) from exc


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

    safe_analysis_id = (
        _validate_analysis_id(
            analysis_id
        )
    )

    init_database()

    try:

        with get_connection() as connection:

            row = connection.execute(
                """
                SELECT *
                FROM analyses
                WHERE id = ?
                """,
                (
                    safe_analysis_id,
                ),
            ).fetchone()

        if row is None:
            return None

        result = dict(
            row
        )

        try:

            saved_results = json.loads(
                result.get(
                    "results_json",
                    "{}",
                )
            )

        except (
            TypeError,
            json.JSONDecodeError,
        ):

            saved_results = {}

        if not isinstance(
            saved_results,
            dict,
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

    except sqlite3.Error as exc:

        raise RuntimeError(
            "Unable to retrieve the analysis."
        ) from exc


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

    safe_analysis_id = (
        _validate_analysis_id(
            analysis_id
        )
    )

    init_database()

    connection = None

    try:

        connection = get_connection()

        cursor = connection.execute(
            """
            DELETE FROM analyses
            WHERE id = ?
            """,
            (
                safe_analysis_id,
            ),
        )

        connection.commit()

        return cursor.rowcount > 0

    except sqlite3.Error as exc:

        if connection is not None:

            try:
                connection.rollback()
            except sqlite3.Error:
                pass

        raise RuntimeError(
            "Unable to delete the analysis."
        ) from exc

    finally:

        if connection is not None:

            connection.close()


# ============================================================
# DATABASE PATH
# ============================================================

def get_database_path() -> Path:
    """
    Return the current SQLite database path.
    """

    return DATABASE_PATH