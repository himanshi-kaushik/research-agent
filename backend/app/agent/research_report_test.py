"""Run and verify a complete multi-source research report."""

from __future__ import annotations

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKClient,
    TextBlock,
    ToolUseBlock,
)

from backend.app.agent.research_agent import (
    READ_TOOL,
    SEARCH_TOOL,
    build_research_options,
)


async def main() -> None:
    """Research a topic and verify the expected workflow."""

    search_count = 0
    read_count = 0
    responses: list[str] = []

    async with ClaudeSDKClient(
        options=build_research_options(),
    ) as client:
        await client.query(
            "Research the main benefits and limitations of renewable "
            "energy adoption."
        )

        async for message in client.receive_response():
            if not isinstance(message, AssistantMessage):
                continue

            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"Agent requested: {block.name}")

                    if block.name == SEARCH_TOOL:
                        search_count += 1

                    elif block.name == READ_TOOL:
                        read_count += 1

                elif isinstance(block, TextBlock):
                    responses.append(block.text)

    if search_count < 2:
        raise RuntimeError(
            f"Expected at least 2 searches, received {search_count}."
        )

    if read_count < 2:
        raise RuntimeError(
            f"Expected at least 2 webpage reads, received {read_count}."
        )

    if not responses:
        raise RuntimeError("The agent did not produce a report.")

    report = responses[-1]

    required_sections = [
        "# Research Report:",
        "## Executive Summary",
        "## Key Findings",
        "## Detailed Analysis",
        "## Limitations",
        "## Sources",
    ]

    missing_sections = [
        section
        for section in required_sections
        if section not in report
    ]

    if missing_sections:
        raise RuntimeError(
            f"Report is missing sections: {missing_sections}"
        )

    print("\nMulti-source research workflow successful")
    print(f"Searches performed: {search_count}")
    print(f"Webpages read: {read_count}")
    print("\n" + report.encode(
        "ascii",
        errors="replace",
    ).decode("ascii"))


if __name__ == "__main__":
    asyncio.run(main())
    