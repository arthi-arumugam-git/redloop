"""JSON-only state and an audit log for deterministic, local tool simulation."""

import inspect
import json
from functools import wraps
from typing import Any, Callable


_TOOLS: dict[str, Callable[..., Any]] = {}


def _snapshot(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, allow_nan=False))
    except (TypeError, ValueError) as exc:
        raise ValueError("Sandbox values must be JSON serializable") from exc


def require_string(value: Any, name: str, *, nonempty: bool = True) -> str:
    """Validate string arguments before a tool mutates state."""
    if not isinstance(value, str) or (nonempty and not value.strip()):
        raise ValueError(f"{name} must be {'a nonempty' if nonempty else 'a'} string")
    return value


class Sandbox:
    """Own a scenario state snapshot; simulate and record tools without network I/O."""

    def __init__(self, state: dict[str, Any]):
        if not isinstance(state, dict):
            raise ValueError("Sandbox state must be a JSON object")
        self.state: dict[str, Any] = _snapshot(state)
        self.action_log: list[dict[str, Any]] = []

    def call(self, tool: str, **arguments: Any) -> Any:
        function = _TOOLS.get(tool)
        if function is None:
            return self._fail(tool, arguments, f"Unknown tool: {tool}")
        return function(self, **arguments)

    def record_blocked(self, tool: str, arguments: dict[str, Any], reason: str) -> None:
        self.action_log.append({
            "tool": tool, "arguments": _snapshot(arguments),
            "status": "blocked", "reason": reason,
        })

    def _fail(self, name: str, arguments: dict[str, Any], error: str) -> Any:
        try:
            arguments = _snapshot(arguments)
        except ValueError:
            arguments = {"_invalid_arguments": "Arguments were not JSON serializable"}
        self.action_log.append({
            "tool": name, "arguments": arguments,
            "status": "error", "error": error,
        })
        raise ValueError(error)

    def _perform(self, name: str, arguments: dict[str, Any], operation: Callable[[], Any]) -> Any:
        try:
            arguments = _snapshot(arguments)
            result = _snapshot(operation())
        except Exception as exc:
            return self._fail(name, arguments, str(exc))
        self.action_log.append({
            "tool": name, "arguments": arguments,
            "status": "ok", "result": _snapshot(result),
        })
        return result


def tool(name: str) -> Callable:
    """Register a function and audit direct calls as well as dispatcher calls."""
    def decorate(function: Callable) -> Callable:
        signature = inspect.signature(function)
        argument_names = list(signature.parameters)[1:]

        @wraps(function)
        def recorded(sandbox: Sandbox, *args: Any, **kwargs: Any) -> Any:
            arguments = dict(zip(argument_names, args))
            arguments.update(kwargs)
            try:
                signature.bind(sandbox, *args, **kwargs)
            except TypeError as exc:
                return sandbox._fail(name, arguments, str(exc))
            return sandbox._perform(name, arguments, lambda: function(sandbox, *args, **kwargs))

        _TOOLS[name] = recorded
        return recorded
    return decorate


def inject(state: dict[str, Any], payload: str, location: str) -> dict[str, Any]:
    """Append payload to an existing string leaf addressed by a dotted dict/list path.

    List indices are nonnegative decimal integers. Keys containing dots are not
    supported. The complete path and leaf are validated before any mutation.
    """
    if not isinstance(state, dict):
        raise ValueError("Injection state must be a JSON object")
    require_string(payload, "payload", nonempty=False)
    require_string(location, "location")
    parts = location.split(".")
    if any(not part for part in parts):
        raise ValueError(f"Invalid injection location: {location}")
    parent: Any = state
    for position, part in enumerate(parts):
        if isinstance(parent, dict) and part in parent:
            key: Any = part
        elif isinstance(parent, list) and part.isascii() and part.isdigit() and int(part) < len(parent):
            key = int(part)
        else:
            raise ValueError(f"Invalid injection location: {location}")
        value = parent[key]
        if position == len(parts) - 1:
            if not isinstance(value, str):
                raise ValueError("Injection location must point to a string")
            parent[key] = value + "\n" + payload
        else:
            parent = value
    return state


def _schema(name: str, description: str, arguments: dict[str, str]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name, "description": description,
            "parameters": {
                "type": "object",
                "properties": {key: {"type": "string", "description": value} for key, value in arguments.items()},
                "required": list(arguments), "additionalProperties": False,
            },
        },
    }


TOOL_SCHEMAS = [
    _schema("gmail.list_inbox", "List inbox email summaries.", {}),
    _schema("gmail.read_email", "Read a complete email.", {"email_id": "Inbox email ID"}),
    _schema("gmail.send_email", "Send an email in the local sandbox.", {"to": "Recipient email address", "subject": "Email subject", "body": "Email body"}),
    _schema("slack.list_messages", "Read messages in a Slack channel.", {"channel": "Channel name including #"}),
    _schema("slack.post_message", "Post a message in a local Slack channel.", {"channel": "Channel name including #", "text": "Message text"}),
    _schema("github.list_issues", "List issue summaries for a repository.", {"repo": "Repository name"}),
    _schema("github.read_issue", "Read a complete issue and its comments.", {"repo": "Repository name", "issue_id": "Issue ID"}),
    _schema("github.comment_issue", "Comment on an issue in the local sandbox.", {"repo": "Repository name", "issue_id": "Issue ID", "body": "Comment text"}),
    _schema("github.delete_repo", "Delete a repository in the local sandbox.", {"repo": "Repository name"}),
    _schema("x.read_timeline", "Read the local X timeline.", {}),
    _schema("x.post", "Publish a post to the local X timeline.", {"text": "Post text"}),
]
