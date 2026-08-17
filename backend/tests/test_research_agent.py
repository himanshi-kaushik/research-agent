"""Tests for Research Agent orchestration rules."""

import pytest

from backend.app.agent.research_agent import (
    READ_TOOL,
    RESEARCH_SYSTEM_PROMPT,
    SEARCH_TOOL,
    SYNTHESIS_SYSTEM_PROMPT,
    FOLLOWUP_SYSTEM_PROMPT,
    build_research_options,
    build_followup_options,
    research_topic,
    validate_report,
    _evidence_fallback_report,
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


def test_followup_agent_can_choose_web_tools():
    options = build_followup_options()
    assert SEARCH_TOOL in options.allowed_tools
    assert READ_TOOL in options.allowed_tools
    assert "web-tools" in options.mcp_servers
    assert "If it is sufficient" in FOLLOWUP_SYSTEM_PROMPT
    assert "use search_web and read_webpage" in FOLLOWUP_SYSTEM_PROMPT


def test_incomplete_report_is_rejected():
    with pytest.raises(RuntimeError, match="incomplete research report"):
        validate_report("I'm sorry, but I can't continue with this request.")


def test_complete_report_is_accepted():
    report = """# Research Report: Test

## Executive Summary
Summary.

## Key Findings
- Finding.

## Detailed Analysis
Analysis.

## Limitations
Limitations.

## Sources
1. https://example.com
"""

    assert validate_report(report) == report.strip()


def test_synthesis_prompt_does_not_require_tools():
    assert "cannot and must not call tools" in SYNTHESIS_SYSTEM_PROMPT
    assert "Call search_web exactly twice" not in SYNTHESIS_SYSTEM_PROMPT


def test_evidence_fallback_is_a_valid_report():
    sources = [
        {"title": "Source One", "url": "https://one.example", "text": "Evidence one " * 30},
        {"title": "Source Two", "url": "https://two.example", "text": "Evidence two " * 30},
    ]

    report = _evidence_fallback_report("Test topic", sources)

    assert validate_report(report) == report
    assert "free language model was temporarily unavailable" in report
