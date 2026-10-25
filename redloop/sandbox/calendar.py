"""In-memory Calendar tools."""

from typing import Any

from .base import Sandbox, require_string, tool


@tool("calendar.list_events")
def list_events(sandbox: Sandbox) -> list[dict[str, Any]]:
    return sandbox.state.get("calendar", {}).get("events", [])


@tool("calendar.create_event")
def create_event(sandbox: Sandbox, title: str, attendee: str, notes: str) -> dict[str, Any]:
    require_string(title, "title")
    require_string(attendee, "attendee")
    require_string(notes, "notes", nonempty=False)
    events = sandbox.state.setdefault("calendar", {}).setdefault("events", [])
    event = {"id": f"event-{len(events) + 1}", "title": title, "attendee": attendee, "notes": notes}
    events.append(event)
    return event


@tool("calendar.delete_event")
def delete_event(sandbox: Sandbox, event_id: str) -> dict[str, Any]:
    require_string(event_id, "event_id")
    events = sandbox.state.get("calendar", {}).get("events", [])
    for index, event in enumerate(events):
        if event.get("id") == event_id:
            events.pop(index)
            return {"event_id": event_id, "deleted": True}
    raise ValueError(f"Unknown event: {event_id}")
