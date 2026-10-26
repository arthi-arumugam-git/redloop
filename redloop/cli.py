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
    export = commands.add_parser("export-suite", help="Freeze red payloads into a regression suite JSON")
    export.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    export.add_argument("--out", type=Path, default=Path("results/regression_suite.json"))
    export.add_argument("--max-per-scenario", type=int, default=5)
    check = commands.add_parser("check-suite", help="Replay a regression suite; exit 1 if any case is red")
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
        from redloop.regressions import check_suite, load_suite
        try:
            summary = check_suite(load_suite(args.suite), args.agent)
        except (ValueError, OSError) as exc:
            parser.error(str(exc))
        for o in summary["outcomes"]:
            print(f"{o['status'].upper():7} {o['scenario']:28} {', '.join(o['violations']) or '-'}")
        print(f"{summary['agent']}: {summary['red']}/{summary['total']} cases still succeed")
        return 1 if summary["red"] else 0

    if args.command == "report":
        from redloop.dashboard_data import load_results, markdown_report
        table = markdown_report(load_results(args.results))
        print(table, end="")
        if args.out:
            args.out.write_text(table, encoding="utf-8")
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
