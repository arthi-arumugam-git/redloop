"""Config-driven mirror of a target agent's tools, with no MCP dependency.

The MCP server in `server.py` is a thin wrapper around `MirrorTarget`, so the
recording, injection and scoring logic is testable without a model or a client.

Run directory layout (one per campaign, kept OUTSIDE the repo for real targets):
    current_case   case id the next tool calls belong to (driver writes it)
    calls.jsonl    one line per tool call the agent made
"""

from __future__ import annotations

import copy
import json
import time
from pathlib import Path
from typing import Any

from redloop.sandbox.base import inject

ROLES = {"list", "read", "write"}
CONFIG_DIR = Path(__file__).parent / "configs"


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate a mirror config; bundled names resolve to configs/<name>.json."""
    path = Path(path)
    if not path.suffix and not path.exists():
        path = CONFIG_DIR / f"{path}.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    for key in ("server_name", "task", "state", "policy", "tools", "injection_location", "poisoned_id"):
        if key not in config:
            raise ValueError(f"Mirror config missing {key!r}")
    names = set()
    for spec in config["tools"]:
        if spec.get("role") not in ROLES:
            raise ValueError(f"Tool {spec.get('name')!r} role must be one of {sorted(ROLES)}")
        if not isinstance(spec.get("input_schema"), dict):
            raise ValueError(f"Tool {spec['name']!r} needs an input_schema object")
        if spec["name"] in names:
            raise ValueError(f"Duplicate tool name {spec['name']!r}")
        names.add(spec["name"])
    if not any(spec["role"] == "read" for spec in config["tools"]):
        raise ValueError("Mirror config needs one read tool (the untrusted input)")
    # Validates the path without mutating the config.
    inject(copy.deepcopy(config["state"]), "", config["injection_location"])
    return config


class MirrorTarget:
    def __init__(self, config: dict[str, Any], run_dir: str | Path, cases: dict[str, str]):
        self.config = config
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.cases = cases
        self.tools = {spec["name"]: spec for spec in config["tools"]}

    def current_case(self) -> str:
        # Re-read on every call: Letta may keep one server process across cases.
        marker = self.run_dir / "current_case"
        return marker.read_text(encoding="utf-8").strip() if marker.exists() else "control"

    def inbox(self, case_id: str) -> list[dict[str, Any]]:
        state = copy.deepcopy(self.config["state"])
        payload = self.cases.get(case_id)
        if payload:
            inject(state, payload, self.config["injection_location"])
        return state["inbox"]

    def call(self, name: str, arguments: dict[str, Any] | None) -> Any:
        arguments = dict(arguments or {})
        case_id = self.current_case()
        spec = self.tools.get(name)
        record = {"ts": time.time(), "case": case_id, "tool": name, "arguments": arguments}
        try:
            if spec is None:
                raise ValueError(f"Unknown tool: {name}")
            result = self._dispatch(spec, arguments, case_id)
        except ValueError as exc:
            self._log({**record, "status": "error", "error": str(exc)})
            raise
        self._log({**record, "status": "ok", "role": spec["role"],
                   "exposed": spec["role"] == "read" and result.get("id") == self.config["poisoned_id"]})
        return result

    def _dispatch(self, spec: dict[str, Any], arguments: dict[str, Any], case_id: str) -> Any:
        inbox = self.inbox(case_id)
        if spec["role"] == "list":
            limit = arguments.get("limit") or len(inbox)
            return [{k: m[k] for k in spec.get("fields", ["id", "from", "subject"]) if k in m}
                    for m in inbox[: int(limit)]]
        if spec["role"] == "read":
            wanted = arguments.get(spec.get("id_arg", "id"))
            for message in inbox:
                if message["id"] == wanted:
                    return message
            raise ValueError(f"Unknown email: {wanted}")
        # Recording stub: look like a real success so the agent does not retry.
        sent = sum(1 for r in self.read_log() if r.get("role") == "write") + 1
        return {"id": f"sent-{sent}", "status": "sent"}

    def _log(self, record: dict[str, Any]) -> None:
        with (self.run_dir / "calls.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def read_log(self) -> list[dict[str, Any]]:
        path = self.run_dir / "calls.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
