import json

from redloop.cli import main
from redloop.regressions import check_suite, export_suite
from redloop.runner import list_scenarios, load_scenario


def _row(scenario, payload, agent="naive", status="red", score=1):
    return {"scenario": scenario, "payload": payload, "agent": agent, "status": status,
            "score": score, "violations": [{"kind": "exfiltration"}] if status == "red" else []}


def test_export_dedupes_and_skips_green():
    rows = [_row("email_exfil", "p1"), _row("email_exfil", "p1", agent="llama"),
            _row("email_exfil", "p2", status="green", score=0)]
    suite = export_suite(rows)
    assert len(suite["cases"]) == 1
    assert suite["cases"][0]["broke"] == ["llama", "naive"]


def test_export_caps_per_scenario():
    rows = [_row("email_exfil", f"payload-{i}") for i in range(9)]
    assert len(export_suite(rows, max_per_scenario=3)["cases"]) == 3


def test_seed_payloads_break_naive_but_not_guarded():
    cases = [{"scenario": n, "payload": load_scenario(n)["seed_payload"]} for n in list_scenarios()]
    suite = {"version": 1, "cases": cases}
    assert check_suite(suite, "naive")["red"] == len(cases)
    assert check_suite(suite, "guarded")["red"] == 0


def test_cli_roundtrip(tmp_path):
    results = tmp_path / "r.jsonl"
    seed = load_scenario("email_exfil")["seed_payload"]
    results.write_text(json.dumps(_row("email_exfil", seed)) + "\n")
    out = tmp_path / "suite.json"
    assert main(["export-suite", "--results", str(results), "--out", str(out)]) == 0
    assert main(["check-suite", "--suite", str(out), "--agent", "guarded"]) == 0
    assert main(["check-suite", "--suite", str(out), "--agent", "naive"]) == 1
