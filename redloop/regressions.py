"""Freeze successful attacks into a replayable regression suite.

`export_suite` keeps every distinct payload that turned any target red, per
scenario. `check_suite` replays the frozen payloads against one target and
reports which still succeed, so a defense change can gate CI.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from redloop.runner import run_scenario

SUITE_VERSION = 1


def export_suite(rows: Iterable[dict[str, Any]], max_per_scenario: int = 5) -> dict[str, Any]:
    cases: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        if row.get("status") != "red" or not isinstance(row.get("payload"), str):
            continue
        key = (row["scenario"], row["payload"])
        case = cases.setdefault(key, {
            "scenario": row["scenario"],
            "payload": row["payload"],
            "broke": [],
            "violations": sorted({v.get("kind", "?") for v in row.get("violations", [])}),
            "score": row.get("score", 0),
        })
        if row.get("agent") and row["agent"] not in case["broke"]:
            case["broke"].append(row["agent"])
        case["score"] = max(case["score"], row.get("score", 0))
    by_scenario: dict[str, list[dict[str, Any]]] = {}
    for case in cases.values():
        by_scenario.setdefault(case["scenario"], []).append(case)
    selected: list[dict[str, Any]] = []
    for scenario in sorted(by_scenario):
        ranked = sorted(by_scenario[scenario], key=lambda c: (-c["score"], len(c["payload"]), c["payload"]))
        selected.extend(ranked[:max_per_scenario])
    for case in selected:
        case["broke"].sort()
    return {"version": SUITE_VERSION, "cases": selected}


def load_suite(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise ValueError("Suite must be a JSON object with a cases list")
    return data


def check_suite(suite: dict[str, Any], agent: str) -> dict[str, Any]:
    outcomes = []
    for case in suite["cases"]:
        row = run_scenario(case["scenario"], agent, case["payload"], results_path=None)
        outcomes.append({"scenario": case["scenario"], "status": row["status"],
                         "violations": [v["kind"] for v in row["violations"]]})
    regressed = [o for o in outcomes if o["status"] == "red"]
    skipped = [o for o in outcomes if o["status"] == "skipped"]
    errors = [o for o in outcomes if o["status"] == "error"]
    return {"agent": agent, "total": len(outcomes), "red": len(regressed),
            "skipped": len(skipped), "errors": len(errors), "outcomes": outcomes}


EXIT_PASS, EXIT_VULNERABLE, EXIT_USAGE, EXIT_INFRA = 0, 1, 2, 3


def suite_exit_code(summary: dict[str, Any]) -> int:
    """1 = a payload still succeeds (vulnerability); 3 = infra errors made the
    run inconclusive (UNKNOWN, never reported as safe); 0 = all cases green."""
    if summary["red"]:
        return EXIT_VULNERABLE
    if summary.get("errors"):
        return EXIT_INFRA
    return EXIT_PASS
