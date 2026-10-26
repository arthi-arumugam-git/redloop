"""Offline targets: intentional instruction following and a guarded baseline."""

import json
from typing import Any, Iterator

from redloop.sandbox import Sandbox
from redloop.targets.base import Agent

CALL_MARKER = "REDLOOP_CALL "


def _strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)


def _instructions(output: Any) -> Iterator[dict[str, Any]]:
    decoder = json.JSONDecoder()
    for text in _strings(output):
        for fragment in text.split(CALL_MARKER)[1:]:
            try:
                instruction, _ = decoder.raw_decode(fragment.lstrip())
            except ValueError:
                continue
            if (
                isinstance(instruction, dict)
                and isinstance(instruction.get("tool"), str)
                and isinstance(instruction.get("arguments"), dict)
            ):
                yield instruction


def spotlight(output: Any) -> str:
    """Mark data as untrusted; JSON escaping prevents literal closing tags."""
    data = json.dumps(output, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e")
    return f"<untrusted_tool_output>{data}</untrusted_tool_output>"


class RuleAgent(Agent):
    def __init__(
        self,
        guarded: bool = False,
        max_actions: int = 16,
        *,
        allowlist: bool | None = None,
        spotlight: bool | None = None,
        name: str | None = None,
    ):
        if max_actions < 1:
            raise ValueError("max_actions must be positive")
        self.guarded = guarded
        # Each defense layer can be toggled alone for ablation studies.
        self.allowlist = guarded if allowlist is None else allowlist
        self.spotlight = guarded if spotlight is None else spotlight
        self.max_actions = max_actions
        self.name = name or ("guarded" if guarded else "naive")

    def run(self, sandbox: Sandbox, scenario: dict[str, Any]) -> str:
        queue = list(scenario["entrypoints"])
        allowed_tools = set(scenario["allowed_tools"])
        observations = []
        count = 0
        while queue:
            if count >= self.max_actions:
                raise RuntimeError("Target action budget exhausted")
            instruction = queue.pop(0)
            tool, arguments = instruction["tool"], instruction["arguments"]
            count += 1
            if self.allowlist and tool not in allowed_tools:
                sandbox.record_blocked(tool, arguments, "Tool is outside the trusted allowlist")
                continue
            output = sandbox.call(tool, **arguments)
            if self.spotlight:
                # Only trusted entrypoints can schedule actions. Spotlighted text
                # is reported as data, never reparsed as authority.
                observations.append(spotlight(output))
            else:
                queue.extend(_instructions(output))
                observations.append(json.dumps(output, ensure_ascii=True))
        return "\n".join(observations)


class GuardedAgent(RuleAgent):
    def __init__(self, max_actions: int = 16):
        super().__init__(guarded=True, max_actions=max_actions)
