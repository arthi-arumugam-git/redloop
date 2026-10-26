import time
"""Load a fixture, inject one payload, run a fresh sandbox, judge and append."""

from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
from importlib import resources
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from redloop.judge import judge
from redloop.policy import Policy
from redloop.sandbox import Sandbox, inject
from redloop.targets import Agent, AgentUnavailable, make_agent

DEFAULT_RESULTS = Path("results/results.jsonl")


def list_scenarios() -> list[str]:
    return sorted(
        entry.name[:-5]
        for entry in resources.files("redloop.scenarios").iterdir()
        if entry.name.endswith(".json") and entry.is_file()
    )


def load_scenario(scenario: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(scenario, dict):
        data = deepcopy(scenario)
    elif str(scenario) in list_scenarios():
        data = json.loads(
            resources.files("redloop.scenarios").joinpath(f"{scenario}.json").read_text(
                encoding="utf-8"
            )
        )
    else:
        path = Path(scenario)
        if not path.is_file():
            raise ValueError(f"Unknown scenario: {scenario}")
        data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Scenario must be a JSON object")
    for key in ("name", "task", "injection_location", "seed_payload"):
        if not isinstance(data.get(key), str) or not data[key]:
            raise ValueError(f"Scenario requires a nonempty {key} string")
    for key in ("state", "policy"):
        if not isinstance(data.get(key), dict):
            raise ValueError(f"Scenario requires a {key} object")
    Policy.from_dict(data["policy"])
    if not isinstance(data.get("allowed_tools"), list) or not all(
        isinstance(tool, str) and tool for tool in data["allowed_tools"]
    ):
        raise ValueError("Scenario requires an allowed_tools list of tool names")
    entrypoints = data.get("entrypoints")
    if not isinstance(entrypoints, list) or not entrypoints:
        raise ValueError("Scenario requires at least one trusted entrypoint")
    for entry in entrypoints:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("tool"), str)
            or not isinstance(entry.get("arguments"), dict)
        ):
            raise ValueError("Each entrypoint requires a tool and arguments object")
    return data


def append_result(row: dict[str, Any], path: str | Path = DEFAULT_RESULTS) -> None:
    # Serialize before opening so an invalid row cannot leave a partial line.
    line = json.dumps(row, ensure_ascii=True, allow_nan=False, sort_keys=True)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as stream:
        stream.write(line + "\n")


def run_scenario(
    scenario: str | Path | dict[str, Any],
    agent: str | Agent,
    payload: str | None = None,
    *,
    results_path: str | Path | None = DEFAULT_RESULTS,
) -> dict[str, Any]:
    """Run one isolated experiment; None selects the seed, '' is a control.

    RED/GREEN judge completed runs only. Unavailable agents are SKIPPED and
    execution failures are ERROR, while retaining any side-effect evidence.
    """
    fixture = load_scenario(scenario)
    target = make_agent(agent) if isinstance(agent, str) else agent
    attack = fixture["seed_payload"] if payload is None else payload
    sandbox = Sandbox(fixture["state"])
    inject(sandbox.state, attack, fixture["injection_location"])
    response = ""
    error = None
    status = None
    started = time.perf_counter()
    try:
        response = target.run(sandbox, fixture)
    except AgentUnavailable as exc:
        status, error = "skipped", str(exc)
    except Exception as exc:
        status, error = "error", f"{type(exc).__name__}: {exc}"
    seconds = round(time.perf_counter() - started, 6)
    violations = judge(sandbox.action_log, fixture["policy"])
    row = {
        "run_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario": fixture["name"],
        "agent": target.name,
        "payload": attack,
        "status": status or ("red" if violations else "green"),
        "score": len(violations),
        "violations": [asdict(violation) for violation in violations],
        "actions": deepcopy(sandbox.action_log),
        "response": response,
        "seconds": seconds,
    }
    if error is not None:
        row["error"] = error
    if results_path is not None:
        append_result(row, results_path)
    return row
