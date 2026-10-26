"""Stdlib command-line entry point."""

import argparse
import json
from pathlib import Path
import sys

from redloop.runner import DEFAULT_RESULTS, list_scenarios, load_scenario, run_scenario


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="redloop", description="Red-team tool-using agents offline.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List bundled scenarios")
    run = commands.add_parser("run", help="Inject, run, judge and append results")
    run.add_argument("--scenario", default="email_exfil", help="Bundled name or JSON path")
    run.add_argument("--agent", choices=("naive", "guarded", "llama", "llama-guarded"), default="naive")
    run.add_argument("--all", action="store_true", help="Run all bundled scenarios; overrides --scenario")
    run.add_argument("--payload", default=None, help="Custom injection (empty string runs a control)")
    run.add_argument("--results", type=Path, default=DEFAULT_RESULTS, help="Append-only JSONL destination")
    attack = commands.add_parser("attack", help="Offline mutate-and-score search (no model needed)")
    attack.add_argument("--scenario", default="email_exfil", help="Bundled name or JSON path")
    attack.add_argument("--all", action="store_true", help="Search every bundled scenario")
    attack.add_argument("--agents", default="naive,guarded", help="Comma-separated targets")
    attack.add_argument("--generations", type=int, default=4)
    attack.add_argument("--population", type=int, default=6)
    attack.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    report = commands.add_parser("report", help="Markdown ASR table (scenario x agent) from results JSONL")
    report.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    report.add_argument("--out", type=Path, default=None, help="Also write the table to this file")
    report.add_argument("--no-latency", action="store_true", help="Omit the cost/latency table")
    badge = commands.add_parser("badge", help="Write an offline SVG ASR badge and print the README markdown snippet")
    badge.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    badge.add_argument("--agent", default="guarded")
    badge.add_argument("--out", type=Path, default=Path("assets/redloop-asr-badge.svg"))
    export = commands.add_parser("export-suite", help="Freeze red payloads into a regression suite JSON")
    export.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    export.add_argument("--out", type=Path, default=Path("results/regression_suite.json"))
    export.add_argument("--max-per-scenario", type=int, default=5)
    check = commands.add_parser("check-suite", help="Replay a regression suite; exit 1 if any case is red, 3 on infra errors")
    check.add_argument("--suite", type=Path, default=Path("results/regression_suite.json"))
    check.add_argument("--agent", choices=("naive", "guarded", "llama", "llama-guarded"), default="guarded")
    args = parser.parse_args(argv)

    if args.command == "export-suite":
        from redloop.dashboard_data import load_results
        from redloop.regressions import export_suite
        suite = export_suite(load_results(args.results), args.max_per_scenario)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(suite, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {len(suite['cases'])} cases to {args.out}")
        return 0

    if args.command == "check-suite":
        from redloop.regressions import check_suite, load_suite, suite_exit_code
        try:
            summary = check_suite(load_suite(args.suite), args.agent)
        except (ValueError, OSError) as exc:
            parser.error(str(exc))
        for o in summary["outcomes"]:
            print(f"{o['status'].upper():7} {o['scenario']:28} {', '.join(o['violations']) or '-'}")
        print(f"{summary['agent']}: {summary['red']}/{summary['total']} cases still succeed")
        if summary["errors"] and not summary["red"]:
            print(f"UNKNOWN: {summary['errors']} case(s) hit infra errors; result is inconclusive, not safe",
                  file=sys.stderr)
        return suite_exit_code(summary)

    if args.command == "report":
        from redloop.dashboard_data import latency_report, load_results, markdown_report
        rows = load_results(args.results)
        table = markdown_report(rows)
        latency = "" if args.no_latency else latency_report(rows)
        if latency:
            table += ("\n### Cost and latency\n\n" + latency
                      + "\n_Seconds are wall-clock per scenario run. Tokens/USD are N/A for offline mock targets._\n")
        print(table, end="")
        if args.out:
            args.out.write_text(table, encoding="utf-8")
        return 0

    if args.command == "badge":
        from redloop.dashboard_data import asr_badge, load_results
        svg, value = asr_badge(load_results(args.results), args.agent)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(svg, encoding="utf-8")
        print(f"Wrote {args.out} (ASR {value})")
        print(f"![RedLoop ASR]({args.out.as_posix()})")
        return 0

    if args.command == "attack":
        from redloop.attacker.search import evolve
        agents = [name.strip() for name in args.agents.split(",") if name.strip()]
        if not agents or any(a not in ("naive", "guarded", "llama", "llama-guarded") for a in agents):
            parser.error("--agents must list naive, guarded, llama and/or llama-guarded")
        names = list_scenarios() if args.all else [args.scenario]
        print(f"{'SCENARIO':28} {'CANDS':>5}  " + "  ".join(f"{a + ' ASR':>12}" for a in agents))
        print("-" * 76)
        for name in names:
            try:
                summary = evolve(name, agents, generations=args.generations,
                                 population=args.population, results_path=args.results)
            except (ValueError, OSError) as exc:
                parser.error(str(exc))
            cells = "  ".join(
                f"{'n/a' if summary['asr'][a] is None else format(summary['asr'][a], '.0%'):>12}"
                for a in summary["agents"]
            )
            print(f"{summary['scenario']:28} {summary['candidates']:>5}  {cells}")
        print(f"Results: {args.results}")
        return 0

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
