"""Extract useful article text from downloaded HTML."""

import re

import trafilatura
from bs4 import BeautifulSoup


MIN_EXTRACTED_CHARACTERS = 100


def _clean_whitespace(text: str) -> str:
    """Remove unnecessary blank lines and repeated spaces."""

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
    ]

    return "\n".join(line for line in lines if line)


def _beautifulsoup_fallback(html: str) -> str:
    """Extract visible text when Trafilatura cannot find enough content."""

    soup = BeautifulSoup(html, "html.parser")

    for element in soup(
        [
            "script",
            "style",
            "noscript",
            "nav",
            "header",
            "footer",
            "aside",
            "form",
        ]
    ):
        element.decompose()

    return _clean_whitespace(
        soup.get_text(separator="\n")
    )


def extract_page_text(
    html: str,
    url: str | None = None,
) -> dict[str, str]:
    """Extract main text and report which extraction method was used."""

    if not html.strip():
        raise ValueError("The downloaded HTML is empty.")

    extracted = trafilatura.extract(
        html,
        url=url,
        output_format="txt",
        include_comments=False,
        include_tables=False,
        favor_precision=True,
    )

    if extracted:
        extracted = _clean_whitespace(extracted)

    if extracted and len(extracted) >= MIN_EXTRACTED_CHARACTERS:
        return {
            "text": extracted,
            "method": "trafilatura",
        }

    fallback_text = _beautifulsoup_fallback(html)

    if not fallback_text:
        raise ValueError(
            "No useful text could be extracted from the webpage."
        )

    return {
        "text": fallback_text,
        "method": "beautifulsoup",
    }
