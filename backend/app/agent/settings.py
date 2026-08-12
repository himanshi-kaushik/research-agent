"""Shared Claude Agent SDK settings for the local LiteLLM gateway."""

from __future__ import annotations

import os

from dotenv import load_dotenv


def litellm_sdk_env() -> tuple[str, dict[str, str]]:
    """Return the configured model alias and environment for the SDK subprocess."""
    load_dotenv()

    base_url = os.getenv("LITELLM_BASE_URL", "http://127.0.0.1:4000")
    model = os.getenv("LITELLM_MODEL", "research-agent-primary")

    return model, {
        "ANTHROPIC_BASE_URL": base_url,
        "ANTHROPIC_API_KEY": "local-litellm",
        "ANTHROPIC_MODEL": model,
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": model,
        "ANTHROPIC_DEFAULT_SONNET_MODEL": model,
        "ANTHROPIC_DEFAULT_OPUS_MODEL": model,
    }
