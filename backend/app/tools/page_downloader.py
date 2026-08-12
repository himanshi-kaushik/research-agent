"""Safe webpage downloading for the Research Agent."""

from urllib.parse import urlparse

import httpx


MAX_PAGE_BYTES = 2_000_000

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ResearchAgent/1.0; "
        "+https://github.com/)"
    )
}


def validate_url(url: str) -> None:
    """Allow only normal public HTTP and HTTPS URLs."""

    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are allowed.")

    if not parsed.hostname:
        raise ValueError("The URL must contain a hostname.")

    if parsed.hostname.lower() in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Local addresses are not allowed.")


async def download_page(url: str) -> str:
    """Download a webpage and return its HTML text."""

    validate_url(url)

    timeout = httpx.Timeout(15.0, connect=5.0)

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=timeout,
        follow_redirects=True,
    ) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()

            if "text/html" not in content_type and "text/plain" not in content_type:
                raise ValueError(
                    f"Unsupported webpage content type: {content_type}"
                )

            content = bytearray()

            async for chunk in response.aiter_bytes():
                content.extend(chunk)

                if len(content) > MAX_PAGE_BYTES:
                    raise ValueError(
                        "The webpage is larger than the allowed 2 MB limit."
                    )

            encoding = response.encoding or "utf-8"
            return bytes(content).decode(encoding, errors="replace")
        