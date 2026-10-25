"""In-memory Gmail tools."""

from typing import Any

from .base import Sandbox, require_string, tool


@tool("gmail.list_inbox")
def list_inbox(sandbox: Sandbox) -> list[dict[str, Any]]:
    return [
        {key: email[key] for key in ("id", "from", "to", "subject") if key in email}
        for email in sandbox.state.get("gmail", {}).get("inbox", [])
    ]


@tool("gmail.read_email")
def read_email(sandbox: Sandbox, email_id: str) -> dict[str, Any]:
    require_string(email_id, "email_id")
    for email in sandbox.state.get("gmail", {}).get("inbox", []):
        if email.get("id") == email_id:
            return email
    raise ValueError(f"Unknown email: {email_id}")


@tool("gmail.send_email")
def send_email(sandbox: Sandbox, to: str, subject: str, body: str) -> dict[str, Any]:
    require_string(to, "to")
    require_string(subject, "subject", nonempty=False)
    require_string(body, "body", nonempty=False)
    sent = sandbox.state.setdefault("gmail", {}).setdefault("sent", [])
    email = {"id": f"sent-{len(sent) + 1}", "to": to, "subject": subject, "body": body}
    sent.append(email)
    return email
