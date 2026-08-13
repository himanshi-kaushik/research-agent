"""Research Agent orchestration and report generation."""

from __future__ import annotations

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
)

from backend.app.agent.settings import litellm_sdk_env
from backend.app.tools.sdk_web_tools import create_web_tools_server


SEARCH_TOOL = "mcp__web-tools__search_web"
READ_TOOL = "mcp__web-tools__read_webpage"

RESEARCH_SYSTEM_PROMPT = """
You are a careful AI Research Agent.

For a new research topic:

1. Call search_web exactly twice using two different queries.
2. After the two searches, do not call search_web again.
3. Prefer reliable sources:
   - government websites
   - universities
   - international organizations
   - peer-reviewed or established research institutions
4. Avoid relying primarily on advertisements, anonymous blogs, social media,
   content farms, or duplicated articles.
5. Select exactly two reliable webpages from different sources.
6. Call read_webpage exactly twice, once for each selected source.
7. After reading two webpages, do not call any more tools.
8. Immediately compare the two sources and write the final report.
9. Never claim that a source says something unless it appears in the webpage
   content returned by read_webpage.
10. Clearly mention uncertainty, conflicting information, or missing evidence.
11. Never invent citations, titles, statistics, or URLs.

Tool budget:
- Exactly 2 search_web calls.
- Exactly 2 read_webpage calls.
- After those 4 calls, stop using tools and write the report.

Return the final report as Markdown using this structure:

# Research Report: <topic>

## Executive Summary
A concise summary of the most important findings.

## Key Findings
A bulleted list of important evidence-based findings.

## Detailed Analysis
A clear comparison and explanation of the evidence.

## Limitations
Any limitations, uncertainty, conflicting information, or unavailable evidence.

## Sources
A numbered list containing the source title and full URL.

Use inline source numbers such as [1] and [2] when presenting factual claims.

For follow-up questions:

- Use the sources and evidence already available in the conversation.
- Do not search again when the existing research can answer the question.
- Use web tools again only when the user requests new, updated, or missing information.
- Clearly state when the existing sources are insufficient.
"""



def build_research_options() -> ClaudeAgentOptions:
    """Configure the SDK, model and web tools for research."""

    model, sdk_env = litellm_sdk_env()

    return ClaudeAgentOptions(
        model=model,
        max_turns=10,
        tools=[],
        mcp_servers={
            "web-tools": create_web_tools_server(),
        },
        allowed_tools=[
            SEARCH_TOOL,
            READ_TOOL,
        ],
        system_prompt=RESEARCH_SYSTEM_PROMPT,
        env=sdk_env,
    )


async def receive_response_text(
    client: ClaudeSDKClient,
) -> str:
    """Collect the final assistant response for one turn."""

    responses: list[str] = []

    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            text_parts = [
                block.text
                for block in message.content
                if isinstance(block, TextBlock)
            ]

            if text_parts:
                responses.append("\n".join(text_parts))

    if not responses:
        raise RuntimeError(
            "The Research Agent did not return a text response."
        )

    return responses[-1]


async def research_topic(topic: str) -> str:
    """Research a topic and return a structured Markdown report."""

    topic = topic.strip()

    if not topic:
        raise ValueError("The research topic cannot be empty.")

    async with ClaudeSDKClient(
        options=build_research_options(),
    ) as client:
        await client.query(
            f"Research this topic and produce the required report: {topic}"
        )

        return await receive_response_text(client)