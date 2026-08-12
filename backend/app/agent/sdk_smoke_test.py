"""Minimal Claude Agent SDK to LiteLLM connectivity test for Phase 4."""

from __future__ import annotations

import asyncio
from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query

from .settings import litellm_sdk_env


def build_options() -> ClaudeAgentOptions:
    """Configure the SDK to use the local LiteLLM Anthropic-compatible API."""
    model, sdk_env = litellm_sdk_env()

    return ClaudeAgentOptions(
        model=model,
        max_turns=1,
        tools=[],
        system_prompt=(
            "You are a connectivity test. Reply with exactly: "
            "Claude Agent SDK connection successful"
        ),
        env=sdk_env,
    )


async def main() -> None:
    """Send one tool-free prompt and print only assistant text."""
    received_text = False

    async for message in query(
        prompt="Confirm that the SDK can reach the configured model.",
        options=build_options(),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    received_text = True
                    print(block.text)

    if not received_text:
        raise RuntimeError("The SDK completed without returning assistant text.")


if __name__ == "__main__":
    asyncio.run(main())
