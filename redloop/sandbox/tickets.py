"""In-memory support-ticket tools (helpdesk queue with screenshot attachments).

``tickets.read_attachment`` returns the attachment's ``ocr_text``: it simulates a
multimodal agent reading text burned into a customer screenshot. That leaf is the
PixelInject injection point: pixels become instructions.
"""

from typing import Any

from .base import Sandbox, require_string, tool


def _tickets(sandbox: Sandbox) -> list[dict[str, Any]]:
    return sandbox.state.get("tickets", {}).get("tickets", [])


def _ticket(sandbox: Sandbox, ticket_id: str) -> dict[str, Any]:
    require_string(ticket_id, "ticket_id")
    for ticket in _tickets(sandbox):
        if ticket.get("id") == ticket_id:
            return ticket
    raise ValueError(f"Unknown ticket: {ticket_id}")


@tool("tickets.list_tickets")
def list_tickets(sandbox: Sandbox) -> list[dict[str, Any]]:
    return [
        {key: ticket[key] for key in ("id", "subject", "status", "customer") if key in ticket}
        for ticket in _tickets(sandbox)
    ]


@tool("tickets.read_ticket")
def read_ticket(sandbox: Sandbox, ticket_id: str) -> dict[str, Any]:
    ticket = _ticket(sandbox, ticket_id)
    # Attachment bodies (OCR text) are only exposed via read_attachment.
    summary = {key: value for key, value in ticket.items() if key != "attachments"}
    summary["attachments"] = [
        {key: item[key] for key in ("id", "filename", "mime_type") if key in item}
        for item in ticket.get("attachments", [])
    ]
    return summary


@tool("tickets.read_attachment")
def read_attachment(sandbox: Sandbox, ticket_id: str, attachment_id: str) -> dict[str, Any]:
    require_string(attachment_id, "attachment_id")
    for item in _ticket(sandbox, ticket_id).get("attachments", []):
        if item.get("id") == attachment_id:
            return item
    raise ValueError(f"Unknown attachment: {ticket_id}/{attachment_id}")
