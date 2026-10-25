"""Pure-Python loaders for the dashboard (testable without Streamlit)."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_results(path: str | Path) -> list[dict[str, Any]]:
    """Read JSONL rows, skipping blank or corrupt lines."""
    source = Path(path)
    if not source.is_file():
        return []
    rows = []
    for line in source.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and "scenario" in row and "agent" in row:
            rows.append(row)
    return rows


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per (scenario, agent): trials, reds, ASR, max score, violation kinds."""
    groups: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {"trials": 0, "red": 0, "skipped": 0, "error": 0, "max_score": 0, "kinds": set()}
    )
    for row in rows:
        g = groups[(row["scenario"], row["agent"])]
        status = row.get("status")
        if status in ("red", "green"):
            g["trials"] += 1
            g["red"] += status == "red"
        elif status in ("skipped", "error"):
            g[status] += 1
        g["max_score"] = max(g["max_score"], int(row.get("score", 0) or 0))
        g["kinds"].update(v.get("kind", "?") for v in row.get("violations", []))
    return [
        {"scenario": s, "agent": a, "trials": g["trials"], "red": g["red"],
         "asr": round(g["red"] / g["trials"], 3) if g["trials"] else None,
         "max_score": g["max_score"], "skipped": g["skipped"], "error": g["error"],
         "violations": ", ".join(sorted(g["kinds"]))}
        for (s, a), g in sorted(groups.items())
    ]


def markdown_report(rows: list[dict[str, Any]]) -> str:
    """Pivot ASR into a Markdown table: one row per scenario, one column per agent, plus overall."""
    summary = summarize(rows)
    agents = sorted({item["agent"] for item in summary})
    scenarios = sorted({item["scenario"] for item in summary})
    if not agents:
        return "_No results yet._\n"
    cell = {(item["scenario"], item["agent"]): item for item in summary}

    def fmt(red: int, trials: int) -> str:
        return "n/a" if not trials else f"{red / trials:.0%} ({red}/{trials})"

    lines = ["| Scenario | " + " | ".join(f"{a} ASR" for a in agents) + " |",
             "|---|" + "---|" * len(agents)]
    totals = {a: [0, 0] for a in agents}
    for scenario in scenarios:
        cells = []
        for agent in agents:
            item = cell.get((scenario, agent))
            red, trials = (item["red"], item["trials"]) if item else (0, 0)
            totals[agent][0] += red
            totals[agent][1] += trials
            cells.append(fmt(red, trials))
        lines.append(f"| {scenario} | " + " | ".join(cells) + " |")
    lines.append("| **overall** | " + " | ".join(f"**{fmt(*totals[a])}**" for a in agents) + " |")
    return "\n".join(lines) + "\n"
