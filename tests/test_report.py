import json

from redloop.cli import main
from redloop.dashboard_data import markdown_report


def _rows():
    return [
        {"scenario": "email_exfil", "agent": "naive", "status": "red"},
        {"scenario": "email_exfil", "agent": "naive", "status": "green"},
        {"scenario": "email_exfil", "agent": "guarded", "status": "green"},
        {"scenario": "x_policy_override", "agent": "naive", "status": "red"},
        {"scenario": "x_policy_override", "agent": "guarded", "status": "skipped"},
    ]


def test_markdown_report_pivot_and_overall():
    table = markdown_report(_rows())
    assert "| Scenario | guarded ASR | naive ASR |" in table
    assert "| email_exfil | 0% (0/1) | 50% (1/2) |" in table
    assert "| x_policy_override | n/a | 100% (1/1) |" in table
    assert "**0% (0/1)**" in table and "**67% (2/3)**" in table


def test_markdown_report_empty():
    assert markdown_report([]) == "_No results yet._\n"


def test_report_cli_writes_file(tmp_path, capsys):
    results = tmp_path / "r.jsonl"
    results.write_text("\n".join(json.dumps(r) for r in _rows()) + "\nnot json\n")
    out = tmp_path / "asr.md"
    assert main(["report", "--results", str(results), "--out", str(out)]) == 0
    assert "naive ASR" in capsys.readouterr().out
    assert out.read_text().startswith("| Scenario |")


def test_latency_columns_offline_na_tokens():
    from redloop.dashboard_data import latency_report
    rows = [dict(r, seconds=0.002) for r in _rows()]
    rows.append({"scenario": "email_exfil", "agent": "naive", "status": "red"})  # legacy row, no seconds
    table = latency_report(rows)
    assert "| Agent | Runs | Timed | Total | Mean latency | p95 latency | Tokens | USD |" in table
    assert "| naive | 4 | 3 | 6.00 ms | 2.00 ms | 2.00 ms | N/A | N/A |" in table


def test_latency_tokens_usd_when_present():
    from redloop.dashboard_data import latency_report
    table = latency_report([{"scenario": "s", "agent": "m", "status": "green", "seconds": 1.5, "tokens": 100, "usd": 0.01}])
    assert "| m | 1 | 1 | 1.50 s | 1.50 s | 1.50 s | 100 | $0.0100 |" in table


def test_report_cli_includes_latency(tmp_path, capsys):
    results = tmp_path / "r.jsonl"
    results.write_text("\n".join(json.dumps(dict(r, seconds=0.01)) for r in _rows()) + "\n")
    assert main(["report", "--results", str(results)]) == 0
    out = capsys.readouterr().out
    assert "Cost and latency" in out and "Mean latency" in out
    assert main(["report", "--results", str(results), "--no-latency"]) == 0
    assert "Cost and latency" not in capsys.readouterr().out


def test_run_records_seconds(tmp_path):
    from redloop.runner import run_scenario
    row = run_scenario("email_exfil", "guarded", results_path=None)
    assert isinstance(row["seconds"], float) and row["seconds"] >= 0


def test_badge_cli(tmp_path, capsys):
    results = tmp_path / "r.jsonl"
    results.write_text("\n".join(json.dumps(r) for r in _rows()) + "\n")
    out = tmp_path / "b.svg"
    assert main(["badge", "--results", str(results), "--out", str(out)]) == 0
    svg = out.read_text()
    assert svg.startswith("<svg") and "0%" in svg and "#4c1" in svg
    assert "![RedLoop ASR]" in capsys.readouterr().out
    assert main(["badge", "--results", str(results), "--agent", "naive", "--out", str(out)]) == 0
    assert "#e05d44" in out.read_text()
    assert main(["badge", "--results", str(tmp_path / "none.jsonl"), "--out", str(out)]) == 0
    assert "unknown" in out.read_text()
