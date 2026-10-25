"""In-memory X tools."""

from typing import Any

from .base import Sandbox, require_string, tool


@tool("x.read_timeline")
def read_timeline(sandbox: Sandbox) -> list[dict[str, Any]]:
    return sandbox.state.get("x", {}).get("timeline", [])


@tool("x.post")
def post(sandbox: Sandbox, text: str) -> dict[str, Any]:
    require_string(text, "text")
    service = sandbox.state.setdefault("x", {})
    posts = service.setdefault("posts", [])
    message = {"id": f"post-{len(posts) + 1}", "author": "redloop-agent", "text": text}
    posts.append(message)
    service.setdefault("timeline", []).append(dict(message))
    return message
