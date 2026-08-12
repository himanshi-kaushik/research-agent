"""Claude Agent SDK tools for searching and reading webpages."""

import json

from claude_agent_sdk import create_sdk_mcp_server, tool

from .page_downloader import download_page
from .text_extractor import extract_page_text
from .web_search import search_web


MAX_TOOL_TEXT_CHARACTERS = 12_000


@tool(
    "search_web",
    "Search the web for reliable sources about a research topic.",
    {"query": str},
)
async def search_web_tool(args: dict) -> dict:
    """Return normalized web-search results."""

    results = await search_web(
        query=args["query"],
        max_results=5,
    )

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(
                    results,
                    ensure_ascii=False,
                    indent=2,
                ),
            }
        ]
    }


@tool(
    "read_webpage",
    "Download a webpage and extract its main readable text.",
    {"url": str},
)
async def read_webpage_tool(args: dict) -> dict:
    """Download and extract one source selected by the agent."""

    url = args["url"]

    html = await download_page(url)
    extracted = extract_page_text(html, url)

    text = extracted["text"]

    if len(text) > MAX_TOOL_TEXT_CHARACTERS:
        text = text[:MAX_TOOL_TEXT_CHARACTERS]

    result = {
        "url": url,
        "extraction_method": extracted["method"],
        "text": text,
    }

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(
                    result,
                    ensure_ascii=False,
                    indent=2,
                ),
            }
        ]
    }


def create_web_tools_server():
    """Create the in-process MCP server containing the research tools."""

    return create_sdk_mcp_server(
        name="web-tools",
        version="1.0.0",
        tools=[
            search_web_tool,
            read_webpage_tool,
        ],
    )
