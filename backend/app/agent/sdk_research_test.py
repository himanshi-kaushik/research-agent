"""Test the complete SDK web-research tool sequence."""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
    ToolUseBlock,
)

from backend.app.agent.settings import litellm_sdk_env
from backend.app.tools.sdk_web_tools import create_web_tools_server


SEARCH_TOOL = "mcp__web-tools__search_web"
READ_TOOL = "mcp__web-tools__read_webpage"


async def main() -> None:
    """Require the agent to search and read a source."""

    model, sdk_env = litellm_sdk_env()

    options = ClaudeAgentOptions(
        model=model,
        max_turns=6,
        tools=[],
        mcp_servers={
            "web-tools": create_web_tools_server(),
        },
        allowed_tools=[
            SEARCH_TOOL,
            READ_TOOL,
        ],
        system_prompt=(
            "You are a research agent. For this test, you must first call "
            "search_web. Select one relevant result and call read_webpage "
            "with its URL. Answer using only the webpage you read. "
            "Include the source URL in your answer."
        ),
        env=sdk_env,
    )

    used_tools: set[str] = set()
    final_text: list[str] = []

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Find one benefit of renewable energy using a reliable source."
        )

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock):
                        used_tools.add(block.name)
                        print(f"Agent requested tool: {block.name}")

                    elif isinstance(block, TextBlock):
                        final_text.append(block.text)

    if SEARCH_TOOL not in used_tools:
        raise RuntimeError("The agent did not use the web-search tool.")

    if READ_TOOL not in used_tools:
        raise RuntimeError("The agent did not use the webpage-reading tool.")

    if not final_text:
        raise RuntimeError("The agent did not produce a final answer.")

    print("\nResearch workflow successful")
    print(
        final_text[-1]
        .encode("ascii", errors="replace")
        .decode("ascii")
    )


if __name__ == "__main__":
    asyncio.run(main())
    