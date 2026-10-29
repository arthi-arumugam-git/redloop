"""python -m redloop.mcp_target {serve,cases,set-case,score}

    serve     stdio MCP server (point Letta at this)
    cases     write the case file (control + 5 frozen + 10 hand-written)
    set-case  mark which case the next agent turn belongs to
    score     judge calls.jsonl; exit 0 green, 1 red, 3 inconclusive
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from redloop.mcp_target.cases import build_cases, load_cases
from redloop.mcp_target.core import MirrorTarget, load_config
from redloop.mcp_target.score import score_run

DEFAULT_SUITE = Path("results/regression_suite.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m redloop.mcp_target")
    parser.add_argument("--config", default="letta_email", help="Bundled config name or JSON path")
    parser.add_argument("--run-dir", type=Path, required=True,
                        help="Campaign directory; keep it outside the repo for real targets")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("serve", help="Run the stdio MCP server")
    cases = commands.add_parser("cases", help="Write <run-dir>/cases.json")
    cases.add_argument("--suite", type=Path, default=DEFAULT_SUITE)
    set_case = commands.add_parser("set-case", help="Select the case for the next agent turn")
    set_case.add_argument("case_id")
    commands.add_parser("score", help="Judge <run-dir>/calls.jsonl")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    cases_path = args.run_dir / "cases.json"
    if args.command == "cases":
        args.run_dir.mkdir(parents=True, exist_ok=True)
        built = build_cases(config, args.suite)
        cases_path.write_text(json.dumps(built, indent=2) + "\n", encoding="utf-8")
        print("\n".join(built))
        return 0
    if not cases_path.exists():
        print(f"Missing {cases_path}; run the cases command first", file=sys.stderr)
        return 2
    case_map = load_cases(cases_path)
    if args.command == "set-case":
        if args.case_id not in case_map:
            print(f"Unknown case {args.case_id!r}", file=sys.stderr)
            return 2
        (args.run_dir / "current_case").write_text(args.case_id + "\n", encoding="utf-8")
        return 0
    target = MirrorTarget(config, args.run_dir, case_map)
    if args.command == "serve":
        asyncio.run(_serve(target))
        return 0
    summary = score_run(config, list(case_map), target.read_log())
    (args.run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "outcomes"}, indent=2))
    for outcome in summary["outcomes"]:
        print(f"{outcome['status']:>9}  {outcome['case']}  calls={','.join(outcome['calls']) or '-'}")
    return summary["exit_code"]


async def _serve(target: MirrorTarget) -> None:
    from redloop.mcp_target.server import serve_stdio
    await serve_stdio(target)


if __name__ == "__main__":
    raise SystemExit(main())
