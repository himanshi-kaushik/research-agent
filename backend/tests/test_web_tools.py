"""Tests for the Phase 5 web-research tools."""

import pytest

from backend.app.tools.page_downloader import validate_url
from backend.app.tools.text_extractor import extract_page_text
from backend.app.tools.web_search import search_web


@pytest.mark.asyncio
async def test_search_rejects_empty_query():
    with pytest.raises(
        ValueError,
        match="query cannot be empty",
    ):
        await search_web("   ")


def test_url_rejects_unsupported_scheme():
    with pytest.raises(
        ValueError,
        match="Only HTTP and HTTPS",
    ):
        validate_url("file:///private/document.txt")


def test_url_rejects_localhost():
    with pytest.raises(
        ValueError,
        match="Local addresses",
    ):
        validate_url("http://localhost:4000/health")


def test_url_accepts_public_https_address():
    validate_url("https://example.com/article")


def test_extractor_returns_clean_text():
    html = """
    <html>
        <body>
            <article>
                <h1>Renewable Energy</h1>
                <p>
                    Renewable energy can reduce greenhouse gas emissions
                    and improve air quality for communities worldwide.
                </p>
                <p>
                    Solar and wind power can also create employment
                    opportunities and improve energy security.
                </p>
            </article>
        </body>
    </html>
    """

    result = extract_page_text(
        html,
        "https://example.com/renewable-energy",
    )

    assert result["method"] in {
        "trafilatura",
        "beautifulsoup",
    }
    assert "Renewable Energy" in result["text"]
    assert "<article>" not in result["text"]


def test_empty_html_is_rejected():
    with pytest.raises(
        ValueError,
        match="HTML is empty",
    ):
        extract_page_text("   ")
        