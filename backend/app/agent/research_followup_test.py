"""Verify follow-up questions use existing research context."""

from __future__ import annotations

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKClient,
    TextBlock,
    ToolUseBlock,
)

from backend.app.agent.research_agent import (
    build_research_options,
)


async def receive_turn(client: ClaudeSDKClient) -> tuple[str, int]:
    """Collect assistant text and count tool calls for one turn."""

    responses: list[str] = []
    tool_calls = 0

    async for message in client.receive_response():
        if not isinstance(message, AssistantMessage):
            continue

        for block in message.content:
            if isinstance(block, ToolUseBlock):
                tool_calls += 1

            elif isinstance(block, TextBlock):
                responses.append(block.text)

    return responses[-1] if responses else "", tool_calls


async def main() -> None:
    """Research once and ask a contextual follow-up question."""

    async with ClaudeSDKClient(
        options=build_research_options(),
    ) as client:
        await client.query(
            "Research two important benefits and two limitations "
            "of renewable energy adoption."
        )

        report, research_tool_calls = await receive_turn(client)

        if not report:
            raise RuntimeError("The initial report was not generated.")

        print(
            f"Initial research tool calls: {research_tool_calls}"
        )

        await client.query(
            "Based only on the research you just completed, "
            "which limitation appears most important and why? "
            "Answer in one short paragraph without searching again."
        )

        followup, followup_tool_calls = await receive_turn(client)

        if not followup:
            raise RuntimeError("No follow-up answer was generated.")

        if followup_tool_calls != 0:
            raise RuntimeError(
                "The agent searched again even though the existing "
                "research was sufficient."
            )

        print("Follow-up context successful")
        print(
            followup
            .encode("ascii", errors="replace")
            .decode("ascii")
        )


if __name__ == "__main__":
    asyncio.run(main())
    