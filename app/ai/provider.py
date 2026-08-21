"""
AI provider abstraction for the AI Resume Analyzer.

V3.3
- Centralized AI configuration
- Environment-based API credentials
- Provider abstraction
- Safe timeout handling
- No provider-specific logic in Flask routes
"""

from __future__ import annotations

import os
from typing import Any


# ============================================================
# AI CONFIGURATION
# ============================================================

DEFAULT_MODEL = "gpt-5.6"

DEFAULT_TIMEOUT = 30.0


class AIProviderError(RuntimeError):
    """Raised when the AI provider cannot complete a request."""


def _get_api_key() -> str:
    """
    Return the configured AI API key.

    The key must come from the environment and must never
    be hard-coded into the application.
    """

    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise AIProviderError(
            "AI provider is not configured."
        )

    return api_key


def _get_model() -> str:
    """
    Return the configured AI model.
    """

    return os.getenv(
        "OPENAI_MODEL",
        DEFAULT_MODEL,
    ).strip() or DEFAULT_MODEL


def _get_timeout() -> float:
    """
    Return the configured AI request timeout.
    """

    raw_timeout = os.getenv(
        "OPENAI_TIMEOUT",
        str(DEFAULT_TIMEOUT),
    )

    try:
        timeout = float(raw_timeout)
    except (TypeError, ValueError):
        timeout = DEFAULT_TIMEOUT

    return max(
        1.0,
        min(timeout, 120.0),
    )


def is_ai_configured() -> bool:
    """
    Return True when an AI API key is configured.
    """

    return bool(
        os.getenv(
            "OPENAI_API_KEY",
            "",
        ).strip()
    )


def generate_text(
    *,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """
    Generate text using the configured AI provider.

    The provider SDK is imported lazily so that the existing
    application and test suite can run without requiring
    an API request.

    Raises:
        AIProviderError:
            When configuration, provider initialization,
            or generation fails.
    """

    if not isinstance(
        system_prompt,
        str,
    ) or not system_prompt.strip():

        raise ValueError(
            "System prompt must be a non-empty string."
        )

    if not isinstance(
        user_prompt,
        str,
    ) or not user_prompt.strip():

        raise ValueError(
            "User prompt must be a non-empty string."
        )

    api_key = _get_api_key()
    model = _get_model()
    timeout = _get_timeout()

    try:

        from openai import OpenAI

    except ImportError as exc:

        raise AIProviderError(
            "OpenAI provider is not installed."
        ) from exc

    try:

        client = OpenAI(
            api_key=api_key,
            timeout=timeout,
        )

        response = client.responses.create(
            model=model,
            instructions=system_prompt,
            input=user_prompt,
        )

        text = getattr(
            response,
            "output_text",
            None,
        )

        if not isinstance(
            text,
            str,
        ) or not text.strip():

            raise AIProviderError(
                "AI provider returned an empty response."
            )

        return text.strip()

    except AIProviderError:

        raise

    except Exception as exc:

        raise AIProviderError(
            "Unable to generate AI content."
        ) from exc


def get_provider_info() -> dict[str, Any]:
    """
    Return non-sensitive provider configuration.

    API keys are intentionally never returned.
    """

    return {
        "provider": "openai",
        "model": _get_model(),
        "timeout": _get_timeout(),
        "configured": is_ai_configured(),
    }