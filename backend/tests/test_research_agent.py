"""Tests for Research Agent orchestration rules."""

import pytest

from backend.app.agent.research_agent import (
    READ_TOOL,
    RESEARCH_SYSTEM_PROMPT,
    SEARCH_TOOL,
    build_research_options,
    research_topic,
)


@pytest.mark.asyncio
async def test_empty_topic_is_rejected():
    with pytest.raises(
        ValueError,
        match="topic cannot be empty",
    ):
        await research_topic("   ")


def test_research_tools_are_configured():
    options = build_research_options()

    assert SEARCH_TOOL in options.allowed_tools
    assert READ_TOOL in options.allowed_tools
    assert "web-tools" in options.mcp_servers


def test_prompt_requires_reliable_sources():
    assert "government websites" in RESEARCH_SYSTEM_PROMPT
    assert "universities" in RESEARCH_SYSTEM_PROMPT
    assert "international organizations" in RESEARCH_SYSTEM_PROMPT


def test_prompt_requires_report_sections():
    required_sections = [
        "# Research Report:",
        "## Executive Summary",
        "## Key Findings",
        "## Detailed Analysis",
        "## Limitations",
        "## Sources",
    ]

    for section in required_sections:
        assert section in RESEARCH_SYSTEM_PROMPT


def test_prompt_contains_followup_rules():
    assert "For follow-up questions:" in RESEARCH_SYSTEM_PROMPT
    assert "Do not search again" in RESEARCH_SYSTEM_PROMPT
    