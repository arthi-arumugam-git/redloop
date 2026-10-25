"""Stdlib command-line entry point."""

import argparse
from pathlib import Path
import sys

from redloop.runner import DEFAULT_RESULTS, list_scenarios, load_scenario, run_scenario


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="redloop", description="Red-team tool-using agents offline.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List bundled scenarios")
    run = commands.add_parser("run", help="Inject, run, judge and append results")
    run.add_argument("--scenario", default="email_exfil", help="Bundled name or JSON path")
    run.add_argument("--agent", choices=("naive", "guarded", "llama"), default="naive")
    run.add_argument("--all", action="store_true", help="Run all bundled scenarios; overrides --scenario")
    run.add_argument("--payload", default=None, help="Custom injection (empty string runs a control)")
    run.add_argument("--results", type=Path, default=DEFAULT_RESULTS, help="Append-only JSONL destination")
    args = parser.parse_args(argv)

    if args.command == "list":
        for name in list_scenarios():
            print(f"{name:28} {load_scenario(name).get('description', '')}")
        return 0

    names = list_scenarios() if args.all else [args.scenario]
    try:
        scenarios = [load_scenario(name) for name in names]
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"{'STATUS':7} {'SCENARIO':28} {'AGENT':8} VIOLATIONS")
    print("-" * 76)
    failed = False
    for scenario in scenarios:
        try:
            row = run_scenario(scenario, args.agent, args.payload, results_path=args.results)
        except (ValueError, OSError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            failed = True
            continue
        label = "SKIP" if row["status"] == "skipped" else row["status"].upper()
        findings = ", ".join(item["kind"] for item in row["violations"]) or "-"
        print(f"{label:7} {row['scenario']:28} {row['agent']:8} {findings}")
        if "error" in row:
            print(f"        {row['error']}")
        failed = failed or row["status"] == "error"
    print(f"Results: {args.results}")
    # Finding a vulnerability is a successful experiment, including in CI.
    return 1 if failed else 0
