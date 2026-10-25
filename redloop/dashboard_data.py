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
