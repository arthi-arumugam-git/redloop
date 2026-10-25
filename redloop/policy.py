"""Scenario policy and JSON-friendly, typed violation records."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Policy:
    secrets: tuple[str, ...] = ()
    allowed_recipients: tuple[str, ...] = ()
    forbidden_tools: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Policy":
        values = {}
        for key in ("secrets", "allowed_recipients", "forbidden_tools"):
            value = data.get(key, [])
            if not isinstance(value, list) or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                raise ValueError(f"policy.{key} must be a list of nonempty strings")
            values[key] = tuple(value)
        return cls(**values)


@dataclass(frozen=True)
class Violation:
    tool: str
    action_index: int
    detail: str
    kind: str = field(init=False, default="violation")


@dataclass(frozen=True)
class Exfiltration(Violation):
    kind: str = field(init=False, default="exfiltration")


@dataclass(frozen=True)
class UnauthorizedSend(Violation):
    kind: str = field(init=False, default="unauthorized_send")


@dataclass(frozen=True)
class DestructiveAction(Violation):
    kind: str = field(init=False, default="destructive_action")


@dataclass(frozen=True)
class PolicyOverride(Violation):
    kind: str = field(init=False, default="policy_override")
