"""Verify multi-turn context within one Claude Agent SDK client session."""

from __future__ import annotations

import asyncio

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient, TextBlock

from .settings import litellm_sdk_env


async def receive_text(client: ClaudeSDKClient) -> str:
    """Collect assistant text for the current turn."""
    parts: list[str] = []
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    parts.append(block.text)
    return "\n".join(parts)


async def main() -> None:
    """Send two messages and verify the second can use the first as context."""
    model, sdk_env = litellm_sdk_env()
    options = ClaudeAgentOptions(
        model=model,
        max_turns=1,
        tools=[],
        system_prompt="Follow the user's memory-test instructions exactly.",
        env=sdk_env,
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Remember this temporary codeword for our conversation: ORCHID-47. "
            "Reply only with: remembered"
        )
        await receive_text(client)

        await client.query("What temporary codeword did I give you? Reply with only the codeword.")
        answer = await receive_text(client)

    if "ORCHID-47" not in answer.upper():
        raise RuntimeError(f"Conversation context was not retained. Received: {answer!r}")

    print("Conversation context successful: ORCHID-47")


if __name__ == "__main__":
    asyncio.run(main())
