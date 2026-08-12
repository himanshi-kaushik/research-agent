"""Verify that the Claude Agent SDK executes an in-process custom tool."""

from __future__ import annotations

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    tool,
)

from .settings import litellm_sdk_env


@tool(
    "get_phase_status",
    "Return the verified status of a Research Agent project phase.",
    {"phase": int},
)
async def get_phase_status(args: dict) -> dict:
    """Return deterministic local data so execution can be verified."""
    phase = args["phase"]
    statuses = {
        1: "completed: project setup",
        2: "completed: Vue and FastAPI foundation",
        3: "completed: LiteLLM and OpenRouter integration",
        4: "in progress: Claude Agent SDK integration",
        5: "pending: web research tools",
    }
    status = statuses.get(phase, "not scheduled")
    return {"content": [{"type": "text", "text": f"Phase {phase} is {status}."}]}


async def main() -> None:
    """Require the model to call the tool and verify that it did so."""
    model, sdk_env = litellm_sdk_env()
    server = create_sdk_mcp_server(
        name="research-tools",
        version="1.0.0",
        tools=[get_phase_status],
    )
    tool_name = "mcp__research-tools__get_phase_status"
    options = ClaudeAgentOptions(
        model=model,
        max_turns=3,
        tools=[],
        mcp_servers={"research-tools": server},
        allowed_tools=[tool_name],
        system_prompt=(
            "You are testing tool execution. You must call get_phase_status "
            "to answer phase-status questions. Never guess the status."
        ),
        env=sdk_env,
    )

    tool_used = False
    final_text: list[str] = []

    async with ClaudeSDKClient(options=options) as client:
        await client.query("What is the verified status of Phase 4?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock) and block.name == tool_name:
                        tool_used = True
                    elif isinstance(block, TextBlock):
                        final_text.append(block.text)

    if not tool_used:
        raise RuntimeError("The model answered without invoking get_phase_status.")

    print("Tool execution successful")
    if final_text:
        print(final_text[-1].encode("ascii", errors="replace").decode("ascii"))


if __name__ == "__main__":
    asyncio.run(main())
