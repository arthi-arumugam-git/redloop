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


def _fnum(value: Any) -> float | None:
    try:
        return None if value is None or isinstance(value, bool) else float(value)
    except (TypeError, ValueError):
        return None


def latency_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per agent: runs, timed runs, total/mean/p95 seconds, tokens and USD (None when unrecorded)."""
    groups: dict[str, dict[str, Any]] = defaultdict(lambda: {"runs": 0, "secs": [], "tokens": [], "usd": []})
    for row in rows:
        g = groups[row["agent"]]
        g["runs"] += 1
        for key, field in (("secs", "seconds"), ("tokens", "tokens"), ("usd", "usd")):
            val = _fnum(row.get(field))
            if val is not None:
                g[key].append(val)
    out = []
    for agent, g in sorted(groups.items()):
        secs = sorted(g["secs"])
        p95 = secs[min(len(secs) - 1, max(0, int(round(0.95 * len(secs))) - 1))] if secs else None
        out.append({"agent": agent, "runs": g["runs"], "timed": len(secs),
                    "total_s": sum(secs) if secs else None,
                    "mean_s": sum(secs) / len(secs) if secs else None, "p95_s": p95,
                    "tokens": int(sum(g["tokens"])) if g["tokens"] else None,
                    "usd": sum(g["usd"]) if g["usd"] else None})
    return out


def latency_report(rows: list[dict[str, Any]]) -> str:
    """Markdown cost/latency table. Offline runs record seconds; tokens/USD are N/A until a real model is called."""
    summary = latency_summary(rows)
    if not summary:
        return ""

    def sec(v: float | None) -> str:
        return "N/A" if v is None else (f"{v * 1000:.2f} ms" if v < 1 else f"{v:.2f} s")

    lines = ["| Agent | Runs | Timed | Total | Mean latency | p95 latency | Tokens | USD |",
             "|---|---|---|---|---|---|---|---|"]
    for s in summary:
        tokens = "N/A" if s["tokens"] is None else str(s["tokens"])
        usd = "N/A" if s["usd"] is None else "$" + format(s["usd"], ".4f")
        lines.append(f"| {s['agent']} | {s['runs']} | {s['timed']} | {sec(s['total_s'])} | {sec(s['mean_s'])} | "
                     f"{sec(s['p95_s'])} | {tokens} | {usd} |")
    return "\n".join(lines) + "\n"


def overall_asr(rows: list[dict[str, Any]], agent: str) -> float | None:
    red = trials = 0
    for row in rows:
        if row.get("agent") == agent and row.get("status") in ("red", "green"):
            trials += 1
            red += row["status"] == "red"
    return red / trials if trials else None


def badge_svg(label: str, value: str, color: str) -> str:
    """Self-contained shields-style SVG (no network)."""
    lw, vw = 6 * len(label) + 12, 6 * len(value) + 12
    w = lw + vw
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="{label}: {value}">'
            f'<rect width="{lw}" height="20" fill="#555"/><rect x="{lw}" width="{vw}" height="20" fill="{color}"/>'
            f'<g fill="#fff" text-anchor="middle" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11">'
            f'<text x="{lw / 2}" y="14">{label}</text><text x="{lw + vw / 2}" y="14">{value}</text></g></svg>\n')


def asr_badge(rows: list[dict[str, Any]], agent: str = "guarded") -> tuple[str, str]:
    """(svg, value). Green at 0%, orange <=10%, red above, grey 'unknown' if no completed runs."""
    asr = overall_asr(rows, agent)
    if asr is None:
        value, color = "unknown", "#9f9f9f"
    else:
        value = f"{asr:.0%}"
        color = "#4c1" if asr == 0 else ("#fe7d37" if asr <= 0.10 else "#e05d44")
    return badge_svg(f"RedLoop ASR ({agent})", value, color), value
