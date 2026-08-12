"""Web-search functionality for the Research Agent."""

import asyncio

from ddgs import DDGS


def _search_sync(query: str, max_results: int) -> list[dict[str, str]]:
    """Perform the blocking DDGS search."""

    results = DDGS().text(
        query,
        max_results=max_results,
    )

    return [
        {
            "title": result.get("title", ""),
            "url": result.get("href", ""),
            "snippet": result.get("body", ""),
        }
        for result in results
        if result.get("href")
    ]


async def search_web(
    query: str,
    max_results: int = 5,
) -> list[dict[str, str]]:
    """Search the web and return normalized results."""

    query = query.strip()

    if not query:
        raise ValueError("The search query cannot be empty.")

    max_results = max(1, min(max_results, 10))

    return await asyncio.to_thread(
        _search_sync,
        query,
        max_results,
    )