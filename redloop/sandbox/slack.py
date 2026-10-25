"""In-memory Slack tools."""

from typing import Any

from .base import Sandbox, require_string, tool


def _messages(sandbox: Sandbox, channel: str) -> list[dict[str, Any]]:
    require_string(channel, "channel")
    channels = sandbox.state.get("slack", {}).get("channels", {})
    if channel not in channels:
        raise ValueError(f"Unknown Slack channel: {channel}")
    return channels[channel]


@tool("slack.list_messages")
def list_messages(sandbox: Sandbox, channel: str) -> list[dict[str, Any]]:
    return _messages(sandbox, channel)


@tool("slack.post_message")
def post_message(sandbox: Sandbox, channel: str, text: str) -> dict[str, Any]:
    require_string(text, "text")
    messages = _messages(sandbox, channel)
    message = {"id": f"slack-{len(messages) + 1}", "user": "redloop-agent", "channel": channel, "text": text}
    messages.append(message)
    return message
