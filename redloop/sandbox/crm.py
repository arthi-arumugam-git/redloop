"""In-memory CRM tools (contacts and notes)."""

from typing import Any

from .base import Sandbox, require_string, tool


def _contacts(sandbox: Sandbox) -> dict[str, Any]:
    return sandbox.state.get("crm", {}).get("contacts", {})


@tool("crm.get_contact")
def get_contact(sandbox: Sandbox, contact_id: str) -> dict[str, Any]:
    require_string(contact_id, "contact_id")
    contact = _contacts(sandbox).get(contact_id)
    if contact is None:
        raise ValueError(f"Unknown contact: {contact_id}")
    return contact


@tool("crm.update_contact")
def update_contact(sandbox: Sandbox, contact_id: str, field: str, value: str) -> dict[str, Any]:
    require_string(field, "field")
    require_string(value, "value", nonempty=False)
    require_string(contact_id, "contact_id")
    contact = _contacts(sandbox).get(contact_id)
    if contact is None:
        raise ValueError(f"Unknown contact: {contact_id}")
    contact[field] = value
    # Echo only the change so record contents cannot re-trigger instructions.
    return {"contact_id": contact_id, "field": field, "updated": True}


@tool("crm.delete_contact")
def delete_contact(sandbox: Sandbox, contact_id: str) -> dict[str, Any]:
    require_string(contact_id, "contact_id")
    if _contacts(sandbox).pop(contact_id, None) is None:
        raise ValueError(f"Unknown contact: {contact_id}")
    return {"contact_id": contact_id, "deleted": True}
